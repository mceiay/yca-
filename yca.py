import streamlit as st
from duckduckgo_search import DDGS

st.set_page_config(page_title="YCA Asistan", page_icon="🤖")

st.title("🤖 YCA - Yapay Zeka Asistanı")

user_input = st.text_input("YCA'ya bir şey yaz...")

if user_input:
    # Sohbet mantığı
    if "nasılsın" in user_input.lower():
        st.success("İyiyim, teşekkür ederim! Sen nasılsın?")
    elif "merhaba" in user_input.lower():
        st.balloons()
        st.write("Merhaba! Sana nasıl yardımcı olabilirim?")
    
    # Arama mantığı
    else:
        with st.spinner('YCA internette arıyor...'):
            try:
                results = list(DDGS().text(user_input, max_results=3))
                if results:
                    for r in results:
                        st.write(f"**{r['title']}**")
                        st.write(r['body'])
                        st.write("---")
                else:
                    st.write("Bu konuda bir sonuç bulamadım.")
            except Exception as e:
                st.error("Bir hata oluştu.")
