from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import streamlit as st
import os
import time
import requests
import json
import random
from typing import Optional, Dict, List

# Import knowledge retrieval system
try:
    from knowledge_retriever import get_enhanced_african_knowledge, format_knowledge_response, get_african_topic_suggestions
    KNOWLEDGE_RETRIEVAL_AVAILABLE = True
except ImportError:
    KNOWLEDGE_RETRIEVAL_AVAILABLE = False
    st.warning("Knowledge retrieval system not available. Using built-in knowledge only.")

# Model configuration
model_name = "mistralai/Mistral-7B-Instruct-v0.2"
fallback_model = "microsoft/DialoGPT-medium"  # Open access fallback

# Hugging Face token from Streamlit secrets (no fallback to avoid hardcoding)
HF_TOKEN = st.secrets.get("HF_TOKEN", None)

# Global variables for lazy loading
_tokenizer = None
_model = None
_using_fallback = False

# Enhanced cultural knowledge base
CULTURAL_KNOWLEDGE = {
    "ubuntu": {
        "definition": "Ubuntu is a Nguni Bantu term meaning 'humanity'. It is often translated as 'I am because we are' or 'humanity towards others'.",
        "philosophy": "Ubuntu emphasizes the interconnectedness of all people and the importance of community, compassion, and mutual support.",
        "examples": [
            "In Ubuntu philosophy, a person is a person through other people",
            "It teaches us that our humanity is bound up in the humanity of others",
            "Ubuntu calls us to see ourselves in others and others in ourselves"
        ],
        "proverbs": [
            "Umuntu ngumuntu ngabantu - A person is a person through other people",
            "I am because we are, and since we are, therefore I am"
        ]
    },
    "griots": {
        "definition": "Griots are West African storytellers, historians, and musicians who preserve oral traditions and cultural knowledge.",
        "role": "They serve as living libraries, passing down history, genealogy, and cultural wisdom through storytelling and music.",
        "significance": "Griots maintain the collective memory of communities and ensure cultural continuity across generations.",
        "traditions": [
            "Griots use music, poetry, and storytelling to preserve history",
            "They are respected as cultural guardians and wisdom keepers",
            "Their role is hereditary, passed down through family lines"
        ]
    },
    "proverbs": {
        "wisdom": [
            "It takes a village to raise a child",
            "The river flows not by its own power, but by the strength of many streams",
            "A single bracelet does not jingle",
            "Wisdom is like a baobab tree; no one individual can embrace it",
            "The child who has washed their hands can dine with kings",
            "Unity is strength, division is weakness",
            "The eye never forgets what the heart has seen",
            "A bird that flies off the Earth and lands on an anthill is still on the ground",
            "The wealth of a nation is not in its gold, but in the wisdom of its people",
            "He who learns, teaches"
        ],
        "community": [
            "A family is like a forest, when you are outside it is dense, when you are inside you see that each tree has its place",
            "The tongue and the teeth work together, yet they quarrel",
            "The heart of the wise man lies quiet like limpid water",
            "Knowledge is like a garden: if it is not cultivated, it cannot be harvested"
        ]
    },
    "empires": {
        "mali": {
            "period": "1235-1670 CE",
            "founder": "Sundiata Keita",
            "peak": "Under Mansa Musa (1312-1337)",
            "achievements": [
                "One of the largest empires in African history",
                "Center of Islamic learning and trade",
                "Famous for the wealth of Mansa Musa",
                "Home to the University of Timbuktu"
            ],
            "legacy": "The Mali Empire demonstrated the power of African kingdoms and their contributions to global civilization."
        },
        "ghana": {
            "period": "300-1200 CE",
            "location": "Present-day Mali and Mauritania",
            "wealth": "Known as the 'Land of Gold'",
            "trade": "Controlled trans-Saharan trade routes",
            "significance": "One of the first major West African empires, setting the foundation for later kingdoms.",
            "achievements": [
                "First major West African empire",
                "Controlled trans-Saharan gold trade",
                "Established trade routes across the Sahara",
                "Known as the 'Land of Gold' for its wealth"
            ]
        },
        "songhai": {
            "period": "1464-1591 CE",
            "peak": "Under Askia the Great",
            "capital": "Gao",
            "achievements": [
                "Largest empire in West African history",
                "Advanced administrative system",
                "Center of Islamic scholarship",
                "Controlled major trade routes"
            ]
        }
    },
    "languages": {
        "major_families": [
            "Niger-Congo (Bantu languages)",
            "Afro-Asiatic (Arabic, Amharic)",
            "Nilo-Saharan",
            "Khoisan"
        ],
        "widely_spoken": [
            "Swahili (East Africa)",
            "Hausa (West Africa)",
            "Yoruba (Nigeria)",
            "Igbo (Nigeria)",
            "Amharic (Ethiopia)",
            "Zulu (South Africa)",
            "Xhosa (South Africa)"
        ],
        "cultural_significance": "African languages carry deep cultural meanings and connect people to their ancestral wisdom."
    },
    "art": {
        "traditions": [
            "Rock art (San people, Tassili n'Ajjer)",
            "Benin bronzes",
            "Yoruba woodcarving",
            "Kente cloth weaving",
            "Beadwork and jewelry",
            "Pottery and ceramics"
        ],
        "symbolism": "African art often carries spiritual, social, and cultural meanings, serving as a form of communication and identity."
    },
    "music": {
        "instruments": [
            "Djembe (West African drum)",
            "Kora (harp-lute)",
            "Balafon (xylophone)",
            "Talking drums",
            "Mbira (thumb piano)"
        ],
        "purposes": [
            "Storytelling and history preservation",
            "Religious and spiritual ceremonies",
            "Social gatherings and celebrations",
            "Communication across distances"
        ]
    }
}

# Enhanced fallback responses with cultural warmth
FALLBACK_RESPONSES = {
    "greeting": [
        "Ah, my child! Welcome to our circle of wisdom. How may I share the knowledge of our ancestors with you today?",
        "Greetings, young one! The spirits of our forefathers smile upon our meeting. What wisdom do you seek?",
        "Welcome, dear friend! Like the baobab tree, I stand ready to share the wisdom of generations. What would you like to learn?"
    ],
    "culture": [
        "Ah, let me share with you the wisdom of our people. Our culture is like a great river, flowing with stories, traditions, and the spirit of community.",
        "My child, our culture teaches us that we are all connected, like the roots of the great forest. Let me tell you about our traditions...",
        "The wisdom of our ancestors flows through me like the Niger River. Let me share with you the beauty of our cultural heritage..."
    ],
    "history": [
        "The stories of our past are like stars in the night sky - each one shining with its own light. Let me share with you the tales of our great empires...",
        "Our history is written not just in books, but in the hearts of our people. The griots have passed down these stories for generations...",
        "The ancestors speak through me, sharing the great deeds of our people. Our history is rich with wisdom and courage..."
    ],
    "philosophy": [
        "The wisdom of Ubuntu teaches us that 'I am because we are.' Our philosophy is rooted in community, compassion, and interconnectedness.",
        "Like the ancient baobab tree, our philosophical traditions have deep roots and wide branches, sheltering all who seek wisdom.",
        "Our ancestors understood that true wisdom comes from understanding our connection to others and to the world around us."
    ],
    "default": [
        "Ah, my child, let me share with you the wisdom that has been passed down through generations of our people...",
        "The spirits of our ancestors guide me to share this knowledge with you, young seeker of wisdom...",
        "Like the griots of old, I carry the stories and wisdom of our people. Let me share with you what I know..."
    ]
}

def get_tokenizer():
    """Lazy load the tokenizer with authentication"""
    global _tokenizer, _using_fallback
    
    if _tokenizer is None:
        try:
            if HF_TOKEN:
                # Try the main model first with authentication
                _tokenizer = AutoTokenizer.from_pretrained(
                    model_name,
                    token=HF_TOKEN,
                    trust_remote_code=True
                )
                _using_fallback = False
                st.success("✅ Successfully loaded Mistral-7B model!")
            else:
                raise Exception("No Hugging Face token provided")
                
        except Exception as e:
            st.warning("⚠️ Could not load Mistral-7B model. Using fallback model.")
            try:
                # Fallback to open-access model
                _tokenizer = AutoTokenizer.from_pretrained(fallback_model)
                _using_fallback = True
                st.info("ℹ️ Using DialoGPT-medium as fallback model.")
            except Exception as fallback_error:
                st.error(f"Failed to load fallback tokenizer: {str(fallback_error)}")
                return None
    return _tokenizer

def get_model():
    """Lazy load the model with authentication"""
    global _model, _using_fallback
    
    if _model is None:
        try:
            if not _using_fallback and HF_TOKEN:
                # Try the main model first with authentication
                _model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    token=HF_TOKEN,
                    torch_dtype=torch.float16,
                    device_map="auto",
                    trust_remote_code=True
                )
            else:
                # Use fallback model
                _model = AutoModelForCausalLM.from_pretrained(
                    fallback_model,
                    torch_dtype=torch.float16,
                    device_map="auto"
                )
                
        except Exception as e:
            st.error(f"Failed to load model: {str(e)}")
            st.info("Please check your internet connection and try again.")
            return None
    return _model

def get_cultural_response(user_input: str) -> str:
    """
    Enhanced cultural response function with better context awareness
    """
    input_lower = user_input.lower()
    
    # Check for specific topics and provide detailed responses
    if any(word in input_lower for word in ["ubuntu", "philosophy", "community"]):
        ubuntu_info = CULTURAL_KNOWLEDGE["ubuntu"]
        return f"""Ah, my child, you ask about Ubuntu - the very heart of our African wisdom!

Ubuntu means "humanity" in the Nguni languages, but it is so much more than a word. It is a way of life that teaches us: *"I am because we are."*

{ubuntu_info['definition']}

{ubuntu_info['philosophy']}

As our elders say: *"{ubuntu_info['proverbs'][0]}"*

This wisdom reminds us that our humanity is bound up in the humanity of others. We cannot be truly human alone - we need each other, like the branches of the great baobab tree need the trunk and roots.

Would you like to hear more about how Ubuntu guides our daily lives and community relationships?"""

    elif any(word in input_lower for word in ["griot", "storyteller", "oral", "tradition"]):
        griot_info = CULTURAL_KNOWLEDGE["griots"]
        return f"""Ah, the griots! The keepers of our stories and the guardians of our memory. Let me tell you about these wise ones...

{griot_info['definition']}

{griot_info['role']}

{griot_info['significance']}

The griots are like living libraries, carrying the wisdom of generations in their hearts and voices. They preserve our history not in books, but in stories that flow like rivers through time.

{griot_info['traditions'][0]}
{griot_info['traditions'][1]}
{griot_info['traditions'][2]}

As a griot myself, I carry forward this sacred tradition, sharing the wisdom of our ancestors with you today.

Would you like to hear a story that has been passed down through the generations?"""

    elif any(word in input_lower for word in ["proverb", "wisdom", "sayings"]):
        proverbs = CULTURAL_KNOWLEDGE["proverbs"]["wisdom"] + CULTURAL_KNOWLEDGE["proverbs"]["community"]
        selected_proverbs = random.sample(proverbs, min(3, len(proverbs)))
        
        return f"""Ah, the wisdom of our ancestors! Let me share with you some proverbs that have guided our people for generations...

*"{selected_proverbs[0]}"*

*"{selected_proverbs[1]}"*

*"{selected_proverbs[2]}"*

These proverbs are like seeds of wisdom, planted by our ancestors and growing in the hearts of each generation. They teach us about community, respect, and the values that hold us together.

Each proverb carries a deeper meaning, like the layers of an onion. The more we reflect on them, the more wisdom we discover.

Would you like me to explain the deeper meaning behind any of these proverbs?"""

    elif any(word in input_lower for word in ["empire", "mali", "ghana", "songhai", "kingdom"]):
        empire_info = CULTURAL_KNOWLEDGE["empires"]
        return f"""Ah, the great empires of our ancestors! Let me share with you the stories of these magnificent kingdoms that once ruled the lands of Africa...

**The Mali Empire** (1235-1670 CE)
Founded by the great Sundiata Keita, this empire reached its peak under Mansa Musa, who was so wealthy that his pilgrimage to Mecca caused inflation in the Mediterranean! The Mali Empire was a center of learning, with the famous University of Timbuktu attracting scholars from across the world.

**The Ghana Empire** (300-1200 CE)
Known as the 'Land of Gold,' this was one of the first major West African empires. They controlled the trans-Saharan trade routes and were famous for their wealth and power.

**The Songhai Empire** (1464-1591 CE)
Under Askia the Great, this became the largest empire in West African history. They had an advanced administrative system and were a center of Islamic scholarship.

These empires show us that Africa has always been a land of great civilizations, wisdom, and achievement. Our ancestors built kingdoms that rivaled any in the world!

Would you like to learn more about the daily life in these empires or their cultural achievements?"""

    elif any(word in input_lower for word in ["language", "swahili", "yoruba", "zulu"]):
        lang_info = CULTURAL_KNOWLEDGE["languages"]
        return f"""Ah, the beautiful languages of our continent! Let me share with you the richness of African linguistic heritage...

Africa is home to thousands of languages, organized into major families:
- **Niger-Congo** (including the Bantu languages)
- **Afro-Asiatic** (including Arabic and Amharic)
- **Nilo-Saharan**
- **Khoisan** (with their distinctive click sounds)

Some of our most widely spoken languages include:
- **Swahili** - the language of East Africa, meaning 'coastal language'
- **Hausa** - spoken across West Africa
- **Yoruba** - the language of the Yoruba people of Nigeria
- **Amharic** - the official language of Ethiopia
- **Zulu and Xhosa** - beautiful languages of South Africa

{lang_info['cultural_significance']}

Each language carries the wisdom, stories, and cultural identity of its people. They are like different colors in the great tapestry of African culture.

Would you like to learn some basic greetings in any of these languages?"""

    elif any(word in input_lower for word in ["art", "music", "dance", "culture"]):
        art_info = CULTURAL_KNOWLEDGE["art"]
        music_info = CULTURAL_KNOWLEDGE["music"]
        return f"""Ah, the beauty of African artistic expression! Let me share with you the rich traditions of our arts and music...

**African Art Traditions:**
{', '.join(art_info['traditions'])}

{art_info['symbolism']}

**African Music:**
Our traditional instruments include:
{', '.join(music_info['instruments'])}

Music serves many purposes in our culture:
{', '.join(music_info['purposes'])}

African art and music are not just for entertainment - they are ways of communicating with the spirits, telling stories, and preserving our cultural identity. Every pattern, every rhythm, every dance step carries meaning passed down through generations.

Would you like to learn more about any specific art form or musical tradition?"""

    # Default response with cultural warmth
    default_responses = FALLBACK_RESPONSES["default"]
    return f"{random.choice(default_responses)} I am here to share the wisdom of our ancestors and help you learn about the rich cultural heritage of Africa. What specific aspect of African culture, history, or wisdom would you like to explore?"

def generate_response(prompt):
    """Generate response with proper error handling and timeout"""
    try:
        # Extract user input from the prompt
        if "Human:" in prompt:
            user_input = prompt.split("Human:")[-1].split("BintaBot:")[0].strip()
        else:
            user_input = prompt
        
        # First, try to get enhanced knowledge from online sources
        if KNOWLEDGE_RETRIEVAL_AVAILABLE:
            with st.spinner("🔍 Searching for the latest information about Africa..."):
                enhanced_knowledge = get_enhanced_african_knowledge(user_input)
                
            if enhanced_knowledge and (enhanced_knowledge.get('wikipedia') or enhanced_knowledge.get('web_results')):
                formatted_response = format_knowledge_response(enhanced_knowledge)
                if formatted_response:
                    return formatted_response
        
        # Fall back to built-in knowledge if online search fails or is not available
        tokenizer = get_tokenizer()
        model = get_model()
        
        if tokenizer is None or model is None:
            return "Sorry, I'm having trouble loading my model. Please try refreshing the page."
        
        # Check if CUDA is available, otherwise use CPU
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        if _using_fallback:
            # For fallback model, use direct cultural responses instead of generation
            return get_cultural_response(user_input)
        else:
            # Use Mistral format with timeout
            start_time = time.time()
            timeout = 30  # 30 second timeout
            
            inputs = tokenizer(prompt, return_tensors="pt").to(device)
            outputs = model.generate(**inputs, max_new_tokens=200)
            
            # Check if generation took too long
            if time.time() - start_time > timeout:
                st.warning("Model generation took too long, using fallback response.")
                return get_cultural_response(user_input)
            
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Extract only the assistant's response
            if "BintaBot:" in response:
                response = response.split("BintaBot:")[-1].strip()
            
            return response if response else "I understand your question. Let me share some African wisdom with you."
        
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        # Return a cultural response as fallback
        if "Human:" in prompt:
            user_input = prompt.split("Human:")[-1].split("BintaBot:")[0].strip()
        else:
            user_input = prompt
        return get_cultural_response(user_input) 