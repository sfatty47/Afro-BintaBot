# 🌍 BintaBot - African Cultural Assistant

A culturally-aware African chatbot with deep knowledge of African traditions, proverbs, and wisdom.

## 🌟 Features

- **Cultural Wisdom**: Responses grounded in African traditions, proverbs, and values
- **Text Chat**: Rich conversation about African culture and history
- **Multiple Interfaces**: Command-line, Streamlit UI, and FastAPI endpoints
- **Cloud Deployment**: Ready for Streamlit Cloud deployment
- **Local Voice Features**: Voice input/output available in local development

## 🚀 Quick Start - Streamlit Cloud

### Deploy to Streamlit Cloud (Recommended)

1. **Fork this repository** to your GitHub account
2. **Go to [Streamlit Cloud](https://streamlit.io/cloud)**
3. **Sign in** with your GitHub account
4. **Click "New app"**
5. **Select your forked repository**
6. **Set the main file path**: `streamlit_app.py`
7. **Add Hugging Face Token** (see setup below)
8. **Click "Deploy"**

Your BintaBot will be live in minutes! 🌍

### 🔑 Hugging Face Token Setup

BintaBot uses the Mistral-7B model which requires authentication. To set up your token:

1. **Get a Hugging Face Token:**
   - Go to [Hugging Face](https://huggingface.co/settings/tokens)
   - Sign in or create an account
   - Click "New token"
   - Give it a name (e.g., "BintaBot")
   - Select "Read" permissions
   - Copy the token

2. **Add Token to Streamlit Cloud:**
   - In your Streamlit Cloud app settings
   - Go to "Secrets" section
   - Add this configuration:
   ```toml
   HF_TOKEN = "your_hugging_face_token_here"
   ```

3. **Alternative: Use Fallback Model**
   - If you don't want to set up a token, the app will automatically use a fallback model
   - The fallback model is open-access and doesn't require authentication
   - You'll still get cultural responses, though they may be less sophisticated

**Note**: The cloud version focuses on text-based cultural exchange. Voice features are available in the local version.

### Local Development (Full Features)

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

4. **Set up Hugging Face Token (Optional):**
   - Create `.streamlit/secrets.toml` file
   - Add: `HF_TOKEN = "your_token_here"`
   - This enables the full Mistral-7B model locally

## 🛠️ Usage

### 1. Streamlit Cloud (Text Only)
- Visit your deployed app URL
- Type messages in chat box
- Ask about African wisdom, stories, or culture
- Perfect for sharing cultural knowledge

### 2. Local Development (Full Features)

#### Voice Chat (Command Line)
```bash
python voice_chatbot.py
```
- Choose between voice input, text input, or quit
- Voice responses are automatic
- Simple and intuitive interface

#### Streamlit Voice UI (Local)
```bash
streamlit run voice_ui.py
```
- Beautiful web interface with voice controls
- Sidebar for voice input button
- Chat history with voice response options
- Real-time speech recognition

#### FastAPI Backend
```bash
uvicorn api:app --reload
```
- RESTful API endpoints
- Voice chat endpoint: `/voice/chat`
- Speech-to-text endpoint: `/voice/speech-to-text`
- Text chat endpoint: `/chat`

#### Simple Text UI
```bash
streamlit run chatbot_ui.py
```
- Basic text-only interface
- No voice capabilities

## 🎤 Voice Features (Local Only)

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
├── streamlit_app.py      # Main app for Streamlit Cloud deployment (text-only)
├── model.py              # Mistral-7B model loading with fallback
├── chatbot.py            # Core chat logic with BintaBot prompt
├── voice_utils.py        # Voice recognition and TTS utilities (local)
├── voice_chatbot.py      # Command-line voice interface (local)
├── voice_ui.py           # Streamlit voice interface (local)
├── chatbot_ui.py         # Basic text interface
├── api.py                # FastAPI backend with voice endpoints (local)
├── requirements.txt      # Python dependencies
├── .streamlit/           # Streamlit configuration
│   ├── config.toml
│   └── secrets.toml      # Hugging Face token (local only)
└── README.md            # This file
```

## 🔧 API Endpoints (Local)

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

## 🎯 Quick Commands

- **"Tell me a story"** - Request African folktale
- **"Share wisdom"** - Request African proverb
- **"How is the family?"** - Cultural greeting
- **"Tell me about Ubuntu"** - Learn about African philosophy
- **"What is a griot?"** - Learn about oral tradition
- **"Share an African proverb"** - Get wisdom from ancestors

## 🌍 Cultural Context

BintaBot is designed with deep knowledge of:
- Ancient African empires (Mali, Ghana, Songhai)
- Oral storytelling traditions (Griots)
- Community philosophies (Ubuntu)
- African proverbs and folk wisdom
- Cultural greetings and customs

## 🐛 Troubleshooting

### Streamlit Cloud Issues
- **Model Loading Errors**: Check if Hugging Face token is properly set in secrets
- **Fallback Model**: If Mistral-7B fails, the app automatically uses DialoGPT-medium
- **Voice features are not available** in cloud environment
- **Text chat will always work** with fallback responses
- Check deployment logs for errors
- Ensure all dependencies are properly specified

### Hugging Face Token Issues
- **Token not working**: Ensure token has "Read" permissions
- **Model access denied**: Accept the model terms on Hugging Face website
- **Token expired**: Generate a new token
- **Fallback mode**: The app will work with open-access models if token fails

### Local Voice Issues
- Ensure microphone permissions are granted
- Check if microphone is connected and working
- Try different microphone if available
- Install system dependencies (portaudio, cmake)

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