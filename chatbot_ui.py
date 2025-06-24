import streamlit as st
from chatbot import culturally_aware_chat

st.title("FatouBot - African Chat Assistant")
user_input = st.text_input("You:")

if user_input:
    response = culturally_aware_chat(user_input)
    st.write("FatouBot:", response) 