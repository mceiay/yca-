import streamlit as st
from ddgs import DDGS
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# Sayfa ayarları
st.set_page_config(page_title="YCA Asistan", page_icon="🤖", layout="centered")

st.title("🤖 YCA - Yapay Zeka Asistanı")
st.write("İnternette derinlemesine arama yapabilen kişisel asistanınız.")

# Arama fonksiyonu
def yca_deep_search(query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            
        if not results:
            return "Maalesef bu konuda bir sonuç bulamadım."
        
        output = ""
        first_result = results[0]
        output += f"**[Ana Kaynak]:** {first_result['title']}\n"
        output += f"**Bağlantı:** {first_result['href']}\n"
        output += f"**Özet:** {first_result['body']}\n\n"
        
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            page = requests.get(first_result['href'], headers=headers, timeout=5)
            if page.status_code == 200:
                soup = BeautifulSoup(page.text, 'html.parser')
                paragraphs = soup.find_all('p')
                full_text = " ".join([p.get_text() for p in paragraphs[:5]])
                if full_text.strip():
                    output += f"**Detaylı Analiz:**\n{full_text[:1000]}...\n\n"
        except Exception:
            pass 
            
        output += "**Diğer İlgili Kaynaklar:**\n"
        for i, r in enumerate(results[1:], 2):
            output += f"- [{r['title']}]({r['href']})\n"
            
        return output
    except Exception as e:
        return f"Arama sırasında bir hata oluştu: {e}"

# Sohbet geçmişini saklamak için state yapısı
if "messages" not in st.session_state:
    st.session_state.messages = []

# Geçmiş mesajları ekranda göster
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Kullanıcıdan mesaj al
if user_input := st.chat_input("YCA'ya bir şey yaz... (Örn: ara: voleybol)"):
    # Kullanıcının mesajını ekrana bas ve kaydet
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Asistanın yanıtını üret
    user_input_lower = user_input.lower().strip()
    
    if user_input_lower.startswith("ara:"):
        query = user_input_lower.replace("ara:", "").strip()
        with st.spinner(f"'{query}' derinlemesine araştırılıyor..."):
            response = yca_deep_search(query)
    elif "merhaba" in user_input_lower:
        response = "Merhaba! Ben YCA. Sana nasıl yardımcı olabilirim?"
    elif "saat kaç" in user_input_lower:
        response = f"Şu an saat: {datetime.now().strftime('%H:%M:%S')}"
    elif "çıkış" in user_input_lower:
        response = "Görüşmek üzere!"
    else:
        response = f"Anlaşıldı. '{user_input}' üzerine çalışıyorum."

    # Asistanın yanıtını ekrana bas ve kaydet
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)