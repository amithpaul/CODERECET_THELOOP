import streamlit as st
import google.generativeai as genai
import os
import PyPDF2

# --- Page Configuration (MUST be the first command) ---
st.set_page_config(page_title="The Loop | Kerala", page_icon="🔄", layout="centered")

# --- Direct Initialization and Model Setup (Robust) ---
# This block runs on every script rerun, ensuring state is always present.
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'submissions' not in st.session_state:
    st.session_state.submissions = []

# Configure the API key and create the model.
try:
    # IMPORTANT: Put your key here
    genai.configure(api_key="AIzaSyBVfuwhsmTb7MYRvN0-5Y8bMbAKh8vh9WM")
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("Error setting up the AI model. Please check your API key.")
    # Stop the app if the model fails to initialize.
    st.stop()


# --- Navigation Functions ---
def go_to_page(page_name):
    st.session_state.page = page_name

# --- Main App Router ---

# Display the HOME page
if st.session_state.page == 'home':
    st.title("Welcome to The Loop kerala 🇮🇳")
    # ... (rest of the homepage UI is the same)
    st.markdown("A digital ecosystem designed to bridge the gap between the youth and governance in Kerala.")
    st.markdown("---")
    st.header("Select a Wing to Get Started")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("💡 Information Wing")
        st.write("Ask questions about government schemes.")
        st.button("Go to Information Wing", on_click=go_to_page, args=['info_wing'], use_container_width=True)
    with col2:
        st.subheader("🚀 Innovation Wing")
        st.write("Submit your innovative ideas.")
        st.button("Go to Innovation Wing", on_click=go_to_page, args=['innovation_wing'], use_container_width=True)
    st.markdown("---")
    st.button("View Officials' Dashboard", on_click=go_to_page, args=['dashboard'])


# Display the INFORMATION WING page
elif st.session_state.page == 'info_wing':
    st.title("Information Wing | Ask the AI")
    st.button("← Back to Home", on_click=go_to_page, args=['home'])
    st.markdown("Ask any question about the schemes in our knowledge base.")

    knowledge_base = None # Add knowledge base later

    if not knowledge_base:
        st.warning("Knowledge base is empty. Please add PDF files to the 'knowledge_base' folder in your project directory.")
    else:
        def answer_question(question):
            prompt = f"Context:\n{knowledge_base}\n\nBased ONLY on the context, answer the question: {question}"
            response = model.generate_content(prompt)
            return response.text

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
    st.markdown("Have an idea to improve your community? Share it with us!")

    def analyze_idea(idea_text):
        prompt = f"""
        Analyze... Idea: "{idea_text}"... Format as:
        Summary: [Your one-sentence summary here]
        Tags: [Your #tag1, #tag2, #tag3, #tag4 here]
        Sentiment: [Your Positive/Negative/Neutral label here]
        """
        response = model.generate_content(prompt)
        return response.text

    with st.form("idea_form"):
        idea_title = st.text_input("1. Title of your idea")
        idea_description = st.text_area("2. Detailed description")
        submitted = st.form_submit_button("Analyze & Submit My Idea")
        if submitted:
            if idea_title and idea_description:
                with st.spinner("AI is analyzing..."):
                    analysis_result = analyze_idea(idea_description)
                    st.session_state.submissions.append({
                        "title": idea_title,
                        "description": idea_description,
                        "analysis": analysis_result
                    })
                    st.success("Your idea has been submitted!")
                    st.markdown(analysis_result)
                    st.balloons()
            else:
                st.warning("Please fill out the title and description.")

# Display the OFFICIALS' DASHBOARD page
elif st.session_state.page == 'dashboard':
    st.title("Officials' Dashboard | Submitted Ideas 📋")
    st.button("← Back to Home", on_click=go_to_page, args=['home'])
    
    if st.session_state.submissions:
        for i, submission in enumerate(st.session_state.submissions):
            with st.container(border=True):
                st.header(f"Idea #{i+1}: {submission['title']}")
                st.info(submission['analysis'])
                with st.expander("Show Full Description"):
                    st.write(submission['description'])
    else:
        st.warning("No ideas have been submitted yet.")