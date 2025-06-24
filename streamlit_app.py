import streamlit as st
import speech_recognition as sr
import pyttsx3
import threading
import time
from chatbot import culturally_aware_chat

# Page configuration
st.set_page_config(
    page_title="BintaBot - African Voice Assistant",
    page_icon="🎤",
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
    .voice-button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border: none;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        cursor: pointer;
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
</style>
""", unsafe_allow_html=True)

# Initialize speech recognition and TTS
@st.cache_resource
def init_voice():
    try:
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        tts_engine = pyttsx3.init()
        
        # Configure TTS voice
        voices = tts_engine.getProperty('voices')
        if voices:
            for voice in voices:
                if 'female' in voice.name.lower() or 'samantha' in voice.name.lower():
                    tts_engine.setProperty('voice', voice.id)
                    break
        
        tts_engine.setProperty('rate', 150)
        tts_engine.setProperty('volume', 0.9)
        
        return recognizer, microphone, tts_engine
    except Exception as e:
        st.error(f"Voice system initialization failed: {e}")
        return None, None, None

def listen_for_speech(recognizer, microphone):
    """Listen for voice input"""
    try:
        with microphone as source:
            st.info("🎤 Listening... Speak now!")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        
        st.info("🔄 Processing speech...")
        text = recognizer.recognize_google(audio)
        return text.lower()
    except sr.WaitTimeoutError:
        st.error("No speech detected within timeout")
        return None
    except sr.UnknownValueError:
        st.error("Could not understand the audio")
        return None
    except sr.RequestError as e:
        st.error(f"Could not request results; {e}")
        return None
    except Exception as e:
        st.error(f"Error during speech recognition: {e}")
        return None

def speak_text(tts_engine, text):
    """Convert text to speech"""
    try:
        tts_engine.say(text)
        tts_engine.runAndWait()
    except Exception as e:
        st.error(f"Error during text-to-speech: {e}")

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎤 BintaBot - African Voice Assistant</h1>
        <p><em>Speak with wisdom, learn from tradition</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize voice components
    recognizer, microphone, tts_engine = init_voice()
    
    if recognizer and microphone and tts_engine:
        st.success("✅ Voice system initialized successfully!")
    else:
        st.warning("⚠️ Voice features may not work in this environment. Text chat is still available.")
    
    # Sidebar
    st.sidebar.header("🎤 Voice Controls")
    
    # Voice input button
    if st.sidebar.button("🎤 Start Voice Input", type="primary", use_container_width=True):
        if recognizer and microphone:
            user_input = listen_for_speech(recognizer, microphone)
            if user_input:
                st.session_state.voice_input = user_input
        else:
            st.error("Voice input not available in this environment")
    
    # Display voice input if available
    if 'voice_input' in st.session_state:
        st.text_area("🎤 Voice Input:", value=st.session_state.voice_input, height=100)
    
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
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get BintaBot response
        with st.chat_message("assistant"):
            with st.spinner("🤔 BintaBot is thinking..."):
                response = culturally_aware_chat(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Voice response option
        if tts_engine:
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("🔊 Speak Response"):
                    speak_text(tts_engine, response)
    
    # Handle voice input from sidebar
    if 'voice_input' in st.session_state and st.session_state.voice_input:
        prompt = st.session_state.voice_input
        st.session_state.messages.append({"role": "user", "content": f"🎤 {prompt}"})
        with st.chat_message("user"):
            st.markdown(f"🎤 {prompt}")
        
        # Get BintaBot response
        with st.chat_message("assistant"):
            with st.spinner("🤔 BintaBot is thinking..."):
                response = culturally_aware_chat(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Auto-speak voice responses if TTS is available
        if tts_engine:
            speak_text(tts_engine, response)
        
        # Clear voice input
        del st.session_state.voice_input
    
    # Clear chat button
    if st.sidebar.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    # Instructions
    st.sidebar.markdown("---")
    st.sidebar.markdown("### How to use:")
    st.sidebar.markdown("1. **Voice Input**: Click the voice button and speak")
    st.sidebar.markdown("2. **Text Input**: Type in the chat box")
    st.sidebar.markdown("3. **Voice Response**: Click 🔊 to hear responses")
    st.sidebar.markdown("4. **Clear Chat**: Remove all conversation history")
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("### About BintaBot")
    st.sidebar.markdown("BintaBot is a culturally-aware African assistant with deep knowledge of African traditions, proverbs, and wisdom.")
    
    # Quick commands
    st.sidebar.markdown("### Quick Commands:")
    st.sidebar.markdown("- 'Tell me a story'")
    st.sidebar.markdown("- 'Share wisdom'")
    st.sidebar.markdown("- 'How is the family?'")
    st.sidebar.markdown("- 'Tell me about Ubuntu'")

if __name__ == "__main__":
    main() 