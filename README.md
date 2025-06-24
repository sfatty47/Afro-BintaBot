# 🎤 BintaBot - African Voice Assistant

A culturally-aware African chatbot with voice capabilities, built with wisdom and tradition.

## 🌟 Features

- **Voice Input**: Speak to BintaBot using your microphone
- **Voice Output**: Hear BintaBot's responses spoken aloud
- **Text Chat**: Traditional text-based conversation
- **Cultural Wisdom**: Responses grounded in African traditions, proverbs, and values
- **Multiple Interfaces**: Command-line, Streamlit UI, and FastAPI endpoints

## 🛠️ Installation

1. **Clone and setup environment:**
```bash
cd fatoubot
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Install system dependencies (macOS):**
```bash
# Install portaudio for microphone access
brew install portaudio

# Install cmake (if needed)
brew install cmake
```

## 🚀 Usage

### 1. Voice Chat (Command Line)
```bash
python voice_chatbot.py
```
- Choose between voice input, text input, or quit
- Voice responses are automatic
- Simple and intuitive interface

### 2. Streamlit Voice UI
```bash
streamlit run voice_ui.py
```
- Beautiful web interface with voice controls
- Sidebar for voice input button
- Chat history with voice response options
- Real-time speech recognition

### 3. FastAPI Backend
```bash
uvicorn api:app --reload
```
- RESTful API endpoints
- Voice chat endpoint: `/voice/chat`
- Speech-to-text endpoint: `/voice/speech-to-text`
- Text chat endpoint: `/chat`

### 4. Simple Text UI
```bash
streamlit run chatbot_ui.py
```
- Basic text-only interface
- No voice capabilities

## 🎤 Voice Features

### Speech Recognition
- Uses Google's speech recognition API
- Automatic noise adjustment
- 5-second timeout with 10-second phrase limit
- Supports multiple languages

### Text-to-Speech
- Female voice optimized for BintaBot
- Adjustable speech rate (150 WPM)
- Volume control (90%)
- Asynchronous speech for non-blocking operation

## 📁 Project Structure

```
fatoubot/
├── model.py              # Mistral-7B model loading
├── chatbot.py            # Core chat logic with BintaBot prompt
├── voice_utils.py        # Voice recognition and TTS utilities
├── voice_chatbot.py      # Command-line voice interface
├── voice_ui.py           # Streamlit voice interface
├── chatbot_ui.py         # Basic text interface
├── api.py                # FastAPI backend with voice endpoints
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🔧 API Endpoints

### Text Chat
```bash
POST /chat
{
  "message": "Hello BintaBot"
}
```

### Voice Chat
```bash
POST /voice/chat
{
  "message": "Tell me a proverb"
}
```
Returns both text response and audio data.

### Speech-to-Text
```bash
POST /voice/speech-to-text
# Upload audio file (WAV format)
```

## 🎯 Voice Commands

- **"Goodbye"** or **"Exit"** or **"Quit"** - End the conversation
- **"How is the family?"** - Cultural greeting
- **"You are invited"** - Cultural invitation response
- **"Tell me a story"** - Request African folktale
- **"Share wisdom"** - Request African proverb

## 🌍 Cultural Context

BintaBot is designed with deep knowledge of:
- Ancient African empires (Mali, Ghana, Songhai)
- Oral storytelling traditions (Griots)
- Community philosophies (Ubuntu)
- African proverbs and folk wisdom
- Cultural greetings and customs

## 🐛 Troubleshooting

### Microphone Issues
- Ensure microphone permissions are granted
- Check if microphone is connected and working
- Try different microphone if available

### Speech Recognition Errors
- Speak clearly and at normal volume
- Reduce background noise
- Check internet connection (Google API required)

### Text-to-Speech Issues
- Ensure speakers/headphones are connected
- Check system volume
- Try different voice settings in voice_utils.py

### Installation Issues
- Update pip: `pip install --upgrade pip`
- Install system dependencies (portaudio, cmake)
- Use virtual environment to avoid conflicts

## 🤝 Contributing

Feel free to contribute by:
- Adding more African proverbs and wisdom
- Improving voice recognition accuracy
- Enhancing the cultural knowledge base
- Adding support for African languages

## 📄 License

This project is open source and available under the MIT License.

---

*"Wisdom is like a baobab tree; no one individual can embrace it."* - African Proverb 