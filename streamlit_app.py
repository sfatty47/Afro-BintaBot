import streamlit as st
from chatbot import culturally_aware_chat, create_cultural_widgets, initialize_chat_session, add_to_chat_history
import time
import random

# Import knowledge retrieval if available
try:
    from knowledge_retriever import get_african_topic_suggestions
    KNOWLEDGE_RETRIEVAL_AVAILABLE = True
except ImportError:
    KNOWLEDGE_RETRIEVAL_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="BintaBot - African Cultural Assistant",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #2E8B57, #228B22);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-box {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #2E8B57;
        margin: 1rem 0;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #E3F2FD;
        border-left: 4px solid #2196F3;
    }
    .bot-message {
        background-color: #F3E5F5;
        border-left: 4px solid #9C27B0;
    }
    .proverb-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .fact-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .cultural-highlight {
        background: linear-gradient(135deg, #FFD700, #FFA500);
        padding: 1rem;
        border-radius: 8px;
        color: #333;
        margin: 0.5rem 0;
    }
    .empire-timeline {
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

def create_african_map():
    """Create a simple African map visualization"""
    st.markdown("### 🗺️ African Cultural Map")
    
    # Simple ASCII art map of Africa with cultural highlights
    map_text = """
    ```
                    🌍 AFRICA
                    
        🇲🇦 Morocco    🇪🇬 Egypt
           🇹🇳 Tunisia     🇸🇩 Sudan
    🇩🇿 Algeria  🇱🇾 Libya  🇹🇩 Chad
    🇲🇷 Mauritania  🇳🇪 Niger  🇨🇫 CAR
    🇸🇳 Senegal  🇲🇱 Mali  🇳🇬 Nigeria
    🇬🇲 Gambia  🇧🇫 Burkina Faso  🇨🇲 Cameroon
    🇬🇳 Guinea  🇨🇮 Ivory Coast  🇬🇦 Gabon
    🇸🇱 Sierra Leone  🇬🇭 Ghana  🇨🇬 Congo
    🇱🇷 Liberia  🇹🇬 Togo  🇨🇩 DRC
    🇨🇮 Ivory Coast  🇧🇯 Benin  🇦🇴 Angola
    🇬🇭 Ghana  🇳🇬 Nigeria  🇿🇲 Zambia
    🇹🇬 Togo  🇨🇲 Cameroon  🇿🇼 Zimbabwe
    🇧🇯 Benin  🇨🇫 CAR  🇧🇼 Botswana
    🇳🇬 Nigeria  🇨🇬 Congo  🇿🇦 South Africa
    🇨🇲 Cameroon  🇬🇦 Gabon  🇲🇿 Mozambique
    🇨🇫 CAR  🇨🇬 Congo  🇲🇼 Malawi
    🇨🇬 Congo  🇨🇩 DRC  🇹🇿 Tanzania
    🇨🇩 DRC  🇦🇴 Angola  🇰🇪 Kenya
    🇦🇴 Angola  🇿🇲 Zambia  🇺🇬 Uganda
    🇿🇲 Zambia  🇿🇼 Zimbabwe  🇷🇼 Rwanda
    🇿🇼 Zimbabwe  🇧🇼 Botswana  🇧🇮 Burundi
    🇧🇼 Botswana  🇿🇦 South Africa  🇪🇹 Ethiopia
    🇿🇦 South Africa  🇲🇿 Mozambique  🇸🇴 Somalia
    🇲🇿 Mozambique  🇲🇼 Malawi  🇩🇯 Djibouti
    🇲🇼 Malawi  🇹🇿 Tanzania  🇪🇷 Eritrea
    🇹🇿 Tanzania  🇰🇪 Kenya  🇸🇸 South Sudan
    🇰🇪 Kenya  🇺🇬 Uganda  🇸🇴 Somalia
    🇺🇬 Uganda  🇷🇼 Rwanda  🇪🇹 Ethiopia
    🇷🇼 Rwanda  🇧🇮 Burundi  🇪🇷 Eritrea
    🇧🇮 Burundi  🇪🇹 Ethiopia  🇸🇸 South Sudan
    🇪🇹 Ethiopia  🇸🇴 Somalia  🇩🇯 Djibouti
    🇸🇴 Somalia  🇩🇯 Djibouti  🇪🇷 Eritrea
    🇩🇯 Djibouti  🇪🇷 Eritrea  🇸🇸 South Sudan
    🇪🇷 Eritrea  🇸🇸 South Sudan  🇸🇴 Somalia
    🇸🇸 South Sudan  🇸🇴 Somalia  🇩🇯 Djibouti
    ```
    """
    
    st.code(map_text, language=None)
    
    # Cultural highlights
    st.markdown("""
    <div class="cultural-highlight">
        <h4>🌟 Cultural Highlights:</h4>
        <ul>
            <li><strong>West Africa:</strong> Griot storytelling, Kente cloth, Djembe drums</li>
            <li><strong>East Africa:</strong> Swahili culture, Maasai traditions, Coffee ceremonies</li>
            <li><strong>North Africa:</strong> Berber culture, Islamic architecture, Desert traditions</li>
            <li><strong>Central Africa:</strong> Pygmy cultures, Rainforest wisdom, Traditional medicine</li>
            <li><strong>Southern Africa:</strong> Zulu culture, San rock art, Ubuntu philosophy</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

def create_empire_timeline():
    """Create a timeline of African empires"""
    st.markdown("### ⏰ African Empires Timeline")
    
    timeline_data = [
        {"period": "300-1200 CE", "empire": "Ghana Empire", "location": "West Africa", "achievement": "Land of Gold"},
        {"period": "1235-1670 CE", "empire": "Mali Empire", "location": "West Africa", "achievement": "Mansa Musa's wealth"},
        {"period": "1464-1591 CE", "empire": "Songhai Empire", "location": "West Africa", "achievement": "Largest West African empire"},
        {"period": "1270-1974 CE", "empire": "Ethiopian Empire", "location": "East Africa", "achievement": "Never colonized"},
        {"period": "1400-1700 CE", "empire": "Benin Empire", "location": "West Africa", "achievement": "Benin bronzes"},
        {"period": "1000-1500 CE", "empire": "Great Zimbabwe", "location": "Southern Africa", "achievement": "Stone architecture"}
    ]
    
    timeline_html = """
    <div class="empire-timeline">
        <h4>🏛️ Great African Empires:</h4>
    """
    
    for empire in timeline_data:
        timeline_html += f"""
        <div style="margin: 1rem 0; padding: 0.5rem; border-left: 3px solid #00bcd4; background: rgba(255,255,255,0.3);">
            <strong>{empire['empire']}</strong> ({empire['period']})<br>
            <em>Location:</em> {empire['location']}<br>
            <em>Notable:</em> {empire['achievement']}
        </div>
        """
    
    timeline_html += "</div>"
    st.markdown(timeline_html, unsafe_allow_html=True)

def create_language_guide():
    """Create a basic African language guide"""
    st.markdown("### 🗣️ African Language Guide")
    
    languages = {
        "Swahili": {"greeting": "Jambo", "thank_you": "Asante", "goodbye": "Kwaheri"},
        "Yoruba": {"greeting": "Bawo ni", "thank_you": "O se", "goodbye": "O da bo"},
        "Zulu": {"greeting": "Sawubona", "thank_you": "Ngiyabonga", "goodbye": "Hamba kahle"},
        "Amharic": {"greeting": "Selam", "thank_you": "Ameseginalehu", "goodbye": "Dehna hun"},
        "Hausa": {"greeting": "Sannu", "thank_you": "Na gode", "goodbye": "Sai an jima"}
    }
    
    for lang, phrases in languages.items():
        with st.expander(f"🇹🇿 {lang}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**Hello:** {phrases['greeting']}")
            with col2:
                st.markdown(f"**Thank you:** {phrases['thank_you']}")
            with col3:
                st.markdown(f"**Goodbye:** {phrases['goodbye']}")

def main():
    # Initialize chat session
    initialize_chat_session()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>BintaBot - African Cultural Assistant</h1>
        <p>Your wise companion for exploring African culture, history, and wisdom</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Model status indicator
    if not check_model_status():
        st.markdown("""
        <div class="feature-box">
            <h4>Loading BintaBot's Wisdom...</h4>
            <p>BintaBot is loading her knowledge of African culture, history, and wisdom. This may take a moment on first startup.</p>
        </div>
        """, unsafe_allow_html=True)
        st.info("Tip: If loading takes too long, try refreshing the page.")
        
        # Show loading progress
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress_bar.progress(i + 1)
        st.success("BintaBot is ready to share wisdom!")
    
    # Knowledge retrieval status
    if KNOWLEDGE_RETRIEVAL_AVAILABLE:
        st.markdown("""
        <div class="feature-box">
            <h4>Enhanced Learning Active</h4>
            <p>BintaBot can now search and learn from online materials about Africa, including Wikipedia and current sources!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Knowledge retrieval system not available. Using built-in knowledge only.")
    
    # Create cultural widgets in sidebar
    create_cultural_widgets()
    
    # Main content area with tabs
    tab1, tab2, tab3 = st.tabs(["Chat with BintaBot", "Cultural Explorer", "Learning Center"])
    
    with tab1:
        st.markdown("### Chat with BintaBot")
        
        # Chat interface
        culturally_aware_chat()
        
        # Quick actions
        st.markdown("### Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Ask about History"):
                st.session_state.quick_question = "Tell me about the Mali Empire"
                
        with col2:
            if st.button("Ask about Culture"):
                st.session_state.quick_question = "What is Ubuntu philosophy?"
                
        with col3:
            if st.button("Ask about Music"):
                st.session_state.quick_question = "Tell me about African drums"
        
        # New session button
        if st.button("New Session"):
            st.session_state.chat_history = []
            st.session_state.quick_question = ""
            st.rerun()
    
    with tab2:
        st.markdown("### 🗺️ Explore African Culture")
        
        # African map
        create_african_map()
        
        # Empire timeline
        create_empire_timeline()
        
        # Language guide
        create_language_guide()
    
    with tab3:
        st.markdown("### Learning Center")
        
        # Learning resources
        st.markdown("""
        <div class="feature-box">
            <h4>Learning Tips:</h4>
            <ul>
                <li>Ask specific questions to get detailed answers</li>
                <li>Use follow-up questions to explore topics deeper</li>
                <li>Try asking about different aspects of African culture</li>
                <li>Learn about historical figures and their legacies</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666; padding: 2rem;">
            <p><strong>BintaBot</strong> - Connecting you to the wisdom of Africa</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 