import streamlit as st
from googlesearch import search

st.set_page_config(page_title="YCA Asistan", page_icon="🤖")
st.title("🤖 YCA - Google Destekli")

user_input = st.text_input("Bir şey sor...")

if user_input:
    if "nasılsın" in user_input.lower():
        st.success("İyiyim, teşekkür ederim!")
    elif "merhaba" in user_input.lower():
        st.write("Merhaba! Sana nasıl yardımcı olabilirim?")
    else:
        with st.spinner('Google\'da aranıyor...'):
            try:
                # Google'da arama yap
                results = list(search(user_input, num_results=3))
                
                if results:
                    st.write("İşte bulduklarım:")
                    for url in results:
                        st.write(url)
                else:
                    st.write("Sonuç bulunamadı.")
            except Exception as e:
                st.error(f"Hata: {e}")
