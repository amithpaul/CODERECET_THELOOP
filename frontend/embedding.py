import chromadb
from sentence_transformers import SentenceTransformer
import uuid
import os
import PyPDF2
from typing import List, Dict
from pathlib import Path
import streamlit as st

class EmbeddingService:
    def __init__(self, db_path: str = "data/chroma_db", model_name: str = 'all-MiniLM-L6-v2'):
        """Initialize the embedding service"""
        self.db_path = db_path
        self.model_name = model_name
        self.embeddings_model = None
        self.client = None
        self.collection = None
        
    @st.cache_resource
    def initialize_embeddings_model(_self):
        """Initialize sentence transformer model for embeddings"""
        return SentenceTransformer(_self.model_name)
    
    @st.cache_resource 
    def initialize_vector_store(_self):
        """Initialize ChromaDB vector store"""
        os.makedirs(_self.db_path, exist_ok=True)
        client = chromadb.PersistentClient(path=_self.db_path)
        collection = client.get_or_create_collection(
            name="kerala_knowledge_base",
            metadata={"hnsw:space": "cosine"}
        )
        return client, collection
    
    def setup(self):
        """Setup the embedding service"""
        self.embeddings_model = self.initialize_embeddings_model()
        self.client, self.collection = self.initialize_vector_store()
        return self.embeddings_model is not None and self.collection is not None
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]
            
            # Try to break at sentence boundaries
            if end < len(text):
                last_period = chunk_text.rfind('.')
                last_newline = chunk_text.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > start + chunk_size // 2:
                    chunk_text = text[start:start + break_point + 1]
                    end = start + break_point + 1
            
            chunks.append({
                'text': chunk_text.strip(),
                'id': str(uuid.uuid4()),
                'start_pos': start,
                'end_pos': end
            })
            
            start = end - overlap
        
        return chunks
    
    @st.cache_data
    def load_and_chunk_pdfs(_self, folder_path: str):
        """Load PDFs and create chunks with metadata"""
        all_chunks = []
        
        try:
            pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
            
            for filename in pdf_files:
                filepath = os.path.join(folder_path, filename)
                
                with open(filepath, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    pdf_text = ""
                    
                    for page_num, page in enumerate(pdf_reader.pages):
                        page_text = page.extract_text()
                        if page_text:
                            pdf_text += f"\n[Page {page_num + 1}]\n{page_text}"
                    
                    # Create chunks for this PDF
                    chunks = _self.chunk_text(pdf_text)
                    
                    # Add metadata to each chunk
                    for chunk in chunks:
                        chunk.update({
                            'source_file': filename,
                            'document_type': 'government_scheme',
                            'total_chunks': len(chunks)
                        })
                    
                    all_chunks.extend(chunks)
            
            return all_chunks, len(pdf_files)
            
        except Exception as e:
            st.error(f"Error loading PDFs: {str(e)}")
            return [], 0
    
    def is_data_indexed(self) -> bool:
        """Check if data is already indexed"""
        try:
            return self.collection.count() > 0
        except:
            return False
    
    def index_documents(self, pdf_folder: str = "data/pdfs") -> tuple:
        """Index documents from PDF folder"""
        if not self.embeddings_model or not self.collection:
            return False, "Embedding service not initialized"
        
        # Check if data already exists
        if self.is_data_indexed():
            count = self.collection.count()
            return True, f"Using existing {count} chunks from vector DB"
        
        # Load and chunk PDFs
        chunks, pdf_count = self.load_and_chunk_pdfs(pdf_folder)
        
        if not chunks:
            return False, "No PDFs found to index"
        
        # Create embeddings and store
        with st.spinner("Creating embeddings for knowledge chunks..."):
            texts = [chunk['text'] for chunk in chunks]
            embeddings = self.embeddings_model.encode(texts).tolist()
            
            ids = [chunk['id'] for chunk in chunks]
            metadatas = [{
                'source_file': chunk['source_file'],
                'document_type': chunk['document_type'],
                'start_pos': chunk['start_pos'],
                'end_pos': chunk['end_pos']
            } for chunk in chunks]
            
            # Add to collection in batches
            batch_size = 100
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                batch_embeddings = embeddings[i:i + batch_size]
                batch_ids = ids[i:i + batch_size]
                batch_metadatas = metadatas[i:i + batch_size]
                
                self.collection.add(
                    documents=batch_texts,
                    embeddings=batch_embeddings,
                    ids=batch_ids,
                    metadatas=batch_metadatas
                )
        
        return True, f"Successfully indexed {len(chunks)} chunks from {pdf_count} PDFs"
    
    def retrieve_chunks(self, query: str, top_k: int = 5) -> List[Dict]:
        """Retrieve most relevant chunks for a query"""
        if not self.embeddings_model or not self.collection:
            return []
        
        try:
            # Create query embedding
            query_embedding = self.embeddings_model.encode([query]).tolist()[0]
            
            # Search vector database
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            relevant_chunks = []
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0], 
                results['distances'][0]
            )):
                relevant_chunks.append({
                    'text': doc,
                    'source': metadata['source_file'],
                    'relevance_score': 1 - distance,
                    'rank': i + 1
                })
            
            return relevant_chunks
            
        except Exception as e:
            st.error(f"Retrieval error: {str(e)}")
            return []
    
    def get_stats(self) -> Dict:
        """Get statistics about indexed data"""
        if not self.collection:
            return {"indexed": False}
        
        try:
            count = self.collection.count()
            return {
                "indexed": count > 0,
                "total_chunks": count,
                "model_name": self.model_name,
                "db_path": self.db_path
            }
        except:
            return {"indexed": False}
