import streamlit as st
import json
import os
from groq import Groq
from duckduckgo_search import DDGS

# 1. Ayarlar
client = Groq(api_key="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") 
HAFIZA_DOSYASI = "hafiza.json"

def hafizayi_yukle():
    if os.path.exists(HAFIZA_DOSYASI):
        with open(HAFIZA_DOSYASI, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"isim": None, "bilgiler": []}

def hafizayi_kaydet(data):
    with open(HAFIZA_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def internetten_bul(soru):
    try:
        # Sorguyu daha net hale getiriyoruz
        with DDGS() as ddgs:
            results = list(ddgs.text(soru, max_results=3))
            if results:
                return "\n".join([f"- {r['title']}: {r['body']}" for r in results])
        return "Güncel bilgi bulunamadı."
    except Exception as e:
        return f"Arama hatası: {str(e)}"

# Session State Başlatma
if "user_data" not in st.session_state:
    st.session_state.user_data = hafizayi_yukle()
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("YCA - Kişisel Asistan")

# İsim sorgulama
if st.session_state.user_data["isim"] is None:
    st.write("Merhaba! İsmin nedir?")
    if isim := st.chat_input("İsmin..."):
        st.session_state.user_data["isim"] = isim
        hafizayi_kaydet(st.session_state.user_data)
        st.reron() if hasattr(st, "reron") else st.rerun()
else:
    # Sohbet geçmişini yazdır
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Sohbet et..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Hafıza güncelleme
        if any(kelime in prompt.lower() for kelime in ["seviyorum", "hoşlanırım", "ilgileniyorum"]):
            st.session_state.user_data["bilgiler"].append(prompt)
            hafizayi_kaydet(st.session_state.user_data)

        # GÜNCEL VERİ ÇEKME - Artık her soru için doğrudan arama yapılıyor ki kaçırma olasılığı olmasın
        with st.spinner("Güncel bilgiler aranıyor..."):
            guncel_veri = internetten_bul(prompt)

        # System Prompt
        bilinenler = ", ".join(st.session_state.user_data["bilgiler"])
        
        system_prompt = f"""Sen YCA'sın. Karşındaki kişi: {st.session_state.user_data['isim']}.
Hakkında bildiklerin: {bilinenler}.

ELİNDEKİ GÜNCEL BİLGİ: {guncel_veri}

KURALLAR:
1. Sadece yukarıdaki 'ELİNDEKİ GÜNCEL BİLGİ' kısmındaki verileri kullanarak cevap ver.
2. Eğer veri 'Güncel bilgi bulunamadı' veya 'Arama hatası' içeriyorsa, asla uydurma. Doğrudan 'Bu konuda şu an güncel bir bilgiye ulaşamıyorum' de.
3. Asla 'İnternette arama yaptım' veya 'Bulduğum sonuçlara göre' gibi yapay cümleler kurma. Doğal bir arkadaş gibi doğrudan cevap ver."""

        context = [{"role": "system", "content": system_prompt}] + st.session_state.messages
        
        completion = client.chat.completions.create(messages=context, model="llama-3.3-70b-versatile")
        cevap = completion.choices[0].message.content
        
        st.session_state.messages.append({"role": "assistant", "content": cevap})
        with st.chat_message("assistant"):
            st.markdown(cevap)
