import json
import os
import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS

# Sayfa Yapılandırması
st.set_page_config(page_title="YCA - Akıllı Hibrit Asistan", page_icon="🤖")

# Hafıza Dosyası Yönetimi (Kalıcı Bellek)
HAFIZA_DOSYASI = "hafiza.json"

def hafizayi_yukle():
    if os.path.exists(HAFIZA_DOSYASI):
        try:
            with open(HAFIZA_DOSYASI, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "ogrenilen_sorular" not in data:
                    data["ogrenilen_sorular"] = {}
                if "sohbet_gecmisi" not in data:
                    data["sohbet_gecmisi"] = []
                return data
        except:
            pass
    return {"ogrenilen_sorular": {}, "sohbet_gecmisi": []}

def hafizayi_kaydet(data):
    with open(HAFIZA_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Hafızayı yükle
hafiza = hafizayi_yukle()

# Groq İstemci Ayarları
api_key = "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" # Kendi anahtarın
try:
    if "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
except:
    pass

client = Groq(api_key=api_key)

st.title("YCA - Akıllı Hibrit Asistan")

# Sohbet Geçmişini Kalıcı Hafızadan Başlat
if "messages" not in st.session_state:
    st.session_state.messages = hafiza["sohbet_gecmisi"]

# Ekrana mesajları yazdır
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# İnternette Arama Fonksiyonu
def internetten_bul(sorgu):
    try:
        results = DDGS().text(sorgu, region="tr-tr", max_results=3)
        return "\n".join([r['body'] for r in results]) if results else "Bilgi bulunamadı."
    except Exception as e:
        return f"Arama hatası: {e}"

# Kullanıcı Girdisi
if prompt := st.chat_input("YCA'ya bir şeyler yaz..."):
    # Kullanıcı mesajını ekle ve hafızaya kaydet
    user_msg = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_msg)
    hafiza["sohbet_gecmisi"] = st.session_state.messages
    hafizayi_kaydet(hafiza)

    with st.chat_message("user"):
        st.markdown(prompt)

    # 1. Aşama: Hafıza Kontrolü (Niyet Tespiti)
    temiz_prompt = prompt.lower().strip()
    arama_gerekli_mi = False

    if temiz_prompt in hafiza["ogrenilen_sorular"]:
        arama_gerekli_mi = hafiza["ogrenilen_sorular"][temiz_prompt]
    else:
        # İlk defa karşılaşılan sorular için varsayılan akış (istersen sonradan değiştirebilirsin)
        arama_gerekli_mi = False 
        hafiza["ogrenilen_sorular"][temiz_prompt] = arama_gerekli_mi
        hafizayi_kaydet(hafiza)

    # 2. Aşama: Karara Göre Bilgi Toplama
    baglam = ""
    if arama_gerekli_mi:
        with st.spinner("İnternette araştırılıyor..."):
            baglam = internetten_bul(prompt)

    # 3. Aşama: Yanıt Üretme
    sistem_mesaji = "Sen akıllı ve yardımcısın. Kullanıcıyı hatırla ve ona göre doğal sohbet et."
    if baglam:
        sistem_mesaji += f"\n\nİnternetten elde edilen güncel bilgiler:\n{baglam}"

    mesaj_listesi = [{"role": "system", "content": sistem_mesaji}] + st.session_state.messages

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=mesaj_listesi,
                stream=True
            )
            
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_placeholder.markdown(full_response + "▌")
                    
            response_placeholder.markdown(full_response)
            
            # Asistanın yanıtını da kalıcı hafızaya ekle
            assistant_msg = {"role": "assistant", "content": full_response}
            st.session_state.messages.append(assistant_msg)
            hafiza["sohbet_gecmisi"] = st.session_state.messages
            hafizayi_kaydet(hafiza)
            
        except Exception as e:
            error_msg = f"Bir hata oluştu: {e}"
            response_placeholder.markdown(error_msg)
