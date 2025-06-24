import speech_recognition as sr
import pyttsx3
import threading
import time

class VoiceAssistant:
    def __init__(self):
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize text-to-speech
        self.tts_engine = pyttsx3.init()
        
        # Configure TTS voice (optional: set to a female voice for BintaBot)
        voices = self.tts_engine.getProperty('voices')
        if voices:
            # Try to find a female voice
            for voice in voices:
                if 'female' in voice.name.lower() or 'samantha' in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
        
        # Set speech rate and volume
        self.tts_engine.setProperty('rate', 150)  # Speed of speech
        self.tts_engine.setProperty('volume', 0.9)  # Volume level
        
        # Adjust for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
    
    def listen(self):
        """Listen for voice input and convert to text"""
        try:
            with self.microphone as source:
                print("Listening... (speak now)")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
            print("Processing speech...")
            text = self.recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text.lower()
            
        except sr.WaitTimeoutError:
            print("No speech detected within timeout")
            return None
        except sr.UnknownValueError:
            print("Could not understand the audio")
            return None
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return None
        except Exception as e:
            print(f"Error during speech recognition: {e}")
            return None
    
    def speak(self, text):
        """Convert text to speech and play it"""
        try:
            print(f"BintaBot: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"Error during text-to-speech: {e}")
    
    def speak_async(self, text):
        """Speak text asynchronously (non-blocking)"""
        thread = threading.Thread(target=self.speak, args=(text,))
        thread.daemon = True
        thread.start()
        return thread

# Global voice assistant instance
voice_assistant = VoiceAssistant() 