import streamlit as st
import google.generativeai as genai
import os
import PyPDF2
from pathlib import Path
import json
from web3 import Web3
import traceback
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import random

# --- Page Configuration (MUST be the first command) ---
st.set_page_config(page_title="The Loop | Kerala", page_icon="🔄", layout="wide")

# --- Session State Initialization ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'submissions' not in st.session_state:
    st.session_state.submissions = []
if 'votes' not in st.session_state:
    st.session_state.votes = {}
if 'suggestions' not in st.session_state:
    st.session_state.suggestions = None
if 'user_wallet' not in st.session_state:
    st.session_state.user_wallet = None
if 'blockchain_connected' not in st.session_state:
    st.session_state.blockchain_connected = False
if 'kerala_map_data' not in st.session_state:
    st.session_state.kerala_map_data = None
if 'map_needs_update' not in st.session_state:
    st.session_state.map_needs_update = True
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

# --- Kerala Districts Data for Heatmap ---
KERALA_DISTRICTS = {
    "Thiruvananthapuram": {"lat": 8.5241, "lon": 76.9366, "ideas": 0},
    "Kollam": {"lat": 8.8932, "lon": 76.6141, "ideas": 0},
    "Pathanamthitta": {"lat": 9.2648, "lon": 76.7870, "ideas": 0},
    "Alappuzha": {"lat": 9.4981, "lon": 76.3388, "ideas": 0},
    "Kottayam": {"lat": 9.5916, "lon": 76.5222, "ideas": 0},
    "Idukki": {"lat": 9.8560, "lon": 76.9740, "ideas": 0},
    "Ernakulam": {"lat": 9.9312, "lon": 76.2673, "ideas": 0},
    "Thrissur": {"lat": 10.5276, "lon": 76.2144, "ideas": 0},
    "Palakkad": {"lat": 10.7867, "lon": 76.6548, "ideas": 0},
    "Malappuram": {"lat": 11.0746, "lon": 76.0740, "ideas": 0},
    "Kozhikode": {"lat": 11.2588, "lon": 75.7804, "ideas": 0},
    "Wayanad": {"lat": 11.6854, "lon": 76.1320, "ideas": 0},
    "Kannur": {"lat": 11.8745, "lon": 75.3704, "ideas": 0},
    "Kasaragod": {"lat": 12.4996, "lon": 74.9869, "ideas": 0}
}

# --- JSON Data Management Functions ---
def save_submissions_to_json():
    """Save all submissions to a JSON file"""
    try:
        data_dir = Path(__file__).parent / "data"
        data_dir.mkdir(exist_ok=True)
        
        submissions_data = {
            "submissions": st.session_state.submissions,
            "votes": st.session_state.votes,
            "last_updated": datetime.now().isoformat(),
            "total_submissions": len(st.session_state.submissions),
            "total_votes": sum(st.session_state.votes.values())
        }
        
        json_path = data_dir / "submissions_data.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(submissions_data, f, indent=2, ensure_ascii=False)
        
        return True, str(json_path)
    except Exception as e:
        return False, str(e)

def load_submissions_from_json():
    """Load submissions from JSON file if it exists"""
    try:
        json_path = Path(__file__).parent / "data" / "submissions_data.json"
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            st.session_state.submissions = data.get("submissions", [])
            st.session_state.votes = data.get("votes", {})
            return True, f"Loaded {len(st.session_state.submissions)} submissions"
        return False, "No saved data found"
    except Exception as e:
        return False, str(e)

# Load existing data on startup
if not st.session_state.data_loaded:
    success, message = load_submissions_from_json()
    st.session_state.data_loaded = True
    if success:
        st.sidebar.success(f"📁 {message}")

# --- Map Functions (Fixed Version) ---
def get_district_data():
    """Get current district data with idea counts"""
    district_data = {}
    
    for district in KERALA_DISTRICTS:
        district_data[district] = {
            "lat": KERALA_DISTRICTS[district]["lat"],
            "lon": KERALA_DISTRICTS[district]["lon"],
            "ideas": 0
        }
    
    for submission in st.session_state.submissions:
        district = submission.get('district', 'Thiruvananthapuram')
        if district in district_data:
            district_data[district]["ideas"] += 1
    
    return district_data

def create_kerala_heatmap():
    """Create a stable map that doesn't refresh constantly"""
    district_data = get_district_data()
    
    m = folium.Map(
        location=[10.8505, 76.2711],
        zoom_start=7,
        tiles='OpenStreetMap'
    )
    
    for district, data in district_data.items():
        if data["ideas"] == 0:
            color = 'gray'
            radius = 8
        elif data["ideas"] <= 3:
            color = 'green'
            radius = 12
        elif data["ideas"] <= 7:
            color = 'orange'
            radius = 16
        else:
            color = 'red'
            radius = 20
        
        folium.CircleMarker(
            location=[data["lat"], data["lon"]],
            radius=radius,
            popup=f"<b>{district}</b><br>Ideas Submitted: {data['ideas']}",
            tooltip=f"{district}: {data['ideas']} ideas",
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            weight=2
        ).add_to(m)
    
    return m

def update_map_trigger():
    """Trigger map update only when necessary"""
    st.session_state.map_needs_update = True

# --- Leaderboard Functions ---
def create_leaderboard():
    """Create leaderboard data from submissions"""
    if not st.session_state.submissions:
        return []
    
    leaderboard = []
    for submission in st.session_state.submissions:
        votes = st.session_state.votes.get(submission['title'], 0)
        rewards = sum(r.get('amount', 0) for r in submission.get('rewards', []))
        
        leaderboard.append({
            'title': submission['title'],
            'submitter': submission.get('submitter', 'Unknown')[:10] + '...' if len(submission.get('submitter', '')) > 10 else submission.get('submitter', 'Unknown'),
            'votes': votes,
            'rewards': rewards,
            'nft_minted': submission.get('nft_minted', False),
            'timestamp': submission.get('timestamp', 'Unknown'),
            'district': submission.get('district', 'Unknown')
        })
    
    leaderboard.sort(key=lambda x: (x['votes'], x['rewards']), reverse=True)
    return leaderboard

# --- Centralized Setup for AI and Blockchain ---
@st.cache_resource
def initialize_ai_model():
    """Initialize AI model separately"""
    try:
        api_key = "AIzaSyBxCfnv1M6dg6NZXZIljFXom1ghLKYIl6c"  # Replace with your actual API key
        if api_key == "YOUR_API_KEY_HERE":
            st.error("⚠️ Please set your Google Gemini API key in the code!")
            return None
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model
    except Exception as e:
        st.error(f"Error setting up AI model: {e}")
        return None

def initialize_blockchain():
    """Initialize blockchain connection with better error handling"""
    try:
        ganache_urls = [
            "http://127.0.0.1:7545",
            "http://127.0.0.1:8545",
            "http://localhost:7545",
            "http://localhost:8545",
            "HTTP://127.0.0.1:7547"
        ]
        
        w3 = None
        for url in ganache_urls:
            try:
                test_w3 = Web3(Web3.HTTPProvider(url))
                if test_w3.is_connected():
                    w3 = test_w3
                    st.sidebar.success(f"✅ Connected to blockchain at {url}")
                    break
            except:
                continue
        
        if not w3:
            st.sidebar.error("❌ Cannot connect to Ganache. Please ensure Ganache is running on one of these ports: 7545, 8545")
            return None, None, None, None
        
        accounts = w3.eth.accounts
        if not accounts:
            st.sidebar.error("❌ No accounts found. Please check your Ganache setup.")
            return w3, None, None, None
        
        st.sidebar.success(f"✅ Found {len(accounts)} accounts")
        
        idea_nft_contract = None
        loop_token_contract = None
        
        try:
            idea_nft_address = "0x5287db2bE7E0Fc9916BF5100F78D50b87e1240E6"
            idea_nft_abi_path = Path(__file__).parent / 'hardhat_project' / 'artifacts' / 'contracts' / 'IdeaNFT.sol' / 'IdeaNFT.json'
            
            if idea_nft_abi_path.exists():
                with open(idea_nft_abi_path, 'r') as f:
                    idea_nft_abi = json.load(f)['abi']
                idea_nft_contract = w3.eth.contract(address=idea_nft_address, abi=idea_nft_abi)
                st.sidebar.success("✅ IdeaNFT contract loaded")
            else:
                st.sidebar.warning("⚠️ IdeaNFT contract ABI file not found")
        except Exception as e:
            st.sidebar.error(f"❌ Error loading IdeaNFT contract: {str(e)}")
        
        try:
            loop_token_address = "0x82aa126e5c34b855767924BCe6741C95C87245dA"
            loop_token_abi_path = Path(__file__).parent / 'hardhat_project' / 'artifacts' / 'contracts' / 'LoopToken.sol' / 'LoopToken.json'
            
            if loop_token_abi_path.exists():
                with open(loop_token_abi_path, 'r') as f:
                    loop_token_abi = json.load(f)['abi']
                loop_token_contract = w3.eth.contract(address=loop_token_address, abi=loop_token_abi)
                st.sidebar.success("✅ LoopToken contract loaded")
            else:
                st.sidebar.warning("⚠️ LoopToken contract ABI file not found")
        except Exception as e:
            st.sidebar.error(f"❌ Error loading LoopToken contract: {str(e)}")
        
        return w3, accounts, idea_nft_contract, loop_token_contract
        
    except Exception as e:
        st.sidebar.error(f"❌ Blockchain connection failed: {str(e)}")
        st.sidebar.error("Please ensure Ganache is running and try refreshing the page.")
        return None, None, None, None

# Initialize connections
if 'initialized' not in st.session_state:
    st.session_state.model = initialize_ai_model()
    st.session_state.w3, st.session_state.accounts, st.session_state.idea_nft, st.session_state.loop_token = initialize_blockchain()
    st.session_state.initialized = True
    
    st.session_state.blockchain_connected = st.session_state.w3 is not None and st.session_state.accounts is not None
    
    if st.session_state.blockchain_connected and st.session_state.accounts:
        st.session_state.user_wallet = st.session_state.accounts[0]

# --- Sidebar Status ---
st.sidebar.title("🔗 Connection Status")

if st.session_state.model:
    st.sidebar.success("🤖 AI Model: Connected")
else:
    st.sidebar.error("🤖 AI Model: Not Connected")

if st.session_state.blockchain_connected:
    st.sidebar.success("⛓️ Blockchain: Connected")
    if st.session_state.accounts:
        st.sidebar.success(f"👛 Wallets: {len(st.session_state.accounts)} found")
        
        if len(st.session_state.accounts) > 1:
            selected_wallet = st.sidebar.selectbox(
                "Select Your Wallet:",
                st.session_state.accounts,
                format_func=lambda x: f"{x[:6]}...{x[-4:]}",
                index=st.session_state.accounts.index(st.session_state.user_wallet) if st.session_state.user_wallet in st.session_state.accounts else 0
            )
            st.session_state.user_wallet = selected_wallet
        
        if st.session_state.user_wallet:
            st.sidebar.info(f"Current Wallet:\n{st.session_state.user_wallet[:6]}...{st.session_state.user_wallet[-4:]}")
            
            try:
                balance = st.session_state.w3.eth.get_balance(st.session_state.user_wallet)
                balance_eth = st.session_state.w3.from_wei(balance, 'ether')
                st.sidebar.info(f"Balance: {balance_eth:.2f} ETH")
            except Exception as e:
                st.sidebar.warning("Could not fetch balance")
else:
    st.sidebar.error("⛓️ Blockchain: Not Connected")
    st.sidebar.warning("NFT minting and token rewards will not work")

if st.sidebar.button("🔄 Refresh Connections"):
    st.cache_resource.clear()
    for key in ['initialized', 'model', 'w3', 'accounts', 'idea_nft', 'loop_token']:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# # --- PDF Loading Function ---
@st.cache_data
def load_knowledge_base_from_pdfs(folder_path):
    text = ""
    try:
        pdf_files = []
        for filename in os.listdir(folder_path):
            if filename.endswith('.pdf'):
                pdf_files.append(filename)
                filepath = os.path.join(folder_path, filename)
                with open(filepath, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text
        
        if pdf_files:
            st.sidebar.success(f"📚 Knowledge Base: {len(pdf_files)} PDFs loaded")
        else:
            st.sidebar.warning("📚 Knowledge Base: No PDFs found")
                            
    except FileNotFoundError:
        st.sidebar.warning("📚 Knowledge Base: Folder not found")
    except Exception as e:
        st.sidebar.error(f"📚 Knowledge Base: Error loading - {str(e)}")
    
    return text

# --- Navigation Functions ---
def go_to_page(page_name):
    st.session_state.page = page_name

# --- Main App Router ---

# Display the HOME page
if st.session_state.page == 'home':
    st.title("Welcome to The Loop Kerala 🇮🇳")
    st.markdown("A digital ecosystem designed to bridge the gap between the youth and governance in Kerala.")
    st.markdown("---")
    
    if not st.session_state.model:
        st.warning("⚠️ AI model not connected. Information Wing may not work properly.")
    
    if not st.session_state.blockchain_connected:
        st.warning("⚠️ Blockchain not connected. Innovation Wing NFT minting and token rewards will not work.")
    
    # Statistics Overview
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💡 Ideas Submitted", len(st.session_state.submissions))
    with col2:
        st.metric("👍 Total Votes", sum(st.session_state.votes.values()))
    with col3:
        nft_count = len([s for s in st.session_state.submissions if s.get('nft_minted', False)])
        st.metric("🎨 NFTs Minted", nft_count)
    with col4:
        district_data = get_district_data()
        active_districts = len([d for d in district_data if district_data[d]["ideas"] > 0])
        st.metric("📍 Active Districts", active_districts)
    
    st.markdown("---")
    
    # Kerala Heatmap Section
    st.header("📍 Innovation Heatmap - Kerala Districts")
    st.markdown("See where the most innovative ideas are coming from across Kerala!")
    
    if st.session_state.kerala_map_data is None or st.session_state.map_needs_update:
        with st.spinner("Loading Kerala Innovation Map..."):
            st.session_state.kerala_map_data = create_kerala_heatmap()
            st.session_state.map_needs_update = False
    
    col1, col2 = st.columns([2, 1])
    with col1:
        map_data = st_folium(
            st.session_state.kerala_map_data, 
            width=700, 
            height=400,
            key="kerala_heatmap_stable"
        )
    
    with col2:
        st.subheader("🏆 Top Districts")
        district_data = get_district_data()
        sorted_districts = sorted(
            district_data.items(), 
            key=lambda x: x[1]["ideas"], 
            reverse=True
        )[:5]
        
        for i, (district, data) in enumerate(sorted_districts):
            if data["ideas"] > 0:
                emoji = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "💡"
                st.info(f"{emoji} **{district}**: {data['ideas']} ideas")
        
        if not any(data["ideas"] > 0 for _, data in sorted_districts):
            st.info("🎯 No ideas submitted yet. Be the first to contribute!")
        
        if st.button("🔄 Refresh Map", key="refresh_map_btn"):
            st.session_state.map_needs_update = True
            st.rerun()
    
    st.markdown("---")
    
    # Navigation Section
    st.header("Select a Wing to Get Started")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💡 Information Wing")
        st.write("Ask questions about government schemes.")
        info_disabled = not st.session_state.model
        st.button(
            "Go to Information Wing", 
            on_click=go_to_page, 
            args=['info_wing'], 
            use_container_width=True,
            disabled=info_disabled,
            help="Requires AI model connection" if info_disabled else None
        )
    
    with col2:
        st.subheader("🚀 Innovation Wing")
        st.write("Submit your innovative ideas.")
        st.button(
            "Go to Innovation Wing", 
            on_click=go_to_page, 
            args=['innovation_wing'], 
            use_container_width=True
        )
    
    st.markdown("---")
    st.button("View Officials' Dashboard", on_click=go_to_page, args=['dashboard'])

# Display the INFORMATION WING page
elif st.session_state.page == 'info_wing':
    st.title("Information Wing | Ask the AI")
    st.button("← Back to Home", on_click=go_to_page, args=['home'])
    
    if not st.session_state.model:
        st.error("❌ AI model is not connected. Please check your API key and refresh connections.")
        st.stop()
    
    st.markdown("Ask any question about the schemes in our knowledge base.")

    script_directory = Path(__file__).parent
    knowledge_base_folder = "frontend\data"
    knowledge_base = load_knowledge_base_from_pdfs(knowledge_base_folder)

    if not knowledge_base:
        st.warning(f"Knowledge base is empty. Please create a folder named 'knowledge_base' and add your PDFs.")
    else:
        def answer_question(question):
            try:
                prompt = f"Context:\n{knowledge_base}\n\nBased ONLY on the context, answer the question: {question}"
                response = st.session_state.model.generate_content(prompt)
                return response.text
            except Exception as e:
                return f"Error generating response: {str(e)}"

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if user_question := st.chat_input("What is your question?"):
            st.session_state.messages.append({"role": "user", "content": user_question})
            with st.chat_message("user"):
                st.markdown(user_question)
            
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    ai_answer = answer_question(user_question)
                    st.write(ai_answer)
            
            st.session_state.messages.append({"role": "assistant", "content": ai_answer})

# Display the INNOVATION WING page
elif st.session_state.page == 'innovation_wing':
    st.title("Innovation Wing | Submit Your Idea 💡")
    st.button("← Back to Home", on_click=go_to_page, args=['home'])
    
    # Leaderboard Section
    st.header("🏆 Innovation Leaderboard")
    leaderboard = create_leaderboard()
    
    if leaderboard:
        tab1, tab2 = st.tabs(["🏆 Top Ideas", "📊 Analytics"])
        
        with tab1:
            for i, entry in enumerate(leaderboard[:10]):
                rank_emoji = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}️⃣"
                
                col1, col2, col3, col4, col5, col6 = st.columns([1, 3, 1, 1, 1, 1])
                with col1:
                    st.markdown(f"**{rank_emoji}**")
                with col2:
                    title_display = entry['title'][:30] + "..." if len(entry['title']) > 30 else entry['title']
                    st.markdown(f"**{title_display}**")
                with col3:
                    st.markdown(f"👍 {entry['votes']}")
                with col4:
                    st.markdown(f"💰 {entry['rewards']}")
                with col5:
                    nft_status = "✅" if entry['nft_minted'] else "❌"
                    st.markdown(f"🎨 {nft_status}")
                with col6:
                    st.markdown(f"📍 {entry['district'][:8]}")
        
        with tab2:
            if len(leaderboard) > 0:
                votes_data = [entry['votes'] for entry in leaderboard]
                fig_votes = px.histogram(
                    x=votes_data, 
                    title="Distribution of Votes",
                    labels={'x': 'Number of Votes', 'y': 'Number of Ideas'}
                )
                st.plotly_chart(fig_votes, use_container_width=True)
                
                district_counts = {}
                for entry in leaderboard:
                    district = entry['district']
                    district_counts[district] = district_counts.get(district, 0) + 1
                
                if len(district_counts) > 1:
                    fig_districts = px.pie(
                        values=list(district_counts.values()),
                        names=list(district_counts.keys()),
                        title="Ideas by District"
                    )
                    st.plotly_chart(fig_districts, use_container_width=True)
    else:
        st.info("🎯 No submissions yet. Be the first to submit an idea and top the leaderboard!")
    
    st.markdown("---")
    
    # Enhanced header with NFT information
    st.markdown("""
    **Have an idea to improve your community? Share it with us!**
    
    🎁 **Special Reward:** Every submitted idea gets you a unique **Idea NFT** as proof of your contribution to Kerala's development!
    """)

    if not st.session_state.blockchain_connected:
        st.error("❌ **NFT Minting Unavailable** - Blockchain not connected")
        st.warning("💡 Ideas will be saved locally, but you won't receive your NFT reward until blockchain is connected.")
        
        st.info("""
        **What you're missing:**
        - 🎨 Unique NFT for your idea submission
        - 🏆 Blockchain proof of your contribution
        - 💰 Potential token rewards from officials
        """)
    else:
        st.success("✅ **NFT Minting Ready!** - You'll receive a unique NFT for each idea submitted")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🎨 Your NFTs", "Coming Soon", help="Track your collected NFTs")
        with col2:
            user_submissions = len([s for s in st.session_state.submissions if s.get('submitter') == st.session_state.user_wallet])
            st.metric("🌟 Ideas Submitted", user_submissions, help="Your total contributions")
        with col3:
            wallet_display = f"{st.session_state.user_wallet[:6]}...{st.session_state.user_wallet[-4:]}" if st.session_state.user_wallet else "None"
            st.metric("👛 Selected Wallet", wallet_display)

    st.markdown("---")

    with st.form("idea_form"):
        st.subheader("💭 Share Your Innovation")
        
        col1, col2 = st.columns(2)
        with col1:
            idea_title = st.text_input(
                "🏷️ **Idea Title**", 
                placeholder="Give your idea a catchy title...",
                help="A brief, descriptive title for your idea"
            )
        
        with col2:
            selected_district = st.selectbox(
                "📍 **Your District**",
                list(KERALA_DISTRICTS.keys()),
                help="Select your district to help with regional analysis"
            )
        
        idea_description = st.text_area(
            "📝 **Detailed Description**", 
            placeholder="Describe your idea in detail. What problem does it solve? How would it work? Who would benefit?",
            height=150,
            help="The more detailed your description, the better the AI analysis will be"
        )
        
        submit_button_text = "🚀 Submit Idea & Mint NFT" if st.session_state.blockchain_connected else "📝 Submit Idea (No NFT)"
        submitted = st.form_submit_button(
            submit_button_text, 
            type="primary",
            use_container_width=True
        )

        if submitted:
            if idea_title and idea_description:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("🤖 AI is analyzing your idea...")
                progress_bar.progress(25)
                
                analysis_result = "Analysis not available (AI model not connected)"
                if st.session_state.model:
                    try:
                        def analyze_idea(idea_text):
                            prompt = f"""
                            Analyze the following innovative idea for Kerala's development. Perform these tasks:
                            
                            1. **Summary**: Write a clear, compelling one-sentence summary of the core proposal
                            2. **Impact Tags**: Suggest exactly 4 relevant hashtags that categorize the idea's impact areas (e.g., #Education, #Healthcare, #Technology, #Environment)
                            3. **Sentiment**: Classify the overall sentiment as Positive, Negative, or Neutral
                            4. **Innovation Score**: Rate the innovation level from 1-10 based on uniqueness and feasibility
                            
                            Idea Title: "{idea_title}"
                            Idea Description: "{idea_text}"

                            Format your response exactly like this:
                            Summary: [Your compelling summary here]
                            Tags: [#tag1, #tag2, #tag3, #tag4]
                            Sentiment: [Positive/Negative/Neutral]
                            Innovation Score: [1-10]/10
                            """
                            response = st.session_state.model.generate_content(prompt)
                            return response.text
                        
                        analysis_result = analyze_idea(idea_description)
                    except Exception as e:
                        analysis_result = f"Analysis error: {str(e)}"
                
                status_text.text("💾 Saving your idea...")
                progress_bar.progress(50)
                
                submission_data = {
                    "title": idea_title,
                    "description": idea_description,
                    "district": selected_district,
                    "analysis": analysis_result,
                    "submitter": st.session_state.user_wallet or "No wallet connected",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                st.session_state.submissions.append(submission_data)

                nft_success = False
                nft_token_id = None
                tx_hash = None
                
                if st.session_state.blockchain_connected and st.session_state.idea_nft and st.session_state.user_wallet:
                    status_text.text("🎨 Minting your unique NFT...")
                    progress_bar.progress(75)
                    
                    try:
                        try:
                            total_supply = st.session_state.idea_nft.functions.totalSupply().call()
                            nft_token_id = total_supply + 1
                        except:
                            nft_token_id = "Unknown"
                        
                        tx_hash = st.session_state.idea_nft.functions.mintIdea(
                            st.session_state.user_wallet
                        ).transact({'from': st.session_state.accounts[0]})
                        
                        receipt = st.session_state.w3.eth.wait_for_transaction_receipt(tx_hash)
                        nft_success = True
                        
                        submission_data["nft_minted"] = True
                        submission_data["nft_token_id"] = nft_token_id
                        submission_data["tx_hash"] = tx_hash.hex()

                    except Exception as e:
                        st.error(f"❌ NFT Minting Failed: {str(e)}")
                        submission_data["nft_minted"] = False
                        submission_data["nft_error"] = str(e)
                
                status_text.text("💾 Saving to permanent storage...")
                progress_bar.progress(90)
                save_success, save_message = save_submissions_to_json()
                
                update_map_trigger()
                
                status_text.text("✅ Process completed!")
                progress_bar.progress(100)
                
                progress_bar.empty()
                status_text.empty()
                
                if save_success:
                    st.success(f"💾 **Data saved successfully!**")
                else:
                    st.warning(f"⚠️ **Data save failed:** {save_message}")
                
                if nft_success:
                    st.success("🎉 **Congratulations! Your idea has been submitted successfully!**")
                    
                    with st.container(border=True):
                        st.markdown("### 🎨 Your NFT Reward")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.info(f"**Token ID:** #{nft_token_id}")
                            st.info(f"**Owner:** {st.session_state.user_wallet[:6]}...{st.session_state.user_wallet[-4:]}")
                        with col2:
                            st.success("**Status:** ✅ Minted Successfully")
                            if tx_hash:
                                st.caption(f"Transaction: `{tx_hash.hex()[:20]}...`")
                    
                    st.balloons()
                    
                else:
                    if st.session_state.blockchain_connected:
                        st.warning("⚠️ **Idea submitted, but NFT minting failed.**")
                        st.info("💡 Your idea is saved and officials can still see it. The NFT might be minted later when the issue is resolved.")
                    else:
                        st.success("✅ **Your idea has been submitted successfully!**")
                        st.info("🎨 **NFT Pending:** Connect to blockchain to receive your NFT reward!")

                st.markdown("---")
                st.markdown("### 🤖 AI Analysis Results")
                with st.container(border=True):
                    st.markdown(analysis_result)
                
                st.markdown("---")
                st.success("🚀 **Ready for another idea?** Clear the form above and share your next innovation!")
                    
            else:
                st.warning("⚠️ Please fill out both the title and description to submit your idea.")
                st.info("💡 **Tip:** The more detailed your description, the better your NFT and potential rewards!")

# Display the OFFICIALS' DASHBOARD page
elif st.session_state.page == 'dashboard':
    st.title("Officials' Dashboard | Submitted Ideas 📋")
    st.button("← Back to Home", on_click=go_to_page, args=['home'])
    
    # JSON management buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💾 Save Data to JSON", use_container_width=True):
            success, message = save_submissions_to_json()
            if success:
                st.success(f"✅ Data saved successfully!")
            else:
                st.error(f"❌ Save failed: {message}")
    
    with col2:
        if st.button("📁 Load Data from JSON", use_container_width=True):
            success, message = load_submissions_from_json()
            if success:
                st.success(f"✅ {message}")
                update_map_trigger()
                st.rerun()
            else:
                st.error(f"❌ Load failed: {message}")
    
    with col3:
        if st.session_state.submissions:
            json_data = {
                "submissions": st.session_state.submissions,
                "votes": st.session_state.votes,
                "export_timestamp": datetime.now().isoformat()
            }
            json_string = json.dumps(json_data, indent=2, ensure_ascii=False)
            st.download_button(
                label="📥 Download JSON",
                data=json_string,
                file_name=f"kerala_ideas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
    
    if st.session_state.submissions:
        total_submissions = len(st.session_state.submissions)
        nft_minted_count = len([s for s in st.session_state.submissions if s.get('nft_minted', False)])
        total_votes = sum(st.session_state.votes.values())
        districts_with_ideas = len(set(s.get('district', 'Unknown') for s in st.session_state.submissions))
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Total Ideas", total_submissions)
        with col2:
            st.metric("🎨 NFTs Minted", nft_minted_count)
        with col3:
            st.metric("👍 Total Votes", total_votes)
        with col4:
            st.metric("📍 Districts", districts_with_ideas)
        
        st.markdown("---")
        
        sorted_submissions = sorted(
            st.session_state.submissions,
            key=lambda x: st.session_state.votes.get(x['title'], 0),
            reverse=True
        )

        for i, submission in enumerate(sorted_submissions):
            # FIXED: Create unique identifier for each submission
            submission_id = f"{submission['title']}_{i}_{submission.get('timestamp', 'unknown')}"
            
            if submission['title'] not in st.session_state.votes:
                st.session_state.votes[submission['title']] = 0
            
            with st.container(border=True):
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col1:
                    rank_emoji = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "💡"
                    st.header(f"{rank_emoji} {submission['title']}")
                with col2:
                    st.metric("Votes 👍", st.session_state.votes[submission['title']])
                with col3:
                    if submission.get('nft_minted', False):
                        st.success("🎨 NFT ✅")
                        if submission.get('nft_token_id'):
                            st.caption(f"Token #{submission['nft_token_id']}")
                    else:
                        st.error("❌ No NFT")
                with col4:
                    district = submission.get('district', 'Unknown')
                    st.info(f"📍 {district}")
                
                st.info(submission['analysis'])
                
                submitter_address = submission.get('submitter', 'No wallet connected')
                timestamp = submission.get('timestamp', 'Unknown time')
                
                col1, col2 = st.columns(2)
                with col1:
                    display_address = submitter_address if len(submitter_address) <= 20 else f"{submitter_address[:10]}...{submitter_address[-10:]}"
                    st.write(f"**👤 Submitter:** `{display_address}`")
                with col2:
                    st.write(f"**📅 Submitted:** {timestamp}")

                # FIXED: Remove key parameter from expanders
                if submission.get('nft_minted', False):
                    with st.expander(f"🎨 NFT Details — {submission_id[:20]}"):
                        nft_col1, nft_col2 = st.columns(2)
                        with nft_col1:
                            st.write(f"**Token ID:** #{submission.get('nft_token_id', 'Unknown')}")
                            display_owner = submitter_address[:6] + "..." + submitter_address[-4:] if len(submitter_address) > 10 else submitter_address
                            st.write(f"**Owner:** {display_owner}")
                        with nft_col2:
                            st.write("**Status:** ✅ Successfully Minted")
                            if submission.get('tx_hash'):
                                st.caption(f"Tx: {submission['tx_hash'][:20]}...")

                with st.expander(f"📖 Full Description — {submission_id[:20]}"):
                    st.write(submission['description'])

                # FIXED: Using unique keys for all buttons
                col1, col2 = st.columns([1, 3])
                with col1:
                    if st.button("👍 Upvote", key=f"upvote_{submission_id}", use_container_width=True):
                        st.session_state.votes[submission['title']] += 1
                        save_submissions_to_json()
                        st.rerun()
                with col2:
                    vote_col1, vote_col2, vote_col3 = st.columns(3)
                    with vote_col1:
                        if st.button("+5 votes", key=f"vote5_{submission_id}"):
                            st.session_state.votes[submission['title']] += 5
                            save_submissions_to_json()
                            st.rerun()
                    with vote_col2:
                        if st.button("+10 votes", key=f"vote10_{submission_id}"):
                            st.session_state.votes[submission['title']] += 10
                            save_submissions_to_json()
                            st.rerun()
                    with vote_col3:
                        if st.button("🌟 Feature", key=f"feature_{submission_id}"):
                            st.session_state.votes[submission['title']] += 25
                            save_submissions_to_json()
                            st.success("⭐ Featured idea!")
                            st.rerun()

                st.subheader("🏆 Reward Outstanding Contribution")
                
                if st.session_state.blockchain_connected and st.session_state.loop_token and submitter_address != 'No wallet connected':
                    reward_col1, reward_col2 = st.columns([2, 1])
                    
                    with reward_col1:
                        reward_amount = st.number_input(
                            "LOOP Tokens to Award:", 
                            min_value=1, 
                            max_value=1000,
                            value=100, 
                            step=50,
                            key=f"reward_{submission_id}",
                            help="Reward exceptional ideas with LOOP tokens"
                        )
                        
                        preset_col1, preset_col2, preset_col3 = st.columns(3)
                        with preset_col1:
                            if st.button("💡 Good (50)", key=f"good_{submission_id}"):
                                reward_amount = 50
                        with preset_col2:
                            if st.button("⭐ Great (100)", key=f"great_{submission_id}"):
                                reward_amount = 100
                        with preset_col3:
                            if st.button("🏆 Excellent (250)", key=f"excellent_{submission_id}"):
                                reward_amount = 250
                    
                    with reward_col2:
                        if st.button("💰 Award Tokens", key=f"award_{submission_id}", type="primary", use_container_width=True):
                            with st.spinner("Processing reward..."):
                                try:
                                    amount_in_wei = reward_amount * (10**18)
                                    tx_hash = st.session_state.loop_token.functions.mint(
                                        submitter_address, amount_in_wei
                                    ).transact({'from': st.session_state.accounts[0]})
                                    st.session_state.w3.eth.wait_for_transaction_receipt(tx_hash)
                                    
                                    st.success(f"🎉 Successfully awarded {reward_amount} LOOP tokens!")
                                    st.balloons()
                                    
                                    submission['rewards'] = submission.get('rewards', [])
                                    submission['rewards'].append({
                                        'amount': reward_amount,
                                        'tx_hash': tx_hash.hex(),
                                        'timestamp': datetime.now().isoformat()
                                    })
                                    
                                    save_submissions_to_json()
                                    
                                except Exception as e:
                                    st.error(f"❌ Reward transaction failed: {str(e)}")
                else:
                    st.warning("⚠️ **Token rewards unavailable**")
                    st.caption("Requires blockchain connection and valid wallet address")
                
                if submission.get('rewards'):
                    with st.expander(f"💰 Previous Rewards ({len(submission['rewards'])}) — {submission_id[:20]}"):
                        total_rewarded = sum(r['amount'] for r in submission['rewards'])
                        st.success(f"Total LOOP tokens awarded: **{total_rewarded}**")
                        for reward in submission['rewards']:
                            reward_time = reward.get('timestamp', 'Unknown time')
                            if 'T' in reward_time:
                                try:
                                    reward_time = datetime.fromisoformat(reward_time.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')
                                except:
                                    pass
                            st.caption(f"• {reward['amount']} LOOP - {reward_time}")
                
                st.markdown("---")
    else:
        st.warning("📭 No ideas have been submitted yet.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            ### 🚀 Encourage Participation
            - Share the Innovation Wing with citizens
            - Promote the NFT rewards system
            - Highlight successful implementations
            """)
        with col2:
            st.markdown("""
            ### 💡 What You'll See Here
            - 📊 Submitted innovative ideas
            - 🎨 NFT minting status
            - 👍 Community voting results
            - 🏆 Token reward distribution
            """)
        
        st.info("**Next Steps:** Visit the Innovation Wing to submit the first idea and test the NFT minting system!")
