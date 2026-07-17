import streamlit as st
from duckduckgo_search import DDGS
import time

st.set_page_config(page_title="YCA Asistan", page_icon="🤖")
st.title("🤖 YCA - Yapay Zeka Asistanı")

user_input = st.text_input("YCA'ya bir şey yaz...")

if user_input:
    if "nasılsın" in user_input.lower():
        st.success("İyiyim, teşekkür ederim! Sen nasılsın?")
    elif "merhaba" in user_input.lower():
        st.balloons()
        st.write("Merhaba! Sana nasıl yardımcı olabilirim?")
    else:
        with st.spinner('YCA internette daha derinden arıyor...'):
            try:
                # DDGS aramasını daha güvenli bir yöntemle yapalım
                ddgs = DDGS()
                results = list(ddgs.text(user_input, max_results=3))
                
                # Eğer sonuç gelmediyse, küçük bir bekleme yapıp tekrar deneyelim (ikinci şans)
                if not results:
                    time.sleep(1) 
                    results = list(ddgs.text(user_input, max_results=3))

                if results:
                    for r in results:
                        st.write(f"### {r['title']}")
                        st.write(r['body'])
                        st.write("---")
                else:
                    st.write("Arama motoru şu an çok yoğun veya kısıtlamaya takıldı. Lütfen biraz bekleyip tekrar 'Galatasaray' gibi basit bir kelime yazmayı dene.")
            except Exception as e:
                st.error("Bir hata oluştu, lütfen sayfayı yenile.")
