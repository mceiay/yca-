import streamlit as st

# Sayfa Yapılandırması
st.set_page_config(page_title="YCA Asistan", page_icon="🤖")

# Yan Menü
st.sidebar.title("YCA Ayarları")
st.sidebar.info("Mod: Kişisel Asistan")

# Ana Başlık
st.title("🤖 YCA - Senin Asistanın")
st.subheader("Bana istediğini sor, senin için özelleştireyim.")

user_input = st.text_input("Bugün neler yapalım?")

if user_input:
    text = user_input.lower()
    
    # KİŞİSELLEŞTİRİLMİŞ CEVAPLAR (Buraları istediğin gibi çoğaltabilirsin)
    if "nasılsın" in text:
        st.success("Harikayım! Seninle yeni projeler üzerinde çalışmaya hazırım. Sen nasılsın?")
    
    elif "galatasaray" in text or "gs" in text:
        st.balloons()
        st.write("### 🦁 Cimbom'un yeri bende ayrıdır!")
        st.write("Takımın son durumu hakkında bilgi almak istersen [buradan güncel haberlere ulaşabilirsin.](https://www.google.com/search?q=galatasaray+haberleri)")
    
    elif "kod" in text or "python" in text or "yazılım" in text:
        st.write("💻 **Yazılım modu aktif!** Kodunu veya hata mesajını buraya yapıştır, birlikte düzeltelim.")
    
    elif "merhaba" in text:
        st.write("Merhaba! YCA emrinde, sana nasıl yardımcı olabilirim?")
    
    # GENEL ARAMA (Eğer özel bir durum yoksa)
    else:
        st.write(f"Anladım, '{user_input}' konusuna bakıyorum...")
        google_url = f"https://www.google.com/search?q={user_input.replace(' ', '+')}"
        st.link_button("🔎 Google'da Detaylı Ara", google_url)
