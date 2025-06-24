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
    "historical_figures": {
        "sundiata_keita": {
            "name": "Sundiata Keita",
            "title": "Founder of the Mali Empire",
            "period": "1217-1255 CE",
            "achievements": [
                "Founded the Mali Empire in 1235 CE",
                "Unified the Mandinka people",
                "Established the foundation for one of Africa's greatest empires",
                "Known as the 'Lion King' or 'Lion Prince'",
                "Created a strong administrative system",
                "Promoted trade and Islamic learning"
            ],
            "legacy": "Sundiata Keita's leadership and vision created the foundation for the Mali Empire, which would later become one of the wealthiest and most powerful empires in African history under Mansa Musa.",
            "story": "According to oral tradition, Sundiata was born disabled but overcame his challenges to become a great warrior and leader. His story is preserved by griots and teaches us about resilience, leadership, and the power of unity."
        },
        "dawda_jawara": {
            "name": "Sir Dawda Kairaba Jawara",
            "title": "First President of The Gambia",
            "period": "1965-1994",
            "achievements": [
                "Led The Gambia to independence from Britain in 1965",
                "Served as Prime Minister (1962-1970) and President (1970-1994)",
                "Established democratic governance in The Gambia",
                "Promoted education and healthcare",
                "Maintained peaceful relations with neighboring countries",
                "Known for his commitment to democracy and human rights"
            ],
            "legacy": "Sir Dawda Jawara is remembered as the 'Father of The Gambia' for his role in leading the country to independence and establishing democratic institutions. He was known for his gentle leadership style and commitment to peace.",
            "background": "Born in 1924, Jawara was originally trained as a veterinarian before entering politics. He led The Gambia through its transition from British colony to independent nation."
        },
        "mansa_musa": {
            "name": "Mansa Musa",
            "title": "Emperor of the Mali Empire",
            "period": "1312-1337 CE",
            "achievements": [
                "Ruled the Mali Empire at its peak",
                "Conducted the famous Hajj pilgrimage to Mecca",
                "Distributed so much gold that it caused inflation in the Mediterranean",
                "Built the University of Timbuktu",
                "Established Mali as a center of Islamic learning",
                "Expanded the empire's territory and influence"
            ],
            "legacy": "Mansa Musa is considered one of the wealthiest people in history. His pilgrimage to Mecca in 1324 brought Mali to the attention of the world and established its reputation as a land of great wealth and learning.",
            "story": "Mansa Musa's famous pilgrimage included 60,000 people, 12,000 slaves, and so much gold that he gave it away freely, causing the price of gold to drop in the regions he visited."
        },
        "kunta_kinteh": {
            "name": "Kunta Kinteh",
            "title": "Historical figure from The Gambia",
            "period": "18th century",
            "story": "Kunta Kinteh was a young Mandinka man from The Gambia who was captured and enslaved in the 18th century. His story was popularized by Alex Haley's novel 'Roots' and the subsequent TV series. According to the story, Kunta was born in Juffure, a village in The Gambia, and was captured by slave traders while searching for wood to make a drum. He was taken to America where he maintained his cultural identity and passed down his African heritage to his descendants.",
            "significance": "Kunta Kinteh's story represents the resilience of African people during the transatlantic slave trade and the importance of preserving cultural identity. His story has inspired millions to trace their African roots.",
            "legacy": "Kunta Kinteh's legacy lives on through the Kunta Kinteh Island (formerly James Island) in The Gambia, which is now a UNESCO World Heritage site. His story continues to educate people about the horrors of slavery and the strength of African heritage.",
            "cultural_impact": "The story of Kunta Kinteh has become a symbol of African resistance and cultural preservation. It has inspired genealogical research and cultural reconnection for many African Americans."
        }
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
    },
    "ethnic_groups": {
        "mandinka": {
            "name": "Mandinka (Mandingo)",
            "location": "West Africa (Senegal, Gambia, Guinea, Mali, Ivory Coast, Burkina Faso)",
            "population": "Over 11 million people",
            "language": "Mandinka (Mande language family)",
            "culture": [
                "Rich oral tradition with griots as storytellers and historians",
                "Strong emphasis on family and community values",
                "Traditional music with kora, balafon, and djembe",
                "Famous for their epic of Sundiata Keita",
                "Traditional clothing includes colorful robes and headwraps",
                "Agricultural society with rice, millet, and groundnut farming"
            ],
            "history": "The Mandinka people trace their origins to the ancient Mali Empire. They are descendants of the Mandé people who migrated from the Niger River region. The Mandinka played a crucial role in the trans-Saharan trade and the spread of Islam in West Africa.",
            "traditions": [
                "Circumcision ceremonies (Kankurang)",
                "Naming ceremonies with family gatherings",
                "Traditional wrestling (Laamb)",
                "Storytelling sessions with griots",
                "Community decision-making through elders",
                "Traditional medicine and healing practices"
            ],
            "values": [
                "Respect for elders and ancestors",
                "Community solidarity and mutual support",
                "Education and wisdom transmission",
                "Hospitality and generosity",
                "Courage and resilience",
                "Preservation of cultural heritage"
            ],
            "famous_figures": [
                "Sundiata Keita - Founder of the Mali Empire",
                "Mansa Musa - Wealthy emperor of Mali",
                "Toumani Diabaté - Master kora player",
                "Salif Keita - Famous musician"
            ]
        },
        "yoruba": {
            "name": "Yoruba",
            "location": "Southwestern Nigeria, Benin, Togo",
            "population": "Over 40 million people",
            "language": "Yoruba (Niger-Congo family)",
            "culture": [
                "Rich artistic traditions including woodcarving and beadwork",
                "Complex religious system with Orishas",
                "Traditional drumming and dance",
                "Famous for their elaborate festivals",
                "Strong emphasis on education and learning",
                "Traditional medicine and herbal knowledge"
            ],
            "history": "The Yoruba have one of the oldest urban civilizations in Africa, with cities like Ife and Oyo dating back over 1000 years. They developed sophisticated political systems and artistic traditions.",
            "traditions": [
                "Egungun masquerade festivals",
                "Traditional wedding ceremonies",
                "Naming ceremonies (Ikomojade)",
                "Twin celebrations (Ibeji)",
                "Traditional chieftaincy system",
                "Ifa divination system"
            ]
        },
        "zulu": {
            "name": "Zulu",
            "location": "South Africa (KwaZulu-Natal)",
            "population": "Over 12 million people",
            "language": "Zulu (Bantu language family)",
            "culture": [
                "Famous for their warrior traditions",
                "Traditional beadwork and basket weaving",
                "Complex social structure with clans",
                "Traditional music with drums and singing",
                "Famous for their traditional dances",
                "Strong cattle-herding traditions"
            ],
            "history": "The Zulu people emerged as a powerful nation under King Shaka in the early 19th century. They developed sophisticated military tactics and social organization.",
            "traditions": [
                "Traditional wedding ceremonies (Umabo)",
                "Coming-of-age ceremonies",
                "Traditional healing practices",
                "Cattle ceremonies and rituals",
                "Traditional clothing with animal skins",
                "Warrior training and traditions"
            ]
        },
        "fula": {
            "name": "Fula (Fulani)",
            "location": "West Africa (Senegal, Guinea, Mali, Nigeria, Cameroon, Chad)",
            "population": "Over 40 million people",
            "language": "Fula (Niger-Congo family)",
            "culture": [
                "Semi-nomadic pastoralist lifestyle",
                "Famous for their cattle herding traditions",
                "Rich oral literature and poetry",
                "Traditional music with flutes and drums",
                "Elaborate traditional clothing and jewelry",
                "Strong emphasis on education and Islamic learning"
            ],
            "history": "The Fula people are one of the largest ethnic groups in West Africa, known for their nomadic pastoralist traditions. They have played significant roles in the spread of Islam and the establishment of several West African empires.",
            "traditions": [
                "Cattle herding and nomadic lifestyle",
                "Traditional wedding ceremonies",
                "Islamic religious practices",
                "Traditional healing and medicine",
                "Storytelling and oral poetry",
                "Traditional wrestling and sports"
            ],
            "values": [
                "Hospitality and generosity",
                "Respect for elders and ancestors",
                "Strong family and community bonds",
                "Education and Islamic learning",
                "Courage and resilience",
                "Preservation of cultural heritage"
            ],
            "famous_figures": [
                "Usman dan Fodio - Founder of the Sokoto Caliphate",
                "Ahmadu Bello - Premier of Northern Nigeria",
                "Modibo Keita - First President of Mali",
                "Amadou Hampâté Bâ - Famous writer and ethnologist"
            ]
        }
    },
    "countries": {
        "senegal": {
            "name": "Senegal",
            "tribes": [
                "Wolof - Largest ethnic group, known for their language and culture",
                "Fula (Fulani) - Semi-nomadic pastoralists, cattle herders",
                "Serer - Traditional farmers and fishermen",
                "Mandinka - Descendants of the Mali Empire",
                "Diola - Rice farmers from the Casamance region",
                "Tukulor - Islamic scholars and traders",
                "Lebou - Traditional fishermen from the coast",
                "Bambara - Farmers and traders"
            ],
            "languages": [
                "French (official language)",
                "Wolof (most widely spoken)",
                "Fula (Fulani)",
                "Serer",
                "Mandinka",
                "Diola",
                "Arabic (religious language)"
            ],
            "culture": "Senegal is known for its rich cultural diversity, traditional music (Mbalax), wrestling (Laamb), and hospitality (Teranga)."
        },
        "gambia": {
            "name": "The Gambia",
            "tribes": [
                "Mandinka - Largest ethnic group, descendants of Mali Empire",
                "Fula (Fulani) - Cattle herders and traders",
                "Wolof - From Senegal, traders and farmers",
                "Jola - Rice farmers from the south",
                "Serahuli - Traders and merchants",
                "Aku - Descendants of freed slaves"
            ],
            "languages": [
                "English (official language)",
                "Mandinka (most widely spoken)",
                "Fula (Fulani)",
                "Wolof",
                "Jola",
                "Serahuli",
                "Arabic (religious language)"
            ],
            "culture": "The Gambia is known for its peaceful nature, traditional music, and the famous Kunta Kinteh Island (formerly James Island)."
        }
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
                st.success("Successfully loaded Mistral-7B model!")
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
    
    # Check for historical figures first
    if any(word in input_lower for word in ["sundiata", "keita", "sundiata keita"]):
        figure_info = CULTURAL_KNOWLEDGE["historical_figures"]["sundiata_keita"]
        return f"""Ah, Sundiata Keita! Let me share with you the story of this legendary founder of the Mali Empire...

Sundiata Keita was the **{figure_info['title']}** during {figure_info['period']}. 

**Key Achievements:**
{', '.join(figure_info['achievements'])}

**Legacy:**
{figure_info['legacy']}

{figure_info['story']}

Sundiata's story teaches us about resilience, leadership, and the power of unity. Like the great baobab tree, his influence continues to provide shade and wisdom for generations to come.

Would you like to learn more about the Mali Empire that Sundiata founded or the griots who preserve his story?"""

    elif any(word in input_lower for word in ["dawda", "jawara", "dawda jawara", "sir dawda"]):
        figure_info = CULTURAL_KNOWLEDGE["historical_figures"]["dawda_jawara"]
        return f"""Ah, Sir Dawda Kairaba Jawara! Let me share with you the story of this remarkable leader of The Gambia...

Sir Dawda Jawara was the **{figure_info['title']}** during {figure_info['period']}. 

**Key Achievements:**
{', '.join(figure_info['achievements'])}

**Legacy:**
{figure_info['legacy']}

{figure_info['background']}

Sir Dawda Jawara's story teaches us about democratic leadership, peaceful transition, and the importance of education and healthcare for a nation's development.

Would you like to learn more about The Gambia's journey to independence or other African independence leaders?"""

    elif any(word in input_lower for word in ["mansa musa", "mansa"]):
        figure_info = CULTURAL_KNOWLEDGE["historical_figures"]["mansa_musa"]
        return f"""Ah, Mansa Musa! Let me share with you the story of this legendary emperor of the Mali Empire...

Mansa Musa was the **{figure_info['title']}** during {figure_info['period']}. 

**Key Achievements:**
{', '.join(figure_info['achievements'])}

**Legacy:**
{figure_info['legacy']}

{figure_info['story']}

Mansa Musa's story teaches us about the wealth and sophistication of African empires, the importance of education and learning, and the power of cultural exchange.

Would you like to learn more about the Mali Empire at its peak or the University of Timbuktu that Mansa Musa built?"""

    elif any(word in input_lower for word in ["kunta kinteh", "kunta"]):
        figure_info = CULTURAL_KNOWLEDGE["historical_figures"]["kunta_kinteh"]
        return f"""Ah, Kunta Kinteh! Let me share with you the powerful story of this remarkable figure from The Gambia...

Kunta Kinteh was a **{figure_info['title']}** during the {figure_info['period']}. 

**His Story:**
{figure_info['story']}

**Significance:**
{figure_info['significance']}

**Legacy:**
{figure_info['legacy']}

**Cultural Impact:**
{figure_info['cultural_impact']}

Kunta Kinteh's story teaches us about resilience, cultural preservation, and the strength of African heritage. His legacy continues to inspire people around the world to connect with their African roots.

Would you like to learn more about The Gambia's history or the transatlantic slave trade?"""

    # Check for specific country queries
    elif any(word in input_lower for word in ["tribes in senegal", "senegalese tribes", "senegal tribes"]):
        country_info = CULTURAL_KNOWLEDGE["countries"]["senegal"]
        return f"""Ah, the tribes of Senegal! Let me share with you the rich ethnic diversity of this beautiful country...

**Major Tribes in Senegal:**

{chr(10).join([f"• {tribe}" for tribe in country_info['tribes']])}

**Languages Spoken:**
{', '.join(country_info['languages'])}

**Cultural Heritage:**
{country_info['culture']}

Senegal's ethnic diversity is a testament to the rich cultural tapestry of West Africa. Each tribe brings its unique traditions, languages, and customs, creating a vibrant and harmonious society.

Would you like to learn more about any specific Senegalese tribe or their traditional customs?"""

    elif any(word in input_lower for word in ["languages in gambia", "gambian languages", "gambia languages"]):
        country_info = CULTURAL_KNOWLEDGE["countries"]["gambia"]
        return f"""Ah, the languages of The Gambia! Let me share with you the linguistic diversity of this peaceful country...

**Languages Spoken in The Gambia:**

{chr(10).join([f"• {language}" for language in country_info['languages']])}

**Cultural Heritage:**
{country_info['culture']}

The Gambia's linguistic diversity reflects its rich cultural heritage and the peaceful coexistence of different ethnic groups. Mandinka is the most widely spoken language, but each language carries the wisdom and traditions of its people.

Would you like to learn some basic phrases in any of these languages or explore Gambian culture further?"""

    # Check for specific topics and provide detailed responses
    elif any(word in input_lower for word in ["ubuntu", "philosophy", "community"]):
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

    # Check for ethnic groups
    elif any(word in input_lower for word in ["mandinka", "mandingo", "mandinka tribe"]):
        tribe_info = CULTURAL_KNOWLEDGE["ethnic_groups"]["mandinka"]
        return f"""Ah, the Mandinka people! Let me share with you the rich culture and traditions of this remarkable ethnic group...

The **{tribe_info['name']}** are one of the largest ethnic groups in West Africa, with over {tribe_info['population']}. They are found across {tribe_info['location']} and speak {tribe_info['language']}.

**Cultural Traditions:**
{', '.join(tribe_info['culture'])}

**History:**
{tribe_info['history']}

**Traditional Practices:**
{', '.join(tribe_info['traditions'])}

**Core Values:**
{', '.join(tribe_info['values'])}

**Famous Mandinka Figures:**
{', '.join(tribe_info['famous_figures'])}

The Mandinka people have preserved their rich cultural heritage through generations, maintaining their traditions while adapting to modern times. Their emphasis on community, respect for elders, and preservation of oral history through griots makes them a shining example of African cultural resilience.

Would you like to learn more about Mandinka music and instruments, their traditional ceremonies, or the role of griots in their society?"""

    elif any(word in input_lower for word in ["yoruba", "yoruba tribe", "yoruba people"]):
        tribe_info = CULTURAL_KNOWLEDGE["ethnic_groups"]["yoruba"]
        return f"""Ah, the Yoruba people! Let me share with you the fascinating culture and traditions of this ancient ethnic group...

The **{tribe_info['name']}** are one of Africa's largest ethnic groups, with over {tribe_info['population']}. They are primarily found in {tribe_info['location']} and speak {tribe_info['language']}.

**Cultural Traditions:**
{', '.join(tribe_info['culture'])}

**History:**
{tribe_info['history']}

**Traditional Practices:**
{', '.join(tribe_info['traditions'])}

The Yoruba people have one of the most sophisticated cultural systems in Africa, with rich artistic traditions, complex religious beliefs, and a strong emphasis on education and learning.

Would you like to learn more about Yoruba art and beadwork, their religious traditions, or their traditional festivals?"""

    elif any(word in input_lower for word in ["zulu", "zulu tribe", "zulu people"]):
        tribe_info = CULTURAL_KNOWLEDGE["ethnic_groups"]["zulu"]
        return f"""Ah, the Zulu people! Let me share with you the proud culture and traditions of this remarkable ethnic group...

The **{tribe_info['name']}** are one of South Africa's largest ethnic groups, with over {tribe_info['population']}. They are primarily found in {tribe_info['location']} and speak {tribe_info['language']}.

**Cultural Traditions:**
{', '.join(tribe_info['culture'])}

**History:**
{tribe_info['history']}

**Traditional Practices:**
{', '.join(tribe_info['traditions'])}

The Zulu people are known for their warrior traditions, rich cultural heritage, and strong sense of community. Their traditional music, dance, and beadwork continue to inspire people around the world.

Would you like to learn more about Zulu warrior traditions, their traditional music and dance, or their cattle-herding customs?"""

    elif any(word in input_lower for word in ["fula", "fulani"]):
        tribe_info = CULTURAL_KNOWLEDGE["ethnic_groups"]["fula"]
        return f"""Ah, the Fula people! Let me share with you the rich culture and traditions of this remarkable ethnic group...

The **{tribe_info['name']}** are one of the largest ethnic groups in West Africa, with over {tribe_info['population']}. They are found across {tribe_info['location']} and speak {tribe_info['language']}.

**Cultural Traditions:**
{', '.join(tribe_info['culture'])}

**History:**
{tribe_info['history']}

**Traditional Practices:**
{', '.join(tribe_info['traditions'])}

**Core Values:**
{', '.join(tribe_info['values'])}

**Famous Fula Figures:**
{', '.join(tribe_info['famous_figures'])}

The Fula people have preserved their rich cultural heritage through generations, maintaining their traditions while adapting to modern times. Their emphasis on community, respect for elders, and preservation of oral history through griots makes them a shining example of African cultural resilience.

Would you like to learn more about Fula music and instruments, their traditional ceremonies, or the role of griots in their society?"""

    # Check for countries
    elif any(word in input_lower for word in ["senegal", "gambia"]):
        country_info = CULTURAL_KNOWLEDGE["countries"][word]
        return f"""Ah, the {country_info['name']}! Let me share with you the rich cultural heritage and traditions of this African country...

**Tribes:**
{', '.join(country_info['tribes'])}

**Languages:**
{', '.join(country_info['languages'])}

**Culture:**
{country_info['culture']}

The {country_info['name']} is known for its rich cultural diversity, traditional music, wrestling, and hospitality.

Would you like to learn more about the daily life in this country or its cultural traditions?"""

    # Default response with cultural warmth
    default_responses = FALLBACK_RESPONSES["default"]
    
    # Check if the query seems to be about a specific person or place
    if any(word in input_lower for word in ["who is", "tell me about", "what is"]):
        return f"""Ah, my child, I understand you're asking about something specific. While I may not have detailed information about that particular topic, let me share some related African wisdom with you...

{random.choice(default_responses)}

I can help you learn about:
- **African historical figures** like Sundiata Keita, Mansa Musa, or Sir Dawda Jawara
- **African ethnic groups** like the Mandinka, Yoruba, or Zulu people
- **African empires** like Mali, Ghana, or Songhai
- **African philosophy** like Ubuntu
- **African traditions** like griot storytelling
- **African proverbs and wisdom**

What would you like to explore about African culture, history, or wisdom?"""
    
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
            with st.spinner("Searching for the latest information about Africa..."):
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