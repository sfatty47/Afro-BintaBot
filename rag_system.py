import streamlit as st
from typing import List, Dict, Tuple
import re
from model import CULTURAL_KNOWLEDGE, FALLBACK_RESPONSES
import random

class AfricanRAGSystem:
    """
    Simple RAG system for African cultural knowledge
    """
    
    def __init__(self):
        self.knowledge_chunks = self._create_knowledge_chunks()
    
    def _create_knowledge_chunks(self) -> List[Dict]:
        """
        Create searchable chunks from the cultural knowledge base
        """
        chunks = []
        
        # Historical figures chunks
        for figure_key, figure_info in CULTURAL_KNOWLEDGE["historical_figures"].items():
            chunks.extend([
                {
                    "content": f"{figure_info['name']} - {figure_info['title']} ({figure_info['period']})",
                    "topic": figure_key,
                    "category": "historical_figure",
                    "keywords": [figure_info['name'].lower(), figure_key, "leader", "president", "emperor", "founder"]
                },
                {
                    "content": f"{figure_info['name']} achievements: {', '.join(figure_info['achievements'])}",
                    "topic": figure_key,
                    "category": "historical_figure",
                    "keywords": [figure_info['name'].lower(), figure_key, "achievements", "accomplishments"]
                },
                {
                    "content": f"{figure_info['name']} legacy: {figure_info['legacy']}",
                    "topic": figure_key,
                    "category": "historical_figure",
                    "keywords": [figure_info['name'].lower(), figure_key, "legacy", "impact", "influence"]
                }
            ])
        
        # Ubuntu chunks
        ubuntu_info = CULTURAL_KNOWLEDGE["ubuntu"]
        chunks.extend([
            {
                "content": f"Ubuntu philosophy: {ubuntu_info['definition']}",
                "topic": "ubuntu",
                "category": "philosophy",
                "keywords": ["ubuntu", "philosophy", "humanity", "community", "interconnectedness"]
            },
            {
                "content": f"Ubuntu meaning: {ubuntu_info['philosophy']}",
                "topic": "ubuntu", 
                "category": "philosophy",
                "keywords": ["ubuntu", "community", "compassion", "support"]
            },
            {
                "content": f"Ubuntu proverb: {ubuntu_info['proverbs'][0]}",
                "topic": "ubuntu",
                "category": "proverb",
                "keywords": ["ubuntu", "proverb", "humanity", "people"]
            }
        ])
        
        # Griot chunks
        griot_info = CULTURAL_KNOWLEDGE["griots"]
        chunks.extend([
            {
                "content": f"Griot definition: {griot_info['definition']}",
                "topic": "griots",
                "category": "tradition",
                "keywords": ["griot", "storyteller", "historian", "musician", "oral"]
            },
            {
                "content": f"Griot role: {griot_info['role']}",
                "topic": "griots",
                "category": "tradition", 
                "keywords": ["griot", "library", "history", "genealogy", "wisdom"]
            },
            {
                "content": f"Griot significance: {griot_info['significance']}",
                "topic": "griots",
                "category": "tradition",
                "keywords": ["griot", "memory", "community", "continuity", "generations"]
            }
        ])
        
        # Empire chunks
        for empire_name, empire_info in CULTURAL_KNOWLEDGE["empires"].items():
            chunks.extend([
                {
                    "content": f"{empire_name.title()} Empire period: {empire_info['period']}",
                    "topic": empire_name,
                    "category": "history",
                    "keywords": [empire_name, "empire", "period", "history"]
                }
            ])
            
            # Add achievements chunk only if it exists
            if 'achievements' in empire_info:
                chunks.append({
                    "content": f"{empire_name.title()} Empire achievements: {', '.join(empire_info['achievements'])}",
                    "topic": empire_name,
                    "category": "history",
                    "keywords": [empire_name, "empire", "achievements", "history"]
                })
            
            # Add other available information
            for key, value in empire_info.items():
                if key not in ['period', 'achievements'] and isinstance(value, str):
                    chunks.append({
                        "content": f"{empire_name.title()} Empire {key}: {value}",
                        "topic": empire_name,
                        "category": "history",
                        "keywords": [empire_name, "empire", key, "history"]
                    })
        
        # Language chunks
        lang_info = CULTURAL_KNOWLEDGE["languages"]
        chunks.extend([
            {
                "content": f"African language families: {', '.join(lang_info['major_families'])}",
                "topic": "languages",
                "category": "culture",
                "keywords": ["language", "families", "african", "linguistic"]
            },
            {
                "content": f"Widely spoken African languages: {', '.join(lang_info['widely_spoken'])}",
                "topic": "languages",
                "category": "culture",
                "keywords": ["language", "spoken", "african", "swahili", "yoruba", "zulu"]
            }
        ])
        
        # Art and music chunks
        art_info = CULTURAL_KNOWLEDGE["art"]
        music_info = CULTURAL_KNOWLEDGE["music"]
        chunks.extend([
            {
                "content": f"African art traditions: {', '.join(art_info['traditions'])}",
                "topic": "art",
                "category": "culture",
                "keywords": ["art", "traditions", "african", "cultural"]
            },
            {
                "content": f"African musical instruments: {', '.join(music_info['instruments'])}",
                "topic": "music",
                "category": "culture",
                "keywords": ["music", "instruments", "african", "traditional"]
            }
        ])
        
        # Proverb chunks
        proverbs = CULTURAL_KNOWLEDGE["proverbs"]["wisdom"] + CULTURAL_KNOWLEDGE["proverbs"]["community"]
        for proverb in proverbs:
            chunks.append({
                "content": f"African proverb: {proverb}",
                "topic": "proverbs",
                "category": "wisdom",
                "keywords": ["proverb", "wisdom", "african", "traditional"]
            })
        
        return chunks
    
    def search_knowledge(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Search for relevant knowledge chunks based on query
        """
        query_lower = query.lower()
        query_words = set(re.findall(r'\w+', query_lower))
        
        scored_chunks = []
        
        for chunk in self.knowledge_chunks:
            score = 0
            
            # Exact name matching (highest priority)
            if chunk["category"] == "historical_figure":
                figure_name = chunk["keywords"][0]  # First keyword is the name
                if figure_name in query_lower:
                    score += 10  # Very high score for exact name match
            
            # Keyword matching
            for keyword in chunk["keywords"]:
                if keyword.lower() in query_lower:
                    score += 2
            
            # Word overlap
            chunk_words = set(re.findall(r'\w+', chunk["content"].lower()))
            overlap = len(query_words.intersection(chunk_words))
            score += overlap
            
            # Topic matching
            if chunk["topic"] in query_lower:
                score += 3
            
            # Category matching
            if chunk["category"] in query_lower:
                score += 2
            
            if score > 0:
                scored_chunks.append((score, chunk))
        
        # Sort by score and return top_k results
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        return [chunk for score, chunk in scored_chunks[:top_k]]
    
    def generate_rag_response(self, query: str, chat_history: List[Dict] = None) -> str:
        """
        Generate response using RAG with cultural warmth
        """
        # Search for relevant knowledge
        relevant_chunks = self.search_knowledge(query)
        
        if not relevant_chunks:
            # No relevant chunks found, use fallback
            return self._get_fallback_response(query)
        
        # Build context from relevant chunks
        context = "\n".join([chunk["content"] for chunk in relevant_chunks])
        
        # Generate culturally warm response
        response = self._generate_cultural_response(query, context, relevant_chunks)
        
        return response
    
    def _generate_cultural_response(self, query: str, context: str, chunks: List[Dict]) -> str:
        """
        Generate a culturally warm response based on retrieved context
        """
        query_lower = query.lower()
        
        # Determine the main topic
        topics = [chunk["topic"] for chunk in chunks]
        main_topic = max(set(topics), key=topics.count) if topics else "general"
        
        # Check for historical figures first (highest priority)
        if main_topic in CULTURAL_KNOWLEDGE["historical_figures"]:
            return self._generate_historical_figure_response(query, context, chunks, main_topic)
        
        # Generate appropriate response based on topic
        if main_topic == "ubuntu":
            return self._generate_ubuntu_response(query, context, chunks)
        elif main_topic == "griots":
            return self._generate_griot_response(query, context, chunks)
        elif main_topic in ["mali", "ghana", "songhai"]:
            return self._generate_empire_response(query, context, chunks, main_topic)
        elif main_topic == "proverbs":
            return self._generate_proverb_response(query, context, chunks)
        elif main_topic == "languages":
            return self._generate_language_response(query, context, chunks)
        elif main_topic in ["art", "music"]:
            return self._generate_art_response(query, context, chunks)
        else:
            return self._generate_general_response(query, context, chunks)
    
    def _generate_historical_figure_response(self, query: str, context: str, chunks: List[Dict], figure_key: str) -> str:
        """Generate specific response for historical figures"""
        figure_info = CULTURAL_KNOWLEDGE["historical_figures"][figure_key]
        
        return f"""Ah, {figure_info['name']}! Let me share with you the story of this remarkable African leader...

{context}

{figure_info['name']} was {figure_info['title']} during {figure_info['period']}. 

**Key Achievements:**
{', '.join(figure_info['achievements'])}

**Legacy:**
{figure_info['legacy']}

{figure_info['story']}

{figure_info['name']}'s story teaches us about leadership, vision, and the power of determination. Like the great baobab tree, their influence continues to provide shade and wisdom for generations to come.

Would you like to learn more about the historical context of {figure_info['name']}'s time or their impact on African history?"""
    
    def _generate_ubuntu_response(self, query: str, context: str, chunks: List[Dict]) -> str:
        """Generate Ubuntu-specific response"""
        ubuntu_info = CULTURAL_KNOWLEDGE["ubuntu"]
        
        return f"""Ah, my child, you ask about Ubuntu - the very heart of our African wisdom!

Based on the knowledge I have gathered, let me share with you the essence of Ubuntu:

{context}

Ubuntu means "humanity" in the Nguni languages, but it is so much more than a word. It is a way of life that teaches us: *"I am because we are."*

{ubuntu_info['philosophy']}

As our elders say: *"{ubuntu_info['proverbs'][0]}"*

This wisdom reminds us that our humanity is bound up in the humanity of others. We cannot be truly human alone - we need each other, like the branches of the great baobab tree need the trunk and roots.

Would you like to hear more about how Ubuntu guides our daily lives and community relationships?"""
    
    def _generate_griot_response(self, query: str, context: str, chunks: List[Dict]) -> str:
        """Generate Griot-specific response"""
        griot_info = CULTURAL_KNOWLEDGE["griots"]
        
        return f"""Ah, the griots! The keepers of our stories and the guardians of our memory. Let me share with you what I know about these wise ones...

{context}

The griots are like living libraries, carrying the wisdom of generations in their hearts and voices. They preserve our history not in books, but in stories that flow like rivers through time.

{griot_info['traditions'][0]}
{griot_info['traditions'][1]}
{griot_info['traditions'][2]}

As a griot myself, I carry forward this sacred tradition, sharing the wisdom of our ancestors with you today.

Would you like to hear a story that has been passed down through the generations?"""
    
    def _generate_empire_response(self, query: str, context: str, chunks: List[Dict], empire_name: str) -> str:
        """Generate empire-specific response"""
        empire_info = CULTURAL_KNOWLEDGE["empires"][empire_name]
        
        # Build empire description dynamically
        empire_desc = f"The {empire_name.title()} Empire"
        
        if 'period' in empire_info:
            empire_desc += f" ({empire_info['period']})"
        
        if 'location' in empire_info:
            empire_desc += f" was located in {empire_info['location']}"
        elif 'capital' in empire_info:
            empire_desc += f" had its capital at {empire_info['capital']}"
        
        if 'achievements' in empire_info:
            achievements_text = f"Key achievements included: {', '.join(empire_info['achievements'])}"
        else:
            # Use other available information
            other_info = []
            for key, value in empire_info.items():
                if key not in ['period', 'achievements'] and isinstance(value, str):
                    other_info.append(f"{key}: {value}")
            achievements_text = f"Notable features: {', '.join(other_info)}" if other_info else "was a significant African empire"
        
        return f"""Ah, the great {empire_name.title()} Empire! Let me share with you the stories of this magnificent kingdom that once ruled the lands of Africa...

{context}

{empire_desc}. {achievements_text}

These empires show us that Africa has always been a land of great civilizations, wisdom, and achievement. Our ancestors built kingdoms that rivaled any in the world!

Would you like to learn more about the daily life in these empires or their cultural achievements?"""
    
    def _generate_proverb_response(self, query: str, context: str, chunks: List[Dict]) -> str:
        """Generate proverb-specific response"""
        proverbs = CULTURAL_KNOWLEDGE["proverbs"]["wisdom"] + CULTURAL_KNOWLEDGE["proverbs"]["community"]
        selected_proverbs = random.sample(proverbs, min(3, len(proverbs)))
        
        return f"""Ah, the wisdom of our ancestors! Let me share with you some proverbs that have guided our people for generations...

{context}

*"{selected_proverbs[0]}"*
*"{selected_proverbs[1]}"*
*"{selected_proverbs[2]}"*

These proverbs are like seeds of wisdom, planted by our ancestors and growing in the hearts of each generation. They teach us about community, respect, and the values that hold us together.

Each proverb carries a deeper meaning, like the layers of an onion. The more we reflect on them, the more wisdom we discover.

Would you like me to explain the deeper meaning behind any of these proverbs?"""
    
    def _generate_language_response(self, query: str, context: str, chunks: List[Dict]) -> str:
        """Generate language-specific response"""
        lang_info = CULTURAL_KNOWLEDGE["languages"]
        
        return f"""Ah, the beautiful languages of our continent! Let me share with you the richness of African linguistic heritage...

{context}

Africa is home to thousands of languages, each carrying the wisdom, stories, and cultural identity of its people. They are like different colors in the great tapestry of African culture.

{lang_info['cultural_significance']}

Would you like to learn some basic greetings in any of these languages?"""
    
    def _generate_art_response(self, query: str, context: str, chunks: List[Dict]) -> str:
        """Generate art/music-specific response"""
        art_info = CULTURAL_KNOWLEDGE["art"]
        music_info = CULTURAL_KNOWLEDGE["music"]
        
        return f"""Ah, the beauty of African artistic expression! Let me share with you the rich traditions of our arts and music...

{context}

African art and music are not just for entertainment - they are ways of communicating with the spirits, telling stories, and preserving our cultural identity. Every pattern, every rhythm, every dance step carries meaning passed down through generations.

Would you like to learn more about any specific art form or musical tradition?"""
    
    def _generate_general_response(self, query: str, context: str, chunks: List[Dict]) -> str:
        """Generate general response"""
        return f"""Ah, my child, let me share with you the wisdom I have gathered about this topic...

{context}

The knowledge of our ancestors flows through me like the great rivers of Africa. Each piece of wisdom connects us to our heritage and helps us understand the beauty of our cultural traditions.

Is there a specific aspect of this topic you'd like to explore further?"""
    
    def _get_fallback_response(self, query: str) -> str:
        """Get fallback response when no relevant chunks are found"""
        default_responses = FALLBACK_RESPONSES["default"]
        return f"{random.choice(default_responses)} I am here to share the wisdom of our ancestors and help you learn about the rich cultural heritage of Africa. What specific aspect of African culture, history, or wisdom would you like to explore?"

# Global RAG system instance
rag_system = AfricanRAGSystem()

def get_rag_response(query: str, chat_history: List[Dict] = None) -> str:
    """
    Get response using the RAG system
    """
    return rag_system.generate_rag_response(query, chat_history) 