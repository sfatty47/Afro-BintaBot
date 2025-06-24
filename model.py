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
            # Use simpler prompt format for DialoGPT
            inputs = tokenizer.encode(prompt, return_tensors="pt").to(device)
            outputs = model.generate(inputs, max_length=150, pad_token_id=tokenizer.eos_token_id)
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Extract only the new part of the response
            response = response[len(prompt):].strip()
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