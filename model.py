from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import streamlit as st
import os
import time

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

def get_cultural_response(user_input):
    """Get a cultural response based on user input keywords with comprehensive African knowledge"""
    user_input_lower = user_input.lower()
    
    # Mansa Musa
    if "mansa musa" in user_input_lower:
        if "pilgrimage" in user_input_lower or "mecca" in user_input_lower:
            return "Mansa Musa's pilgrimage to Mecca in 1324-1325 CE is one of the most famous journeys in African history. He traveled with 60,000 people, including 12,000 slaves, and carried so much gold that he caused inflation in Egypt and the Mediterranean. His generosity and wealth demonstrated Mali's power to the Islamic world and established Timbuktu as a center of learning."
        elif "wealth" in user_input_lower or "gold" in user_input_lower:
            return "Mansa Musa was incredibly wealthy, with estimates suggesting he was the richest person in history. His wealth came from Mali's control of gold mines and trade routes. During his pilgrimage, he gave away so much gold that it devalued the metal in Egypt for years. His wealth demonstrated the economic power of African empires."
        else:
            return "Mansa Musa (1280-1337 CE) was the most famous ruler of the Mali Empire, reigning from 1312 to 1337. He was a devout Muslim who made the famous pilgrimage to Mecca in 1324, demonstrating Mali's wealth and power to the Islamic world. Under his rule, Timbuktu became a major center of learning and culture."
    
    # Sundiata Keita
    elif "sundiata" in user_input_lower:
        if "mother" in user_input_lower or "family" in user_input_lower:
            return "Sundiata Keita's mother, Sogolon Kedjou, was a remarkable woman who played a crucial role in his rise to power. Despite Sundiata being born with a disability, his mother never gave up on him. She taught him patience, wisdom, and the importance of inner strength. When Sundiata was exiled, his mother's teachings and the memory of her love gave him the courage to return and claim his rightful place as king."
        elif "childhood" in user_input_lower or "early" in user_input_lower:
            return "Sundiata Keita was born around 1217 CE in Niani, Mali. As a child, he was unable to walk and was often mocked. However, his mother Sogolon Kedjou believed in his potential. At age seven, he miraculously stood and walked, showing his inner strength. This transformation marked the beginning of his journey to become the Lion King of Mali."
        elif "battle" in user_input_lower or "war" in user_input_lower or "kirina" in user_input_lower:
            return "The Battle of Kirina in 1235 CE was the decisive battle where Sundiata Keita defeated King Soumaoro Kanté of the Sosso Empire. This victory established the Mali Empire and marked the beginning of one of Africa's greatest kingdoms. Sundiata's military strategy and leadership united the Mandinka people."
        else:
            return "Sundiata Keita (1217-1255 CE) was the founder of the Mali Empire, one of Africa's greatest kingdoms. Known as the 'Lion King,' he united the Mandinka people and established a powerful empire that controlled the gold and salt trade routes. His capital was Niani, and his story is preserved through griot oral traditions."
    
    # Mandinka Language
    elif "mandinka" in user_input_lower or "mandingo" in user_input_lower:
        if "good morning" in user_input_lower or "greeting" in user_input_lower:
            return "In Mandinka, 'Good morning' is **'I ni sogoma'** (pronounced: ee-nee soh-GOH-mah). Other common greetings include: 'I ni wula' (Good afternoon), 'I ni tilo' (Good evening), and 'I ni fanaa' (How are you?). Greetings are very important in Mandinka culture and show respect for others."
        elif "language" in user_input_lower or "speak" in user_input_lower:
            return "Mandinka is a Mande language spoken by the Mandinka people in West Africa, particularly in Mali, Senegal, Gambia, Guinea, and Guinea-Bissau. It's part of the larger Mande language family and has influenced other West African languages. The language is rich in proverbs and oral traditions."
        else:
            return "Mandinka is a Mande language spoken by the Mandinka people across West Africa. It's the language of the ancient Mali Empire and is still spoken today in Mali, Senegal, Gambia, and other West African countries. The language preserves many traditional proverbs and cultural wisdom."
    
    # Mali Empire
    elif "mali" in user_input_lower and "empire" in user_input_lower:
        if "wealth" in user_input_lower or "gold" in user_input_lower:
            return "The Mali Empire was incredibly wealthy, controlling the gold mines of Bambuk and the salt trade from the Sahara. Gold was so abundant that Mansa Musa's pilgrimage to Mecca in 1324 caused inflation in Egypt and the Mediterranean. The empire's wealth came from controlling trade routes between West Africa, North Africa, and the Middle East."
        elif "timeline" in user_input_lower or "period" in user_input_lower:
            return "The Mali Empire flourished from approximately 1235 CE to 1670 CE. It reached its peak under Mansa Musa (1312-1337 CE) and controlled territory from the Atlantic coast to Timbuktu, including parts of modern-day Mali, Senegal, Guinea, Burkina Faso, and Niger."
        else:
            return "The Mali Empire (1235-1670 CE) was one of Africa's greatest empires, centered in West Africa. Its capital was Niani, and it controlled territory from the Atlantic coast to Timbuktu. The empire was known for its wealth in gold, sophisticated government, and cultural achievements, particularly in Timbuktu."
    
    # Ghana Empire
    elif "ghana" in user_input_lower and "empire" in user_input_lower:
        return "The Ghana Empire (300-1100 CE) was one of the first great West African empires, predating Mali. Located in present-day Mauritania and Mali, it controlled the gold and salt trade routes. The empire's wealth came from taxing trade caravans crossing the Sahara. Its capital was Koumbi Saleh."
    
    # Songhai Empire
    elif "songhai" in user_input_lower and "empire" in user_input_lower:
        return "The Songhai Empire (1464-1591 CE) succeeded Mali as the dominant power in West Africa. Under Askia Muhammad, it became the largest empire in African history, controlling territory from the Atlantic to Lake Chad. Its capital was Gao, and it was known for its military strength and cultural achievements."
    
    # Timbuktu
    elif "timbuktu" in user_input_lower:
        return "Timbuktu was a major center of learning and trade in the Mali and Songhai empires. Founded around 1100 CE, it became famous for its universities, including Sankore University, and its vast libraries. Scholars from across the Islamic world came to study there, making it a center of intellectual and cultural exchange."
    
    # Griots
    elif "griot" in user_input_lower:
        if "role" in user_input_lower or "function" in user_input_lower:
            return "Griots are traditional West African storytellers, historians, and musicians. They serve as living libraries, preserving oral history, genealogy, and cultural traditions. Griots use music, poetry, and storytelling to pass down knowledge from generation to generation. They are respected advisors to kings and communities."
        else:
            return "Griots are the traditional storytellers, historians, and keepers of oral tradition in West Africa. They are the living libraries of our people, passing down wisdom through generations. Their role is crucial in preserving African history and culture."
    
    # Ubuntu Philosophy
    elif "ubuntu" in user_input_lower:
        if "meaning" in user_input_lower or "definition" in user_input_lower:
            return "Ubuntu is a Nguni Bantu term meaning 'humanity.' It translates to 'I am because we are' and emphasizes the interconnectedness of all people. This philosophy teaches that our humanity is defined by our relationships with others and that we find our true selves through community."
        else:
            return "Ubuntu is a beautiful African philosophy that means 'I am because we are.' It teaches us that our humanity is interconnected - we find our true selves through our relationships with others. This philosophy is central to many African cultures, especially in Southern Africa."
    
    # African Proverbs
    elif any(word in user_input_lower for word in ["proverb", "wisdom", "elder"]):
        if "village" in user_input_lower or "child" in user_input_lower:
            return "The proverb 'It takes a village to raise a child' reflects the communal nature of African societies. This wisdom teaches that children belong to the entire community, not just their parents. Everyone has a role in nurturing and educating the next generation."
        else:
            return "As our ancestors said: 'It takes a village to raise a child.' This speaks to the communal nature of African societies. Other wise sayings include: 'The river flows not by its own power, but by the strength of many streams' and 'A single bracelet does not jingle.' These proverbs teach us about unity, cooperation, and community."
    
    # African Stories and Folktales
    elif any(word in user_input_lower for word in ["story", "tale", "folktale"]):
        if "anansi" in user_input_lower:
            return "Anansi the Spider is a famous trickster figure in West African and Caribbean folklore. He is known for his cleverness and ability to outsmart others. Anansi stories teach moral lessons and are passed down through generations, showing the importance of wisdom and wit."
        else:
            return "Let me share a tale from the griots: Once, in the ancient kingdom of Mali, there lived a wise woman who taught that 'The wealth of a nation is not in its gold, but in the wisdom of its people.' African stories often feature animals, tricksters, and moral lessons that teach important values."
    
    # African Kingdoms and Empires
    elif "kingdom" in user_input_lower or "empire" in user_input_lower:
        return "Africa has been home to many great kingdoms and empires throughout history. Notable ones include the Ghana Empire (300-1100 CE), Mali Empire (1235-1670 CE), Songhai Empire (1464-1591 CE), Great Zimbabwe (1100-1450 CE), and the Kingdom of Kush (1070 BCE-350 CE). Each contributed to Africa's rich cultural heritage."
    
    # African Trade Routes
    elif "trade" in user_input_lower or "route" in user_input_lower:
        return "Africa had extensive trade networks, including the Trans-Saharan trade routes that connected West Africa to North Africa and the Mediterranean. These routes carried gold, salt, ivory, and other goods. The Swahili Coast also had trade connections with the Indian Ocean world, including Arabia, India, and China."
    
    # African Architecture
    elif "architecture" in user_input_lower or "building" in user_input_lower:
        return "African architecture is diverse and impressive. Great Zimbabwe features stone walls and towers built without mortar. The mud-brick mosques of Mali, like the Great Mosque of Djenné, are architectural marvels. The rock-hewn churches of Lalibela in Ethiopia demonstrate advanced engineering skills."
    
    # African Art and Culture
    elif "art" in user_input_lower or "culture" in user_input_lower:
        return "African art is incredibly diverse, from the bronze sculptures of Benin to the masks of West Africa, the rock art of the Sahara, and the beadwork of Southern Africa. African cultures have rich traditions in music, dance, storytelling, and craftsmanship that have influenced cultures worldwide."
    
    # Default response
    else:
        return "I am BintaBot, your African cultural assistant. I'm here to share the wisdom, stories, and traditions of Africa with you. What would you like to learn about African culture, history, or wisdom?"

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