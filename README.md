# BintaBot - African Cultural Assistant

A culturally-aware African chatbot that shares wisdom, history, and cultural knowledge using the Mistral-7B model with a FastAPI backend and Streamlit UI.

## Features

### Enhanced Learning System
- **Web Search Integration**: Searches Wikipedia and other sources for current African information
- **Knowledge Retrieval**: Filters and processes online content for cultural relevance
- **Dynamic Learning**: Continuously updates knowledge base with new information

### Cultural Intelligence
- **Ubuntu Philosophy**: Embodies "I am because we are" in responses
- **Proverb Integration**: Shares traditional African wisdom and proverbs
- **Historical Accuracy**: Provides factual information about African history and cultures
- **Cultural Sensitivity**: Respects diverse African traditions and perspectives

### Smart Response System
- **Topic Detection**: Automatically identifies query intent (history, culture, music, etc.)
- **Response Cleaning**: Removes repetition and improves clarity
- **Context Awareness**: Maintains conversation context and avoids redundancy
- **Fallback Responses**: Provides culturally-rich responses when external sources are unavailable

## Quick Start

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

## Knowledge Sources

BintaBot learns from multiple sources:

### Online Learning
- **Wikipedia**: Academic information about African topics
- **DuckDuckGo Search**: Current information and news
- **Cultural Databases**: African history and traditions
- **Academic Sources**: Scholarly articles and research

### Built-in Knowledge
- **Historical Empires**: Detailed information about Mali, Ghana, Songhai
- **Cultural Figures**: Sundiata Keita, Mansa Musa, and more
- **Philosophical Traditions**: Ubuntu and African wisdom
- **Oral Traditions**: Griot storytelling and proverbs

## Learning Categories

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

## Example Conversations

**User**: "Tell me about Sundiata Keita"
**BintaBot**: *Searches online sources and provides comprehensive information about the founder of the Mali Empire, including his childhood, battles, and legacy*

**User**: "What is Ubuntu philosophy?"
**BintaBot**: *Explains the Nguni Bantu concept of interconnectedness and community*

**User**: "Share an African proverb"
**BintaBot**: *Shares traditional wisdom like "It takes a village to raise a child" with cultural context*

## Technical Architecture

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

## Deployment

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

## Security & Privacy

- **No Data Storage**: Conversations are not stored
- **Secure Authentication**: Hugging Face tokens via Streamlit secrets
- **Privacy-First**: No personal information collection
- **Open Source**: Transparent and auditable code

## Contributing

We welcome contributions to enhance BintaBot's knowledge and capabilities:

1. **Knowledge Expansion**: Add more cultural content
2. **Source Integration**: Connect additional reliable sources
3. **Language Support**: Add more African languages
4. **Feature Development**: Enhance learning algorithms

## License

This project is open source and available under the MIT License.

## Acknowledgments

- African griots and oral tradition keepers
- Academic researchers of African history and culture
- Open source community for tools and libraries
- Cultural experts who preserve African wisdom

*BintaBot: "I am because we are" - Learning and sharing the wisdom of Africa together.* 