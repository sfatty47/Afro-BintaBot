import streamlit as st
from chatbot import culturally_aware_chat
from model import get_model, get_tokenizer

# Import knowledge retrieval if available
try:
    from knowledge_retriever import get_african_topic_suggestions
    KNOWLEDGE_RETRIEVAL_AVAILABLE = True
except ImportError:
    KNOWLEDGE_RETRIEVAL_AVAILABLE = False

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
    .status-box {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #ff8c42;
    }
    .knowledge-box {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #00bcd4;
    }
</style>
""", unsafe_allow_html=True)

def check_model_status():
    """Check if model and tokenizer are loaded"""
    try:
        tokenizer = get_tokenizer()
        model = get_model()
        return tokenizer is not None and model is not None
    except:
        return False

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🌍 BintaBot - African Cultural Assistant</h1>
        <p><em>Wisdom from the heart of Africa, enhanced with real-time learning</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Model status indicator
    if not check_model_status():
        st.markdown("""
        <div class="status-box">
            <h4>🔄 Loading BintaBot's Wisdom...</h4>
            <p>BintaBot is loading her knowledge of African culture, history, and wisdom. This may take a moment on first startup.</p>
        </div>
        """, unsafe_allow_html=True)
        st.info("💡 Tip: If loading takes too long, try refreshing the page.")
    
    # Knowledge retrieval status
    if KNOWLEDGE_RETRIEVAL_AVAILABLE:
        st.markdown("""
        <div class="knowledge-box">
            <h4>🔍 Enhanced Learning Active</h4>
            <p>BintaBot can now search and learn from online materials about Africa, including Wikipedia and current sources!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Knowledge retrieval system not available. Using built-in knowledge only.")
    
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
    
    # Enhanced features section
    if KNOWLEDGE_RETRIEVAL_AVAILABLE:
        st.sidebar.markdown("### 🔍 Enhanced Features:")
        st.sidebar.markdown("- **Real-time learning** from online sources")
        st.sidebar.markdown("- **Wikipedia integration** for academic information")
        st.sidebar.markdown("- **Current information** about Africa")
        st.sidebar.markdown("- **Comprehensive knowledge** base")
    
    # Quick commands
    st.sidebar.markdown("### 💡 Quick Commands:")
    st.sidebar.markdown("- 'Tell me a story'")
    st.sidebar.markdown("- 'Share wisdom'")
    st.sidebar.markdown("- 'How is the family?'")
    st.sidebar.markdown("- 'Tell me about Ubuntu'")
    st.sidebar.markdown("- 'What is a griot?'")
    st.sidebar.markdown("- 'Share an African proverb'")
    
    # Advanced learning suggestions
    if KNOWLEDGE_RETRIEVAL_AVAILABLE:
        st.sidebar.markdown("### 🎓 Advanced Learning:")
        st.sidebar.markdown("- 'Tell me about modern African art'")
        st.sidebar.markdown("- 'What are African independence movements?'")
        st.sidebar.markdown("- 'Tell me about African geography'")
        st.sidebar.markdown("- 'What are African traditional religions?'")
    
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
    
    if KNOWLEDGE_RETRIEVAL_AVAILABLE:
        st.sidebar.markdown("""
    - **Real-time Learning**: Current information
    - **Academic Sources**: Wikipedia integration
    - **Comprehensive Knowledge**: Extensive coverage
        """)
    
    # Note about voice features
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📝 Note")
    st.sidebar.markdown("Voice features are available in the local version. This cloud version focuses on text-based cultural exchange with enhanced learning capabilities.")

if __name__ == "__main__":
    main() 