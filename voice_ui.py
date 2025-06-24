import streamlit as st
import speech_recognition as sr
import pyttsx3
import threading
import time
from chatbot import culturally_aware_chat

# Initialize speech recognition and TTS
@st.cache_resource
def init_voice():
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
    st.set_page_config(
        page_title="BintaBot Voice Assistant",
        page_icon="🎤",
        layout="wide"
    )
    
    st.title("🎤 BintaBot - African Voice Assistant")
    st.markdown("### Speak with wisdom, learn from tradition")
    
    # Initialize voice components
    try:
        recognizer, microphone, tts_engine = init_voice()
        st.success("✅ Voice system initialized successfully!")
    except Exception as e:
        st.error(f"❌ Failed to initialize voice system: {e}")
        st.info("Please ensure you have a microphone connected and the required packages installed.")
        return
    
    # Sidebar for voice controls
    st.sidebar.header("🎤 Voice Controls")
    
    # Voice input button
    if st.sidebar.button("🎤 Start Voice Input", type="primary"):
        user_input = listen_for_speech(recognizer, microphone)
        if user_input:
            st.session_state.voice_input = user_input
    
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
        
        # Auto-speak voice responses
        speak_text(tts_engine, response)
        
        # Clear voice input
        del st.session_state.voice_input
    
    # Clear chat button
    if st.sidebar.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    # Instructions
    st.sidebar.markdown("---")
    st.sidebar.markdown("### How to use:")
    st.sidebar.markdown("1. **Voice Input**: Click the voice button and speak")
    st.sidebar.markdown("2. **Text Input**: Type in the chat box")
    st.sidebar.markdown("3. **Voice Response**: Click 🔊 to hear responses")
    st.sidebar.markdown("4. **Clear Chat**: Remove all conversation history")

if __name__ == "__main__":
    main() 