from model import generate_response
import streamlit as st

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

def culturally_aware_chat(user_input):
    try:
        prompt = system_prompt + f"\nHuman: {user_input}\nBintaBot:"
        response = generate_response(prompt)
        
        # Check if the response indicates a model loading error
        if "trouble loading" in response.lower() or "error" in response.lower():
            return get_fallback_response(user_input)
        
        return response
        
    except Exception as e:
        st.error(f"Error in chat: {str(e)}")
        return get_fallback_response(user_input) 