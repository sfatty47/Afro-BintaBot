from model import generate_response, get_cultural_response
from rag_system import get_rag_response
import streamlit as st
import time

system_prompt = """
You are BintaBot, a wise and culturally-grounded African assistant.

You possess deep knowledge of Africa's ancient history, traditions, proverbs, and moral values passed down through generations. You understand the rich diversity of African cultures—from the empires of Mali, Ghana, and Songhai, to the oral storytelling traditions of the griots, and the community-centered philosophies like Ubuntu.

You speak with clarity, respect, and warmth. When appropriate, use African proverbs, folk wisdom, or historical examples to explain ideas or provide guidance. You recognize and respond appropriately to culturally significant greetings such as "How is the family?" or "You are invited."

Always reply in clear, simple English, using culturally relevant analogies when helpful. Be kind, grounded, and wise, like an elder speaking to younger generations.
"""

# Fallback responses for when the model is not available
fallback_responses = {
    "greeting": [
        "Salaam! I am BintaBot, your African cultural assistant. I'm here to share wisdom from the heart of Africa.",
        "Greetings! I am BintaBot, keeper of African wisdom and traditions. How may I serve you today?",
        "Welcome! I am BintaBot, your guide to African culture, history, and wisdom."
    ],
    "story": [
        "Let me share a tale from the griots: Once, in the ancient kingdom of Mali, there lived a wise woman who taught that 'The wealth of a nation is not in its gold, but in the wisdom of its people.'",
        "Here's a story from our ancestors: A young hunter once asked an elder, 'How do I become wise?' The elder replied, 'Listen more than you speak, observe more than you act, and learn from every person you meet.'",
        "In the tradition of our griots: There was a village where the children were taught that 'Ubuntu' means 'I am because we are.' This simple truth guided their every action."
    ],
    "proverb": [
        "As our ancestors said: 'It takes a village to raise a child.' This speaks to the communal nature of African societies.",
        "Here's wisdom from the elders: 'The river flows not by its own power, but by the strength of many streams.'",
        "Our forefathers taught us: 'A single bracelet does not jingle.' Unity brings strength and harmony."
    ],
    "ubuntu": [
        "Ubuntu is a beautiful African philosophy that means 'I am because we are.' It teaches us that our humanity is interconnected - we find our true selves through our relationships with others.",
        "Ubuntu, from the Bantu languages of Southern Africa, embodies the belief that we are all connected. It's the understanding that 'a person is a person through other persons.'",
        "Ubuntu is the heart of African community philosophy. It reminds us that we exist in relation to others - our well-being is tied to the well-being of our community."
    ],
    "griot": [
        "Griots are the traditional storytellers, historians, and keepers of oral tradition in West Africa. They are the living libraries of our people, passing down wisdom through generations.",
        "A griot is more than a storyteller - they are the guardians of our history, culture, and wisdom. They use music, poetry, and narrative to preserve our heritage.",
        "Griots are the cultural memory of African societies. They carry the stories of kings, warriors, and everyday people, ensuring that our traditions live on."
    ],
    "sundiata": [
        "Sundiata Keita was the legendary founder of the Mali Empire in the 13th century. Known as the 'Lion King,' he united the Mandinka people and established one of Africa's greatest empires. His story teaches us about leadership, unity, and the power of determination.",
        "Sundiata Keita, the founder of the Mali Empire, was a remarkable leader who overcame physical challenges to become one of Africa's greatest kings. His empire controlled the gold and salt trade routes, making Mali one of the wealthiest kingdoms of its time.",
        "The story of Sundiata Keita is one of resilience and leadership. Despite being born with a disability, he became the founder of the Mali Empire, proving that true strength comes from character and determination, not physical ability."
    ],
    "mali_empire": [
        "The Mali Empire was one of the greatest African empires, flourishing from the 13th to 16th centuries. It was known for its wealth, particularly in gold, and its famous ruler Mansa Musa, who made a legendary pilgrimage to Mecca.",
        "The Mali Empire, centered in West Africa, was a beacon of learning and culture. Its capital, Timbuktu, became a center of Islamic scholarship and trade, attracting scholars from across the Muslim world.",
        "The Mali Empire represents the height of African civilization, with its sophisticated government, extensive trade networks, and rich cultural traditions. It shows what African societies can achieve when united under strong leadership."
    ],
    "mansa_musa": [
        "Mansa Musa was the most famous ruler of the Mali Empire, known for his legendary pilgrimage to Mecca in 1324. His journey with thousands of followers and vast amounts of gold demonstrated the empire's wealth and power.",
        "Mansa Musa's pilgrimage to Mecca was so extravagant that it affected the gold market in Egypt and the Mediterranean. His generosity and the wealth he displayed showed the world the sophistication of African kingdoms.",
        "Mansa Musa was not just wealthy; he was a wise ruler who invested in education and culture. He built mosques and schools, making Timbuktu a center of learning that attracted scholars from across the Islamic world."
    ],
    "default": [
        "I am BintaBot, your African cultural assistant. I'm here to share the wisdom, stories, and traditions of Africa with you.",
        "Greetings! I'm here to help you learn about African culture, history, and wisdom. What would you like to know?",
        "Welcome! I am BintaBot, keeper of African traditions. How may I share our cultural heritage with you today?"
    ]
}

def get_fallback_response(user_input):
    """Get an appropriate fallback response based on user input"""
    user_input_lower = user_input.lower()
    
    if any(word in user_input_lower for word in ["hello", "hi", "greetings", "salaam"]):
        return fallback_responses["greeting"][0]
    elif any(word in user_input_lower for word in ["story", "tale", "griot"]):
        return fallback_responses["story"][0]
    elif any(word in user_input_lower for word in ["proverb", "wisdom", "elder"]):
        return fallback_responses["proverb"][0]
    elif "ubuntu" in user_input_lower:
        return fallback_responses["ubuntu"][0]
    elif "griot" in user_input_lower:
        return fallback_responses["griot"][0]
    elif "sundiata" in user_input_lower:
        return fallback_responses["sundiata"][0]
    elif "mali" in user_input_lower and "empire" in user_input_lower:
        return fallback_responses["mali_empire"][0]
    elif "mansa musa" in user_input_lower:
        return fallback_responses["mansa_musa"][0]
    else:
        return fallback_responses["default"][0]

def culturally_aware_chat(user_input, chat_history=None):
    """
    Enhanced chat function with cultural warmth, RAG, and BintaBot's persona
    """
    
    # Enhanced system prompt with cultural warmth
    system_prompt = """You are BintaBot, a wise African cultural assistant with the warmth and wisdom of a village elder. 

Your responses should embody:
- Cultural wisdom and ancestral knowledge
- Warm, welcoming tone like a respected elder
- Authentic African perspectives and values
- Connection to community and tradition
- Respect for oral traditions and griot storytelling

When sharing information:
- Rephrase facts with cultural warmth and context
- Include relevant African proverbs when appropriate
- Connect historical events to cultural values
- Share wisdom as if speaking to family
- Avoid dry, academic language - speak from the heart

Remember: You are not just sharing facts, but passing down wisdom from the ancestors."""

    # Enhanced final prompt with cultural warmth instruction
    final_prompt = f"""{system_prompt}

Please answer the user's question in the voice of BintaBot — with cultural wisdom, warmth, and an elder's perspective.
If relevant, include a proverb or historical reference. Avoid copying from Wikipedia word-for-word.
Rephrase information with cultural warmth and connection to African values.

Question: {user_input}

BintaBot:"""

    # Generate response with enhanced prompt
    try:
        # First, try RAG system for better cultural responses
        rag_response = get_rag_response(user_input, chat_history)
        
        # Check if RAG found relevant information (not just a generic response)
        if rag_response and len(rag_response) > 50 and not any(word in rag_response.lower() for word in ["i am here to share", "what specific aspect", "help you learn"]):
            response = rag_response
        else:
            # Try knowledge retrieval system for online information
            try:
                from knowledge_retriever import get_enhanced_african_knowledge, format_knowledge_response
                
                with st.spinner("🔍 Searching for information about this African topic..."):
                    enhanced_knowledge = get_enhanced_african_knowledge(user_input)
                
                if enhanced_knowledge and (enhanced_knowledge.get('wikipedia') or enhanced_knowledge.get('web_results')):
                    formatted_response = format_knowledge_response(enhanced_knowledge)
                    if formatted_response:
                        # Add cultural warmth to the response
                        response = f"""Ah, my child, let me share with you what I have learned about this topic from our collective knowledge...

{formatted_response}

As our elders say, 'Knowledge is like a garden: if it is not cultivated, it cannot be harvested.' Let us continue to learn and grow together.

Would you like to explore more about this topic or learn about related aspects of African culture?"""
                    else:
                        # Fall back to model generation
                        response = generate_response(final_prompt)
                else:
                    # Fall back to model generation
                    response = generate_response(final_prompt)
                    
            except ImportError:
                # Knowledge retrieval not available, fall back to model generation
                response = generate_response(final_prompt)
        
        # Post-process to ensure cultural warmth
        if response and not response.startswith("I am BintaBot"):
            # Add cultural warmth if response seems too formal
            if any(word in response.lower() for word in ["according to", "research shows", "studies indicate"]):
                response = f"Ah, my child, let me share this wisdom with you... {response}"
            
            # Add follow-up engagement
            follow_ups = [
                "Would you like to hear a proverb related to this?",
                "Should I tell you more about the griots who preserve such stories?",
                "Would you like to learn more about our ancestors' wisdom?",
                "Shall I share how this connects to our community values?",
                "Would you like to hear a story about this from our oral traditions?",
                "Should I tell you more about how this wisdom guides our daily lives?"
            ]
            
            # Add follow-up 30% of the time
            import random
            if random.random() < 0.3:
                response += f"\n\n💭 {random.choice(follow_ups)}"
        
        return response
        
    except Exception as e:
        st.error(f"Error in chat: {str(e)}")
        # Fallback to cultural response
        return get_cultural_response(user_input)

def get_daily_proverb():
    """Get a daily African proverb"""
    proverbs = [
        "It takes a village to raise a child.",
        "The river flows not by its own power, but by the strength of many streams.",
        "A single bracelet does not jingle.",
        "Wisdom is like a baobab tree; no one individual can embrace it.",
        "The child who has washed their hands can dine with kings.",
        "Unity is strength, division is weakness.",
        "The eye never forgets what the heart has seen.",
        "A bird that flies off the Earth and lands on an anthill is still on the ground.",
        "The wealth of a nation is not in its gold, but in the wisdom of its people.",
        "He who learns, teaches.",
        "The tongue and the teeth work together, yet they quarrel.",
        "A family is like a forest, when you are outside it is dense, when you are inside you see that each tree has its place.",
        "The heart of the wise man lies quiet like limpid water.",
        "Knowledge is like a garden: if it is not cultivated, it cannot be harvested.",
        "The best time to plant a tree was 20 years ago. The second best time is now."
    ]
    
    import random
    return random.choice(proverbs)

def get_did_you_know_fact():
    """Get a random 'Did You Know?' fact about Africa"""
    facts = [
        "Did you know? The University of Timbuktu, founded in 1327, was one of the world's first universities and had over 25,000 students at its peak.",
        "Did you know? The Great Zimbabwe ruins, built without mortar, are the largest ancient structure south of the Sahara.",
        "Did you know? The Swahili language has influenced English words like 'safari' and 'jumbo'.",
        "Did you know? The ancient Egyptians were the first to use toothpaste, made from crushed eggshells and ox hooves.",
        "Did you know? Ethiopia is the only African country that was never colonized by Europeans.",
        "Did you know? The Mali Empire under Mansa Musa was so wealthy that his pilgrimage to Mecca caused inflation in the Mediterranean region.",
        "Did you know? The Yoruba people of Nigeria have one of the highest rates of twins in the world.",
        "Did you know? The ancient city of Carthage in Tunisia was once the richest city in the Mediterranean.",
        "Did you know? The Kingdom of Kush in Sudan ruled Egypt for nearly 100 years as the 25th Dynasty.",
        "Did you know? The rock-hewn churches of Lalibela in Ethiopia were carved from solid rock in the 12th century."
    ]
    
    import random
    return random.choice(facts)

def create_cultural_widgets():
    """Create cultural widgets for the sidebar"""
    st.sidebar.markdown("---")
    
    # Daily Proverb
    st.sidebar.markdown("### 🌟 Proverb of the Day")
    proverb = get_daily_proverb()
    st.sidebar.info(f'*"{proverb}"*')
    
    # Did You Know?
    st.sidebar.markdown("### 💡 Did You Know?")
    fact = get_did_you_know_fact()
    st.sidebar.success(fact)
    
    # Cultural Topics
    st.sidebar.markdown("### 🎯 Explore African Culture")
    topics = [
        "Ancient African Empires",
        "African Proverbs & Wisdom", 
        "Traditional African Music",
        "African Art & Architecture",
        "African Languages",
        "Griot Storytelling",
        "Ubuntu Philosophy",
        "African Trade Routes"
    ]
    
    selected_topic = st.sidebar.selectbox(
        "Choose a topic to learn about:",
        topics,
        index=None,
        placeholder="Select a cultural topic..."
    )
    
    if selected_topic:
        st.sidebar.markdown(f"**Ask BintaBot about: {selected_topic}**")
        st.sidebar.markdown("Type your question in the chat below!")

def initialize_chat_session():
    """Initialize chat session with memory"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "daily_proverb" not in st.session_state:
        st.session_state.daily_proverb = get_daily_proverb()
    
    if "did_you_know" not in st.session_state:
        st.session_state.did_you_know = get_did_you_know_fact()

def add_to_chat_history(user_input, response):
    """Add conversation to chat history"""
    st.session_state.chat_history.append({
        "user": user_input,
        "bintabot": response,
        "timestamp": time.time()
    })
    
    # Keep only last 10 conversations to manage memory
    if len(st.session_state.chat_history) > 10:
        st.session_state.chat_history = st.session_state.chat_history[-10:] 