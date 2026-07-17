import streamlit as st
import requests

st.set_page_config(page_title="YCA Asistan", page_icon="🤖")
st.title("🤖 YCA - Arama Testi")

user_input = st.text_input("Ne aramıştın?")

if user_input:
    if "nasılsın" in user_input.lower():
        st.write("İyiyim, teşekkür ederim!")
    else:
        st.write("Doğrudan arama yapmaya çalışıyorum...")
        # Arama yerine doğrudan Google linki verelim, en azından boş dönmez
        google_url = f"https://www.google.com/search?q={user_input.replace(' ', '+')}"
        st.write(f"Sonuçları buradan görebilirsin: [Google'da Ara]({google_url})")
