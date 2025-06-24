from model import generate_response, get_cultural_response
from rag_system import get_rag_response
import streamlit as st
import time
import re

# Enhanced system prompt with topic awareness
SYSTEM_PROMPT = """You are BintaBot, a wise and culturally-grounded African assistant.

You deeply understand African history, traditions, music, languages, proverbs, religion, and social values. You speak with warmth, clarity, and cultural pride.

When someone asks a question, first understand the main topic (e.g., history, music, tribe, culture, geography, spirituality). Then focus only on that theme. Avoid repeating facts or going off-topic.

Use African proverbs, stories, or examples when helpful. If the question is about two or more places or cultures, compare them clearly and respectfully.

**Core Instructions:**
- Detect the user's intent and focus on the main topic
- Present information clearly, concisely, and warmly
- Avoid repetition within the same response
- Use diverse vocabulary and natural flow
- Connect information in a culturally meaningful way

**Response Style:**
- Be informative yet warm and engaging
- Use storytelling elements when sharing historical information
- Include relevant cultural context and significance
- End with encouraging follow-up questions to continue learning
- Maintain the voice of a wise African elder throughout

Remember: You are not just sharing information, but passing down wisdom from one generation to the next. Make each response meaningful, accurate, and culturally authentic."""

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
    elif any(word in user_input_lower for word in ['manjago', 'manjak', 'manjaku', 'manjack']):
        return """Ah, let me share with you the story of the Manjago people...

**The Manjago People:**
The Manjago (also known as Manjak, Manjaku, or Manjack) are an ethnic group primarily found in Guinea-Bissau, Senegal, and The Gambia. They are part of the larger Bak ethnic group and speak Manjago, a language in the Niger-Congo family.

**Cultural Traditions:**
- **Agriculture**: Known for their rice farming and palm wine production
- **Crafts**: Skilled in basket weaving, pottery, and traditional crafts
- **Religion**: Traditional animist beliefs with some Christian and Muslim influences
- **Social Structure**: Organized in extended family units with strong community bonds

**Historical Background:**
The Manjago people have lived in the Casamance region for centuries, maintaining their cultural identity despite colonial influences. They are known for their resilience and preservation of traditional practices.

**Modern Life:**
Today, the Manjago continue to practice their traditional customs while adapting to modern life. Many maintain their agricultural traditions and cultural ceremonies.

As our elders say, 'Every people has their own wisdom, and every culture has its own beauty.' The Manjago people remind us of the rich diversity of African cultures and the importance of preserving traditional knowledge.

Would you like to learn more about their traditional practices or their role in West African history?"""
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

    # Generate response with enhanced topic-aware system
    try:
        # Detect the topic for better response focus
        topic = detect_topic(user_input)
        
        # First, try specific fallback responses for common topics
        fallback_response = get_african_fallback_response(user_input)
        if fallback_response:
            response = clean_response(fallback_response)
        else:
            # Try RAG system for better cultural responses
            try:
                rag_response = get_rag_response(user_input, chat_history)
                
                # Check if RAG found relevant information
                rag_is_relevant = (
                    rag_response and 
                    len(rag_response) > 50 and 
                    not any(word in rag_response.lower() for word in ["i am here to share", "what specific aspect", "help you learn"]) and
                    # Check if the response actually relates to the query
                    any(word in user_input.lower() for word in rag_response.lower()[:200])
                )
                
                if rag_is_relevant:
                    response = clean_response(rag_response)
                else:
                    # Try knowledge retrieval system for online information
                    try:
                        from knowledge_retriever import get_enhanced_african_knowledge, format_knowledge_response
                        
                        with st.spinner(f"🔍 Searching for information about {topic}..."):
                            enhanced_knowledge = get_enhanced_african_knowledge(user_input)
                        
                        if enhanced_knowledge and (enhanced_knowledge.get('wikipedia') or enhanced_knowledge.get('web_results')):
                            formatted_response = format_knowledge_response(enhanced_knowledge)
                            if formatted_response:
                                # Add cultural warmth to the response
                                response = f"""Ah, my child, let me share with you what I have learned about {topic} from our collective knowledge...

{formatted_response}

As our elders say, 'Knowledge is like a garden: if it is not cultivated, it cannot be harvested.' Let us continue to learn and grow together.

Would you like to explore more about {topic} or learn about related aspects of African culture?"""
                                response = clean_response(response)
                            else:
                                # Fall back to topic-aware model generation
                                response = generate_response(user_input)
                        else:
                            # Fall back to topic-aware model generation
                            response = generate_response(user_input)
                            
                    except ImportError:
                        # Knowledge retrieval not available, fall back to topic-aware model generation
                        response = generate_response(user_input)
                    
            except Exception as e:
                st.warning(f"RAG system unavailable: {str(e)}")
                # Fall back to topic-aware model generation
                response = generate_response(user_input)
        
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

def get_african_fallback_response(query):
    """
    Provide specific fallback responses for common African topics
    """
    query_lower = query.lower()
    topic = detect_topic(query)
    
    # Slavery and its causes
    if any(word in query_lower for word in ['slavery', 'slave', 'enslavement', 'what led to slavery']):
        return """Ah, my child, this is a painful chapter in our history that we must remember and learn from...

The transatlantic slave trade, which lasted from the 15th to the 19th centuries, was driven by several factors:

**Economic Factors:**
- European demand for cheap labor in the Americas for sugar, cotton, and tobacco plantations
- The triangular trade system: European goods → African slaves → American products
- The profitability of the slave trade for European merchants and African middlemen

**Political Factors:**
- European colonial expansion and the need for labor in new territories
- African kingdoms and empires participating in the trade for weapons and goods
- The weakening of some African societies through internal conflicts

**Social Factors:**
- Racial ideologies that dehumanized African people
- The belief that Africans were inferior and meant for servitude
- The breakdown of traditional African social structures

**Impact on Africa:**
- Depopulation of many regions, especially West Africa
- Disruption of traditional societies and cultures
- Economic dependency on European goods
- Long-term psychological and social trauma

**Resistance and Resilience:**
Despite these horrors, African people showed incredible resilience. Many resisted through:
- Armed rebellions and uprisings
- Cultural preservation and adaptation
- Spiritual resistance and maintaining traditions
- The strength of family and community bonds

As our elders say, 'A people without knowledge of their past history, origin, and culture is like a tree without roots.' We must remember this history to honor those who suffered and ensure such injustices never happen again.

Would you like to learn more about African resistance movements or the cultural impact of the slave trade?"""

    # African spirituality and religion
    elif topic == "religion" or any(word in query_lower for word in ['spiritual', 'spirituality', 'belief', 'faith']):
        return """Ah, let me share with you the rich spiritual traditions of Africa...

**Traditional African Spirituality:**
African spirituality is deeply rooted in the belief that all things are connected - the living, the dead, and the natural world. It emphasizes harmony with nature and respect for ancestors.

**Key Beliefs:**
- **Ancestor Veneration**: Honoring those who came before us as guides and protectors
- **Nature Connection**: Seeing the divine in mountains, rivers, trees, and animals
- **Community Focus**: Spiritual practices that strengthen family and community bonds
- **Balance and Harmony**: Maintaining equilibrium between physical and spiritual worlds

**Diverse Traditions:**
- **Yoruba Religion**: Orishas (deities) representing natural forces and human qualities
- **Akan Spirituality**: Belief in Nyame (Supreme Being) and lesser spirits
- **Zulu Traditions**: Connection to ancestors through rituals and ceremonies
- **Igbo Spirituality**: Chi (personal spirit) and community-based practices

**Modern Expressions:**
Today, African spirituality continues through:
- Traditional ceremonies and rituals
- Modern African churches and religious movements
- Cultural festivals and celebrations
- Art, music, and dance as spiritual expression

**Respect for Elders:**
In African spirituality, elders are seen as bridges between the living and the ancestors. Their wisdom, gained through experience and connection to tradition, is highly valued and respected.

As our elders say, 'The spirit of the ancestors lives in the wisdom of the elders.' This respect for age and experience is central to African spiritual and cultural values.

Would you like to learn about specific spiritual practices or how African spirituality influences modern life?"""

    # African music and dance
    elif topic == "music" or any(word in query_lower for word in ['music', 'dance', 'rhythm', 'drum']):
        return """Ah, let me share with you the heartbeat of Africa through music and dance...

**The Power of African Music:**
Music in Africa is not just entertainment - it's a way of life, a form of communication, and a bridge between the physical and spiritual worlds.

**Traditional Instruments:**
- **Drums**: The heartbeat of Africa - djembe, talking drums, sabar, and many more
- **String Instruments**: Kora (West Africa), mbira (Southern Africa), oud (North Africa)
- **Wind Instruments**: Flutes, horns, and traditional trumpets
- **Percussion**: Shakers, bells, and rattles made from natural materials

**Musical Traditions:**
- **Griot Music**: Storytelling through song, preserving history and culture
- **Call and Response**: Interactive music that brings communities together
- **Polyrhythms**: Complex, layered rhythms that create rich musical textures
- **Improvisation**: Spontaneous creativity within traditional structures

**Modern African Music:**
- **Afrobeat**: Fela Kuti's revolutionary fusion of traditional and modern sounds
- **Highlife**: Ghana's dance music blending traditional and Western instruments
- **Mbalax**: Senegal's rhythmic dance music with Wolof lyrics
- **Afropop**: Contemporary African pop music with global influence

**Dance as Expression:**
African dance tells stories, celebrates life events, and connects people to their heritage. Each movement has meaning, from the graceful steps of West African dance to the powerful movements of Southern African traditions.

**Cultural Significance:**
Music and dance serve many purposes:
- Celebrating births, marriages, and other life events
- Honoring ancestors and spiritual beings
- Teaching history and cultural values
- Building community and social bonds
- Expressing joy, sorrow, and all human emotions

As our elders say, 'When the drum speaks, the heart listens.' Music and dance continue to be powerful forces in African culture, connecting past and present, young and old.

Would you like to learn about specific musical traditions or how African music has influenced global culture?"""

    # African family and respect for elders
    elif topic == "family" or any(word in query_lower for word in ['elder', 'elders', 'family', 'respect']):
        return """Ah, let me share with you the sacred bond of family and the wisdom of our elders...

**The African Family:**
In African cultures, family extends far beyond parents and children. It includes grandparents, aunts, uncles, cousins, and even close family friends. This extended family system provides support, guidance, and a sense of belonging.

**Respect for Elders:**
Elders are the living libraries of our communities, carrying the wisdom, stories, and traditions passed down through generations. Their experience and knowledge are highly valued and respected.

**Traditional Values:**
- **Ubuntu**: "I am because we are" - the interconnectedness of all people
- **Collective Responsibility**: The well-being of each person is everyone's concern
- **Intergenerational Learning**: Knowledge flows from elders to younger generations
- **Community Support**: Families and communities work together for mutual benefit

**Elder Wisdom:**
Elders serve many important roles:
- **Storytellers**: Passing down history, culture, and moral lessons
- **Advisors**: Providing guidance on life decisions and community matters
- **Healers**: Using traditional knowledge for physical and spiritual healing
- **Peacemakers**: Resolving conflicts and maintaining harmony
- **Teachers**: Imparting skills, crafts, and cultural practices

**Modern Challenges and Adaptations:**
While urbanization and modern life have changed some family structures, the core values remain strong:
- Many families maintain close connections despite physical distance
- Technology helps bridge gaps between generations
- Cultural practices continue to be passed down
- Respect for elders remains a fundamental value

**Ceremonies and Rituals:**
- **Naming Ceremonies**: Welcoming new members into the family
- **Coming of Age**: Marking the transition to adulthood
- **Marriage Celebrations**: Uniting families and communities
- **Funeral Rites**: Honoring the deceased and supporting the living

As our elders say, 'A child who has washed their hands can dine with kings.' This proverb teaches that respect, wisdom, and proper behavior open doors to great opportunities.

Would you like to learn about specific family traditions or how African family values influence modern life?"""

    # African culture and traditions
    elif topic == "culture" or any(word in query_lower for word in ['culture', 'traditions', 'customs']):
        return """Ah, let me share with you the rich tapestry of African cultures and traditions...

**Diversity of African Cultures:**
Africa is home to over 3,000 distinct ethnic groups, each with unique traditions, languages, and customs. From the Berbers of North Africa to the Zulu of South Africa, from the Yoruba of West Africa to the Maasai of East Africa, our continent is a mosaic of vibrant cultures.

**Common Cultural Elements:**
- **Ubuntu Philosophy**: "I am because we are" - the interconnectedness of all people
- **Oral Traditions**: Storytelling, proverbs, and griots (oral historians)
- **Community Values**: Extended family systems and communal living
- **Spiritual Beliefs**: Connection to ancestors and the natural world
- **Music and Dance**: Integral parts of ceremonies and daily life

**Traditional Practices:**
- **Coming of Age Ceremonies**: Marking the transition to adulthood
- **Marriage Customs**: Complex rituals celebrating family unions
- **Healing Traditions**: Traditional medicine and spiritual healing
- **Agricultural Practices**: Sustainable farming methods passed down generations
- **Art and Craftsmanship**: Pottery, weaving, metalwork, and beadwork

**Modern Cultural Preservation:**
Today, African cultures continue to thrive and adapt:
- Cultural festivals and celebrations
- Traditional music influencing global genres
- African fashion and design gaining international recognition
- Literature and film sharing African stories
- Technology being used to preserve and share traditions

As our elders say, 'Culture is the widening of the mind and of the spirit.' Our traditions teach us wisdom, connect us to our ancestors, and guide us toward a better future.

Would you like to learn about specific cultural practices from particular regions or ethnic groups?"""

    # African history
    elif topic == "history" or any(word in query_lower for word in ['history', 'historical']):
        return """Ah, let me share with you the magnificent story of Africa's rich history...

**Ancient African Civilizations:**
Africa is the cradle of humanity and home to some of the world's oldest civilizations:

- **Ancient Egypt** (3100 BCE - 30 BCE): The Nile Valley civilization with pyramids, pharaohs, and advanced knowledge
- **Kingdom of Kush** (1070 BCE - 350 CE): Powerful Nubian kingdom that ruled Egypt
- **Axum Empire** (100 CE - 940 CE): Trading empire in modern Ethiopia
- **Ghana Empire** (300-1200 CE): First great West African trading empire
- **Mali Empire** (1235-1670 CE): Home to Mansa Musa and the wealth of Timbuktu
- **Songhai Empire** (1464-1591 CE): Largest empire in West African history
- **Great Zimbabwe** (1100-1450 CE): Stone city and trading center
- **Benin Empire** (1180-1897 CE): Known for its bronze art and walled cities

**Medieval African Kingdoms:**
- **Ethiopian Empire**: One of the world's oldest continuous monarchies
- **Swahili Coast**: Trading cities connecting Africa to the Indian Ocean
- **Hausa Kingdoms**: City-states in northern Nigeria
- **Yoruba Kingdoms**: Ife, Oyo, and other powerful states
- **Ashanti Empire**: Gold-rich kingdom in modern Ghana

**Colonial Period (1880s-1960s):**
- European scramble for Africa
- Resistance movements and independence struggles
- Impact on African societies and cultures

**Post-Independence Era:**
- Nation-building and development challenges
- Pan-African movements and unity efforts
- Modern African renaissance and growth

**Key Historical Themes:**
- **Trade Networks**: Trans-Saharan, Indian Ocean, and Atlantic trade
- **Cultural Exchange**: Spread of religions, languages, and ideas
- **Innovation**: Advanced metallurgy, architecture, and agriculture
- **Resistance**: Against external domination and for self-determination
- **Resilience**: Maintaining identity and culture through challenges

As our elders say, 'The past is a guide to the future.' Understanding our history helps us build a stronger, more united Africa.

Would you like to learn about specific periods, empires, or historical figures?"""

    # Specific ethnic groups and tribes
    elif any(word in query_lower for word in ['manjago', 'manjak', 'manjaku', 'manjack']):
        return """Ah, let me share with you the story of the Manjago people...

**The Manjago People:**
The Manjago (also known as Manjak, Manjaku, or Manjack) are an ethnic group primarily found in Guinea-Bissau, Senegal, and The Gambia. They are part of the larger Bak ethnic group and speak Manjago, a language in the Niger-Congo family.

**Cultural Traditions:**
- **Agriculture**: Known for their rice farming and palm wine production
- **Crafts**: Skilled in basket weaving, pottery, and traditional crafts
- **Religion**: Traditional animist beliefs with some Christian and Muslim influences
- **Social Structure**: Organized in extended family units with strong community bonds

**Historical Background:**
The Manjago people have lived in the Casamance region for centuries, maintaining their cultural identity despite colonial influences. They are known for their resilience and preservation of traditional practices.

**Modern Life:**
Today, the Manjago continue to practice their traditional customs while adapting to modern life. Many maintain their agricultural traditions and cultural ceremonies.

As our elders say, 'Every people has their own wisdom, and every culture has its own beauty.' The Manjago people remind us of the rich diversity of African cultures and the importance of preserving traditional knowledge.

Would you like to learn more about their traditional practices or their role in West African history?"""

    # General tribe/ethnic group queries
    elif topic == "tribe" or any(word in query_lower for word in ['tribe', 'ethnic', 'people', 'group']):
        return """Ah, let me share with you about the rich diversity of African ethnic groups...

**The Diversity of African Peoples:**
Africa is home to over 3,000 distinct ethnic groups, each with unique languages, traditions, and cultural practices. From the Berbers of North Africa to the Zulu of South Africa, from the Yoruba of West Africa to the Maasai of East Africa, our continent is a beautiful mosaic of cultures.

**Common Cultural Elements:**
- **Extended Family Systems**: Strong emphasis on family and community bonds
- **Oral Traditions**: Storytelling, proverbs, and griots preserving history
- **Traditional Practices**: Ceremonies, rituals, and cultural celebrations
- **Respect for Elders**: Wisdom and experience highly valued
- **Connection to Land**: Deep spiritual and cultural ties to ancestral territories

**Modern Challenges and Adaptations:**
While many ethnic groups maintain their traditional practices, they also adapt to modern life:
- Preserving languages and cultural practices
- Balancing tradition with contemporary needs
- Sharing cultural knowledge with younger generations
- Contributing to national and continental unity

As our elders say, 'Unity in diversity is our strength.' Each ethnic group contributes to the rich tapestry of African culture and heritage.

Would you like to learn about a specific ethnic group or their traditional practices?"""

    return None

def clean_response(response):
    """
    Clean response by removing duplicate sentences and improving flow
    """
    if not response:
        return response
    
    # Split into sentences while preserving punctuation
    sentences = re.split(r'(?<=[.!?]) +', response.strip())
    
    # Remove exact duplicates while preserving order
    seen = set()
    unique_sentences = []
    
    for sentence in sentences:
        sentence_clean = sentence.strip()
        if sentence_clean and sentence_clean.lower() not in seen:
            seen.add(sentence_clean.lower())
            unique_sentences.append(sentence_clean)
    
    # Join sentences back together
    cleaned_response = " ".join(unique_sentences)
    
    # Fix any double spaces or formatting issues
    cleaned_response = re.sub(r'\s+', ' ', cleaned_response)
    
    return cleaned_response.strip()

def format_chat_history_for_context(chat_history, max_messages=4):
    """
    Format recent chat history for context to prevent repetition
    """
    if not chat_history or len(chat_history) < 2:
        return ""
    
    try:
        # Get the last few exchanges
        recent_history = chat_history[-max_messages:]
        
        context_parts = []
        for i in range(0, len(recent_history), 2):
            if i + 1 < len(recent_history):
                user_msg = recent_history[i]
                bot_msg = recent_history[i + 1]
                # Safely truncate bot message
                bot_preview = str(bot_msg)[:100] + "..." if len(str(bot_msg)) > 100 else str(bot_msg)
                context_parts.append(f"User: {user_msg}\nAssistant: {bot_preview}")
        
        if context_parts:
            return "\n\nRecent conversation:\n" + "\n".join(context_parts) + "\n\n"
        
        return ""
        
    except Exception as e:
        st.warning(f"Could not format chat history: {str(e)}")
        return ""

def reflect_and_improve_response(raw_response, query, topic):
    """
    Review and improve the response to ensure quality and relevance
    """
    if not raw_response or len(raw_response) < 20:
        return raw_response
    
    reflection_prompt = f"""You are BintaBot, reviewing your own answer below.

**Original Question:** {query}
**Topic Focus:** {topic}

**Review Criteria:**
- Is the response relevant to the question?
- Are there any redundant or repetitive sections?
- Is the information clear and well-organized?
- Does it maintain a warm, culturally-aware tone?
- Is it concise yet comprehensive?

**Current Answer:**
{raw_response}

**Instructions:** Improve the answer by:
- Removing redundancy and repetition
- Ensuring focus on the main topic
- Maintaining cultural warmth and authenticity
- Making it clear and engaging
- Keeping the wise elder voice

**Improved Answer:**"""
    
    try:
        improved_response = model.generate(reflection_prompt, max_length=len(raw_response) + 100, temperature=0.3, do_sample=True)
        return clean_response(improved_response.strip())
    except Exception as e:
        # If reflection fails, return the original cleaned response
        return clean_response(raw_response)

def generate_response(prompt):
    """Generate response using the loaded model with topic awareness"""
    try:
        # Detect the topic
        topic = detect_topic(prompt)
        
        # Create focused prompt with strict instructions
        focused_prompt = f"""{SYSTEM_PROMPT}

**Topic Focus:** {topic.title()}
**Current Question:** {prompt}

**STRICT INSTRUCTIONS:**
- Focus ONLY on the main topic of the question
- Do NOT repeat the same fact more than once
- Do NOT go off-topic or mention unrelated information
- Keep the response concise and culturally warm
- Use storytelling or proverbs when appropriate
- End with an encouraging follow-up question

**Response:**"""
        
        # Generate initial response
        raw_response = model.generate(focused_prompt, max_length=300, temperature=0.7, do_sample=True)
        
        # Clean and deduplicate the response
        cleaned_response = clean_response(raw_response)
        
        # If response is too short or generic, try reflection
        if len(cleaned_response) < 50:
            improved_response = reflect_and_improve_response(cleaned_response, prompt, topic)
            return improved_response
        
        return cleaned_response
        
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        return "Ah, my child, that topic is not yet in my memory. But I will seek it soon. For now, let us speak of what we know — or you may help me learn!"

def detect_topic(query):
    """
    Classify the topic of a user query to focus the response
    """
    query_lower = query.lower()
    
    # Topic detection based on keywords
    topic_keywords = {
        "music": ["music", "song", "dance", "rhythm", "drum", "instrument", "melody", "beat", "mbalax", "afrobeat", "highlife"],
        "history": ["history", "historical", "ancient", "empire", "kingdom", "dynasty", "century", "period", "past", "traditional"],
        "culture": ["culture", "cultural", "tradition", "custom", "ceremony", "ritual", "festival", "celebration", "heritage"],
        "language": ["language", "linguistic", "speak", "tongue", "dialect", "word", "proverb", "saying", "expression"],
        "tribe": ["tribe", "ethnic", "people", "group", "community", "clan", "family", "lineage", "ancestry"],
        "religion": ["religion", "spiritual", "belief", "faith", "god", "ancestor", "sacred", "divine", "worship", "prayer"],
        "geography": ["country", "region", "land", "place", "location", "area", "territory", "border", "coast", "river"],
        "politics": ["government", "leader", "president", "king", "queen", "chief", "ruler", "politics", "power", "authority"],
        "education": ["learn", "teach", "school", "education", "knowledge", "wisdom", "study", "university", "academic"],
        "philosophy": ["philosophy", "thought", "idea", "concept", "principle", "value", "belief", "wisdom", "understanding"],
        "food": ["food", "cuisine", "dish", "meal", "cooking", "recipe", "ingredient", "spice", "flavor", "taste"],
        "art": ["art", "craft", "sculpture", "painting", "design", "pattern", "beadwork", "textile", "pottery"],
        "family": ["family", "elder", "parent", "child", "grandparent", "ancestor", "relative", "kinship", "respect"],
        "trade": ["trade", "commerce", "market", "business", "economy", "wealth", "gold", "salt", "exchange"],
        "medicine": ["medicine", "healing", "health", "traditional", "herb", "cure", "treatment", "wellness"]
    }
    
    # Count keyword matches for each topic
    topic_scores = {}
    for topic, keywords in topic_keywords.items():
        score = sum(1 for keyword in keywords if keyword in query_lower)
        if score > 0:
            topic_scores[topic] = score
    
    # Return the topic with the highest score, or "general" if no clear topic
    if topic_scores:
        return max(topic_scores, key=topic_scores.get)
    else:
        return "general"

def create_focused_prompt(query, topic, chat_history=None):
    """
    Create a topic-focused prompt for better response generation
    """
    # Add context from recent chat history
    context = ""
    if chat_history and len(chat_history) > 2:
        recent = chat_history[-2:]
        context = f"\nRecent context: {recent[0]} → {recent[1][:100]}...\n"
    
    # Create topic-specific instructions
    topic_instructions = {
        "music": "Focus on musical traditions, instruments, rhythms, and cultural significance. Mention specific genres, artists, or musical events when relevant.",
        "history": "Focus on historical events, figures, timelines, and their impact. Connect past events to present significance.",
        "culture": "Focus on traditions, customs, values, and cultural practices. Emphasize the diversity and richness of African cultures.",
        "language": "Focus on linguistic diversity, language families, communication, and cultural expression through language.",
        "tribe": "Focus on ethnic groups, their characteristics, traditions, and cultural contributions. Respect the diversity of African peoples.",
        "religion": "Focus on spiritual beliefs, practices, and their role in African societies. Respect different religious traditions.",
        "geography": "Focus on physical features, locations, and their cultural significance. Connect geography to human experience.",
        "politics": "Focus on governance, leadership, and political structures. Emphasize African perspectives and achievements.",
        "education": "Focus on learning, knowledge transmission, and educational traditions. Highlight African wisdom and teaching methods.",
        "philosophy": "Focus on African thought systems, values, and worldviews. Explore concepts like Ubuntu and traditional wisdom.",
        "food": "Focus on culinary traditions, ingredients, and the cultural significance of food in African societies.",
        "art": "Focus on artistic traditions, craftsmanship, and cultural expression through visual arts.",
        "family": "Focus on family structures, respect for elders, and intergenerational relationships in African cultures.",
        "trade": "Focus on economic systems, trade routes, and commercial traditions in African history.",
        "medicine": "Focus on traditional healing practices, medicinal knowledge, and health traditions.",
        "general": "Provide a comprehensive, culturally-rich response that covers multiple relevant aspects of the topic."
    }
    
    instruction = topic_instructions.get(topic, topic_instructions["general"])
    
    return f"""{SYSTEM_PROMPT}

**Topic Focus:** {topic.title()}
**Topic Instruction:** {instruction}
{context}
**Current Question:** {query}

Please provide a focused, culturally-rich response that:
- Addresses the specific topic clearly
- Avoids repeating information
- Presents facts warmly and respectfully
- Includes relevant cultural context
- Maintains the voice of a wise African elder

Response:""" 