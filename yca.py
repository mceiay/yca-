import json
import os
from datetime import datetime
import streamlit as st
import requests
from groq import Groq
from tavily import TavilyClient
from streamlit_mic_recorder import speech_to_text
from gtts import gTTS
from authlib.integrations.requests_client import OAuth2Session
from PIL import Image
from google import genai

# Sayfa Yapılandırması
st.set_page_config(page_title="YCA - Akıllı Hibrit Asistan", page_icon="🤖")

# --- GOOGLE OAUTH KİMLİK DOĞRULAMA KONTROLÜ ---
client_id = st.secrets["google_oauth"]["client_id"]
client_secret = st.secrets["google_oauth"]["client_secret"]
redirect_uri = st.secrets["google_oauth"]["redirect_uri"]

AUTHORIZATION_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
USERINFO_ENDPOINT = "https://www.googleapis.com/oauth2/v3/userinfo"

if "user" not in st.session_state:
    st.session_state.user = None

oauth = OAuth2Session(client_id, client_secret, scope="openid email profile")

if not st.session_state.user:
    st.title("YCA - Akıllı Hibrit Asistan")
    st.write("Devam etmek için lütfen Google hesabınızla giriş yapın.")

    query_params = st.query_params
    if "code" in query_params:
        code = query_params["code"]
        try:
            token_data = {
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code"
            }
            token_response = requests.post(
                TOKEN_ENDPOINT, 
                data=token_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            token_json = token_response.json()

            if "access_token" in token_json:
                headers = {"Authorization": f"Bearer {token_json['access_token']}"}
                user_resp = requests.get(USERINFO_ENDPOINT, headers=headers)
                user_info = user_resp.json()
                
                if user_info and isinstance(user_info, dict):
                    st.session_state.user = user_info
                    st.query_params.clear()
                    st.rerun()
                else:
                    st.error("Google'dan kullanıcı bilgileri alınamadı.")
            else:
                error_desc = token_json.get('error_description', token_json.get('error', 'Bilinmeyen hata'))
                st.error(f"Google Token Hatası: {error_desc}")
        except Exception as e:
            st.error(f"Giriş sırasında bir hata oluştu: {e}")

    uri, state = oauth.create_authorization_url(
        AUTHORIZATION_ENDPOINT, 
        redirect_uri=redirect_uri,
        prompt="consent"
    )
    st.link_button("🔐 Google ile Giriş Yap", uri)
    st.stop()

# --- GİRİŞ BAŞARILI İSE DEVAM EDEN ASİSTAN KODLARI ---
user = st.session_state.user

if not user or not isinstance(user, dict):
    st.session_state.user = None
    st.rerun()

user_email = user.get("email", "varsayilan_kullanici")
safe_email_filename = "".join([c if c.isalnum() else "_" for c in user_email])
HAFIZA_DOSYASI = f"hafiza_{safe_email_filename}.json"

st.sidebar.success(f"Giriş yapıldı:\n{user.get('name', 'Kullanıcı')}\n({user_email})")

if st.sidebar.button("Çıkış Yap"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.query_params.clear()
    st.rerun()

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

hafiza = hafizayi_yukle()

groq_api_key = st.secrets.get("GROQ_API_KEY", "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")
client = Groq(api_key=groq_api_key)

tavily_api_key = st.secrets.get("TAVILY_API_KEY", "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")
tavily_client = TavilyClient(api_key=tavily_api_key)

gemini_api_key = st.secrets.get("GEMINI_API_KEY", "AQ.Ab8RN6JxgCkBuMSrGCmwgminDf5DTINJzBVnI3_-VwHds43tIg")

st.title("YCA - Akıllı Hibrit Asistan")

app_mode = st.sidebar.radio("Mod Seçimi", ["💬 Sohbet & Asistan", "📷 Kamera & Nesne Tanıma (Vision)"])

if app_mode == "💬 Sohbet & Asistan":
    if "messages" not in st.session_state:
        st.session_state.messages = hafiza["sohbet_gecmisi"]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

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

        bugun_tarih = datetime.now().strftime("%d %B %Y, %A")

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
                
                if aktif_kaynak == "ses":
                    tts = gTTS(text=full_response, lang='tr', tld='com.tr')
                    ses_dosyasi = "temp_yanit.mp3"
                    tts.save(ses_dosyasi)
                    st.audio(ses_dosyasi, format="audio/mp3", autoplay=True)
                
            except Exception as e:
                error_msg = f"Bir hata oluştu: {e}"
                response_placeholder.markdown(error_msg)

elif app_mode == "📷 Kamera & Nesne Tanıma (Vision)":
    st.subheader("YCA Vision - Gerçek Zamanlı Nesne ve Görsel Analizi")
    st.write("Kameradan bir fotoğraf çekerek veya nesne göstererek analiz ettirebilirsiniz.")

    camera_file = st.camera_input("Fotoğraf Çek", key="yca_vision_camera")

    if camera_file is not None:
        image = Image.open(camera_file)
        st.image(image, caption="Yakalanan Görüntü", use_container_width=True)
        
        vision_prompt = st.text_input("Görsel hakkında ne öğrenmek istiyorsun?", "Bu fotoğrafın içinde ne var, detaylı açıkla.", key="vision_prompt_input")
        
        if st.button("Görseli Analiz Et", key="vision_analyze_btn"):
            if not gemini_api_key:
                st.error("Streamlit Secrets içinde `GEMINI_API_KEY` tanımlı değil!")
            else:
                with st.spinner("Görsel analiz ediliyor..."):
                    try:
                        # Yeni nesil google-genai kütüphanesi istemci yapısı (OAuth ve API anahtarı çakışmasını engeller)
                        gemini_client = genai.Client(api_key=gemini_api_key)
                        response = gemini_client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=[vision_prompt, image]
                        )
                        
                        st.success("Analiz Başarılı!")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"Görsel analiz edilirken hata oluştu: {e}")
