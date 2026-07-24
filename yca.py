import json
import os
from datetime import datetime
import streamlit as st
from groq import Groq
from tavily import TavilyClient
from streamlit_mic_recorder import speech_to_text
from gtts import gTTS

# Sayfa Yapılandırması
st.set_page_config(page_title="YCA - Akıllı Hibrit Asistan", page_icon="🤖")

# Hafıza Dosyası Yönetimi (Kalıcı Bellek)
HAFIZA_DOSYASI = "hafiza.json"

def hafizayi_yukle():
    if os.path.exists(HAFIZA_DOSYASI):
        try:
            with open(HAFIZA_DOSYASI, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "sohbet_gecmisi" not in data:
                    data["sohbet_gecmisi"] = []
                return data
        except:
            pass
    return {"sohbet_gecmisi": []}

def hafizayi_kaydet(data):
    with open(HAFIZA_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Hafızayı yükle
hafiza = hafizayi_yukle()

# Groq İstemci Ayarları
groq_api_key = "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"
try:
    if "GROQ_API_KEY" in st.secrets:
        groq_api_key = st.secrets["GROQ_API_KEY"]
except:
    pass

client = Groq(api_key=groq_api_key)

# Tavily İstemci Ayarları
tavily_api_key = "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"  # Kendi Tavily API anahtarını buraya yaz
try:
    if "TAVILY_API_KEY" in st.secrets:
        tavily_api_key = st.secrets["TAVILY_API_KEY"]
except:
    pass

tavily_client = TavilyClient(api_key=tavily_api_key)

st.title("YCA - Akıllı Hibrit Asistan")

# Sohbet Geçmişini Kalıcı Hafızadan Başlat
if "messages" not in st.session_state:
    st.session_state.messages = hafiza["sohbet_gecmisi"]

# Ekrana mesajları yazdır
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Tavily ile İnternette Arama Fonksiyonu
def internetten_bul(sorgu):
    try:
        response = tavily_client.search(query=sorgu, search_depth="advanced", max_results=3)
        results = response.get("results", [])
        if results:
            return "\n".join([f"- {r['title']}: {r['content']}" for r in results])
        return "İnternette güncel bilgi bulunamadı."
    except Exception as e:
        return f"Arama hatası: {e}"

aktif_kaynak = None
prompt = None

# Arayüz Yerleşimi (Mesaj kutusu ve Mikrofon yan yana)
col1, col2 = st.columns([10, 1])

with col1:
    chat_input = st.chat_input("YCA'ya bir şeyler yaz veya mikrofonu kullan...")

with col2:
    sesli_metin = speech_to_text(
        language="tr",
        start_prompt="🎤",
        stop_prompt="⏹️",
        just_once=True,
        key="whatsapp_mic"
    )

if chat_input:
    prompt = chat_input
    aktif_kaynak = "yazi"
elif sesli_metin:
    prompt = sesli_metin
    aktif_kaynak = "ses"

if prompt:
    user_msg = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_msg)
    hafiza["sohbet_gecmisi"] = st.session_state.messages
    hafizayi_kaydet(hafiza)

    with st.chat_message("user"):
        st.markdown(prompt)

    # Güncel tarih bilgisi
    bugun_tarih = datetime.now().strftime("%d %B %Y, %A")

    # Akıllı niyet tespiti: Selamlama dışındaki bilgi taleplerinde arama yap
    temiz_prompt = prompt.lower().strip()
    selamlasmalar = ["merhaba", "selam", "selamın aleyküm", "günaydın", "iyi akşamlar", "nasılsın", "teşekkürler", "sağ ol"]
    
    arama_gerekli_mi = True
    if temiz_prompt in selamlasmalar or len(temiz_prompt) < 3:
        arama_gerekli_mi = False

    baglam = ""
    if arama_gerekli_mi:
        with st.spinner("Tavily ile güncel bilgiler araştırılıyor..."):
            baglam = internetten_bul(prompt)

    sistem_mesaji = (
        f"Sen akıllı ve yardımcısın. Türkçe olarak doğal sohbet et, kullanıcıyı hatırla.\n"
        f"Bugünün tarihi: {bugun_tarih}.\n"
        f"Eğer sana internetten güncel bilgiler verildiyse, bu bilgileri kullanarak kullanıcının sorusuna net, güncel ve doğru yanıtlar ver."
    )
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
                    response_placeholder.markdown(full_response)
                    
            response_placeholder.markdown(full_response)
            
            assistant_msg = {"role": "assistant", "content": full_response}
            st.session_state.messages.append(assistant_msg)
            hafiza["sohbet_gecmisi"] = st.session_state.messages
            hafizayi_kaydet(hafiza)
            
            # Sadece sesli girdilerde gTTS tetiklenir
            if aktif_kaynak == "ses":
                tts = gTTS(text=full_response, lang='tr', tld='com.tr')
                ses_dosyasi = "temp_yanit.mp3"
                tts.save(ses_dosyasi)
                st.audio(ses_dosyasi, format="audio/mp3", autoplay=True)
            
        except Exception as e:
            error_msg = f"Bir hata oluştu: {e}"
            response_placeholder.markdown(error_msg)
