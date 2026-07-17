import streamlit as st
from duckduckgo_search import DDGS

# Sayfa ayarları - Bunu en başa ekle, sitenin adını ve ikonunu değiştirir
st.set_page_config(page_title="YCA Asistan", page_icon="🤖")

# Arayüzü güzelleştirmek için biraz CSS (Opsiyonel)
st.markdown("""
    <style>
    .stTextInput {background-color: #f0f2f6; border-radius: 10px;}
    </style>
    """, unsafe_allow_html=True)

# Yan menü (Sidebar)
st.sidebar.title("🤖 YCA Hakkında")
st.sidebar.info("YCA, seninle sohbet edebilen ve internette arama yapabilen bir yapay zeka asistanıdır.")

# Başlık
st.title("🤖 YCA - Yapay Zeka Asistanı")
st.subheader("İnternette arama yapabilir veya benimle sohbet edebilirsin.")

# Giriş
user_input = st.text_input("Bir şey yaz...")

if user_input:
    # 1. Sohbet mantığı
    if "nasılsın" in user_input.lower():
        st.success("İyiyim, teşekkür ederim! Sen nasılsın, bugün sana nasıl yardımcı olabilirim?")
    elif "merhaba" in user_input.lower():
        st.balloons() # Küçük bir sürpriz :)
        st.write("Merhaba! YCA seninle tanıştığına çok memnun oldu.")
    
    # 2. Arama mantığı
    else:
        with st.spinner('YCA düşünüyor...'):
            try:
                # Arama metodunu biraz daha esnek hale getirelim
                results = list(DDGS().text(user_input, max_results=3))
                
                if results:
                    st.write("İşte bulduklarım:")
                    for r in results:
                        st.write(f"- {r['body']}")
                else:
                    st.warning("Maalesef bu konuda bir sonuç bulamadım. Başka bir şey sormayı dene!")
            except Exception as e:
                st.error(f"Bir hata oluştu: {e}")
