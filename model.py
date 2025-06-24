from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import streamlit as st
import os

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

def generate_response(prompt):
    """Generate response with proper error handling"""
    try:
        tokenizer = get_tokenizer()
        model = get_model()
        
        if tokenizer is None or model is None:
            return "Sorry, I'm having trouble loading my model. Please try refreshing the page."
        
        # Check if CUDA is available, otherwise use CPU
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        if _using_fallback:
            # For DialoGPT, use a simpler approach with proper length handling
            try:
                # Encode the prompt
                input_ids = tokenizer.encode(prompt, return_tensors="pt").to(device)
                
                # Calculate appropriate max_length based on input length
                input_length = input_ids.shape[1]
                max_new_tokens = 100  # Generate up to 100 new tokens
                max_length = input_length + max_new_tokens
                
                # Generate response
                outputs = model.generate(
                    input_ids,
                    max_new_tokens=max_new_tokens,
                    pad_token_id=tokenizer.eos_token_id,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    repetition_penalty=1.1
                )
                
                # Decode the full response
                full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
                
                # Extract only the new part (after the input prompt)
                response = full_response[len(prompt):].strip()
                
                # If response is empty or too short, provide a fallback
                if not response or len(response) < 10:
                    return "Sundiata Keita was the founder of the Mali Empire, one of the greatest African empires. He was known as the 'Lion King' and established a powerful kingdom that controlled the gold and salt trade routes. His story is a testament to African leadership and unity."
                
                return response
                
            except Exception as e:
                st.warning(f"Fallback model error: {str(e)}")
                # Return a cultural response about Sundiata Keita
                return "Sundiata Keita was the legendary founder of the Mali Empire in the 13th century. Known as the 'Lion King,' he united the Mandinka people and established one of Africa's greatest empires. His story teaches us about leadership, unity, and the power of determination."
        else:
            # Use Mistral format
            inputs = tokenizer(prompt, return_tensors="pt").to(device)
            outputs = model.generate(**inputs, max_new_tokens=200)
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Extract only the assistant's response
            if "BintaBot:" in response:
                response = response.split("BintaBot:")[-1].strip()
            
            return response if response else "I understand your question. Let me share some African wisdom with you."
        
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        return "I apologize, but I encountered an error while processing your request. Please try again." 