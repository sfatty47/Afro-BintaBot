import streamlit as st
from chatbot import culturally_aware_chat

# Page configuration
st.set_page_config(
    page_title="BintaBot - African Cultural Assistant",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .bot-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .feature-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🌍 BintaBot - African Cultural Assistant</h1>
        <p><em>Wisdom from the heart of Africa</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.header("🌍 About BintaBot")
    st.sidebar.markdown("""
    BintaBot is a culturally-aware African assistant with deep knowledge of:
    
    - Ancient African empires (Mali, Ghana, Songhai)
    - Oral storytelling traditions (Griots)
    - Community philosophies (Ubuntu)
    - African proverbs and folk wisdom
    - Cultural greetings and customs
    """)
    
    # Quick commands
    st.sidebar.markdown("### 💡 Quick Commands:")
    st.sidebar.markdown("- 'Tell me a story'")
    st.sidebar.markdown("- 'Share wisdom'")
    st.sidebar.markdown("- 'How is the family?'")
    st.sidebar.markdown("- 'Tell me about Ubuntu'")
    st.sidebar.markdown("- 'What is a griot?'")
    st.sidebar.markdown("- 'Share an African proverb'")
    
    # Clear chat button
    if st.sidebar.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    # Main chat interface
    st.header("💬 Chat with BintaBot")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask BintaBot about African wisdom, stories, or culture..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get BintaBot response
        with st.chat_message("assistant"):
            with st.spinner("🤔 BintaBot is thinking..."):
                try:
                    response = culturally_aware_chat(prompt)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"I apologize, but I encountered an error while processing your request. Please try again with a different question about African culture, wisdom, or traditions."
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🌟 Features")
    st.sidebar.markdown("""
    - **Cultural Wisdom**: Learn from African traditions
    - **Proverbs**: Discover ancient wisdom
    - **Stories**: Hear African folktales
    - **History**: Explore African empires
    - **Philosophy**: Understand Ubuntu and more
    """)
    
    # Note about voice features
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📝 Note")
    st.sidebar.markdown("Voice features are available in the local version. This cloud version focuses on text-based cultural exchange.")

if __name__ == "__main__":
    main() 