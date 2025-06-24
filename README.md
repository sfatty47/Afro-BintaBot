# 🌍 BintaBot - African Cultural Assistant

BintaBot is a culturally-aware African chatbot that combines traditional wisdom with modern learning capabilities. She can learn from extensive online materials about Africa, providing accurate, comprehensive, and culturally-grounded responses.

## ✨ Features

### 🧠 Enhanced Learning System
- **Real-time Knowledge Retrieval**: Searches Wikipedia and current online sources
- **Academic Integration**: Pulls from reliable academic sources about Africa
- **Comprehensive Coverage**: Covers history, culture, philosophy, geography, and more
- **Factual Accuracy**: Prevents hallucination with verified information

### 🌟 Cultural Intelligence
- **Ancient African Empires**: Mali, Ghana, Songhai, and more
- **Oral Traditions**: Griot storytelling and wisdom
- **Philosophy**: Ubuntu and African community values
- **Proverbs & Wisdom**: Traditional African sayings and teachings
- **Cultural Greetings**: Authentic African ways of connecting

### 🎯 Smart Response System
- **Context-Aware**: Understands cultural nuances
- **Multi-Source Learning**: Combines built-in knowledge with online research
- **Fallback Protection**: Graceful degradation when online sources unavailable
- **Timeout Handling**: Fast responses even with complex queries

## 🚀 Quick Start

### Cloud Version (Recommended)
1. Visit the Streamlit Cloud deployment
2. Start chatting with BintaBot about African culture
3. Experience enhanced learning from online materials

### Local Installation
```bash
# Clone the repository
git clone <repository-url>
cd fatoubot

# Install dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run streamlit_app.py
```

## 📚 Knowledge Sources

BintaBot learns from multiple sources:

### 🔍 Online Learning
- **Wikipedia**: Academic information about African topics
- **DuckDuckGo Search**: Current information and news
- **Cultural Databases**: African history and traditions
- **Academic Sources**: Scholarly articles and research

### 📖 Built-in Knowledge
- **Historical Empires**: Detailed information about Mali, Ghana, Songhai
- **Cultural Figures**: Sundiata Keita, Mansa Musa, and more
- **Philosophical Traditions**: Ubuntu and African wisdom
- **Oral Traditions**: Griot storytelling and proverbs

## 🎓 Learning Categories

### History
- African empires and kingdoms
- Trans-Saharan trade routes
- Colonial history and independence movements
- Ancient civilizations

### Culture
- Traditional religions and beliefs
- Music, dance, and art
- Languages and literature
- Festivals and celebrations

### Philosophy
- Ubuntu philosophy
- Community values
- Moral teachings
- Traditional wisdom

### Geography
- African landscapes and climate
- Natural resources
- Wildlife and ecosystems
- Cities and landmarks

## 💬 Example Conversations

**User**: "Tell me about Sundiata Keita"
**BintaBot**: *Searches online sources and provides comprehensive information about the founder of the Mali Empire, including his childhood, battles, and legacy*

**User**: "What is Ubuntu philosophy?"
**BintaBot**: *Explains the Nguni Bantu concept of interconnectedness and community*

**User**: "Share an African proverb"
**BintaBot**: *Shares traditional wisdom like "It takes a village to raise a child" with cultural context*

## 🔧 Technical Architecture

### Model System
- **Primary**: Mistral-7B-Instruct-v0.2 (with Hugging Face authentication)
- **Fallback**: DialoGPT-medium (open access)
- **Knowledge Retrieval**: Wikipedia + DuckDuckGo integration

### Response Generation
1. **Online Search**: Query online sources for current information
2. **Knowledge Integration**: Combine with built-in cultural knowledge
3. **Context Analysis**: Apply cultural understanding
4. **Response Generation**: Create culturally-aware responses

### Error Handling
- **Timeout Protection**: 30-second generation limits
- **Fallback Responses**: Cultural knowledge when models fail
- **Graceful Degradation**: Maintains functionality with partial failures

## 🌐 Deployment

### Streamlit Cloud
- Text-based interface with enhanced learning
- Real-time knowledge retrieval
- Responsive design
- No voice features (cloud limitations)

### Local Development
- Full voice capabilities
- Complete feature set
- Offline knowledge base
- Customizable configuration

## 🔐 Security & Privacy

- **No Data Storage**: Conversations are not stored
- **Secure Authentication**: Hugging Face tokens via Streamlit secrets
- **Privacy-First**: No personal information collection
- **Open Source**: Transparent and auditable code

## 🤝 Contributing

We welcome contributions to enhance BintaBot's knowledge and capabilities:

1. **Knowledge Expansion**: Add more cultural content
2. **Source Integration**: Connect additional reliable sources
3. **Language Support**: Add more African languages
4. **Feature Development**: Enhance learning algorithms

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- African griots and oral tradition keepers
- Academic researchers of African history and culture
- Open source community for tools and libraries
- Cultural experts who preserve African wisdom

---

*BintaBot: "I am because we are" - Learning and sharing the wisdom of Africa together.* 🌍 