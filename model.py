from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import streamlit as st

model_name = "mistralai/Mistral-7B-Instruct-v0.2"

# Global variables for lazy loading
_tokenizer = None
_model = None

def get_tokenizer():
    """Lazy load the tokenizer"""
    global _tokenizer
    if _tokenizer is None:
        try:
            _tokenizer = AutoTokenizer.from_pretrained(model_name)
        except Exception as e:
            st.error(f"Failed to load tokenizer: {str(e)}")
            st.info("Please check your internet connection and try again.")
            return None
    return _tokenizer

def get_model():
    """Lazy load the model"""
    global _model
    if _model is None:
        try:
            _model = AutoModelForCausalLM.from_pretrained(
                model_name, 
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
        
        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        outputs = model.generate(**inputs, max_new_tokens=200)
        return tokenizer.decode(outputs[0], skip_special_tokens=True)
        
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        return "I apologize, but I encountered an error while processing your request. Please try again." 