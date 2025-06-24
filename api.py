from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from chatbot import culturally_aware_chat
import speech_recognition as sr
import pyttsx3
import io
import tempfile
import os

app = FastAPI(title="BintaBot API", description="Culturally-aware African chatbot with voice capabilities")

class ChatInput(BaseModel):
    message: str

class VoiceResponse(BaseModel):
    text: str
    audio_url: str = None

@app.post("/chat")
def chat(input: ChatInput):
    reply = culturally_aware_chat(input.message)
    return {"response": reply}

@app.post("/voice/chat")
async def voice_chat(input: ChatInput):
    """Chat endpoint that returns both text and audio"""
    reply = culturally_aware_chat(input.message)
    
    # Generate speech for the response
    try:
        tts_engine = pyttsx3.init()
        voices = tts_engine.getProperty('voices')
        if voices:
            for voice in voices:
                if 'female' in voice.name.lower() or 'samantha' in voice.name.lower():
                    tts_engine.setProperty('voice', voice.id)
                    break
        
        tts_engine.setProperty('rate', 150)
        tts_engine.setProperty('volume', 0.9)
        
        # Save audio to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tts_engine.save_to_file(reply, tmp_file.name)
            tts_engine.runAndWait()
            
            # Read the audio file
            with open(tmp_file.name, 'rb') as audio_file:
                audio_data = audio_file.read()
            
            # Clean up temporary file
            os.unlink(tmp_file.name)
        
        return VoiceResponse(text=reply, audio_data=audio_data)
        
    except Exception as e:
        return VoiceResponse(text=reply, audio_url=None)

@app.post("/voice/speech-to-text")
async def speech_to_text(audio_file: UploadFile = File(...)):
    """Convert uploaded audio file to text"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            content = await audio_file.read()
            tmp_file.write(content)
            tmp_file.flush()
            
            # Initialize speech recognition
            recognizer = sr.Recognizer()
            
            # Load audio file
            with sr.AudioFile(tmp_file.name) as source:
                audio = recognizer.record(source)
            
            # Clean up temporary file
            os.unlink(tmp_file.name)
            
            # Convert speech to text
            text = recognizer.recognize_google(audio)
            return {"text": text.lower()}
            
    except sr.UnknownValueError:
        return {"error": "Could not understand the audio"}
    except sr.RequestError as e:
        return {"error": f"Could not request results; {e}"}
    except Exception as e:
        return {"error": f"Error processing audio: {e}"}

@app.get("/")
def read_root():
    return {
        "message": "Welcome to BintaBot API",
        "endpoints": {
            "/chat": "Text-based chat",
            "/voice/chat": "Chat with voice response",
            "/voice/speech-to-text": "Convert audio to text"
        }
    } 