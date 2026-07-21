import streamlit as st
import json
import os
from groq import Groq
from duckduckgo_search import DDGS

# 1. Ayarlar
client = Groq(api_key="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")  # Kendi Groq API anahtarını buraya yaz
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
        with DDGS() as ddgs:
            hedef_sorgu = f"{soru} maç sonucu özet"
            results = list(ddgs.text(hedef_sorgu, max_results=6, region="tr-tr", backend="api"))
            if results:
                metin = ""
                linkler = []
                for r in results:
                    title = r.get('title', '')
                    body = r.get('body', '')
                    href = r.get('href', '')
                    
                    yasakli_kelimeler = ["duckduckgo.com", "bing.com", "google.com", "kick.com", "twitch.tv", "eksisozluk.com", "reddit.com"]
                    if href and not any(yasakli in href.lower() for yasakli in yasakli_kelimeler):
                        metin += f"- {title}: {body}\n"
                        linkler.append((title, href))
                
                secilenler = linkler[:2] if linkler else [(r['title'], r['href']) for r in results[:2] if 'href' in r]
                return metin, secilenler
        return "Güncel haber bulunamadı.", []
    except Exception as e:
        return f"Arama hatası: {str(e)}", []

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
        st.rerun()
else:
    # Sohbet geçmişini yazdır
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "links" in msg and msg["links"]:
                st.markdown("**Kaynaklar:**")
                for title, href in msg["links"]:
                    st.markdown(f"- [{title}]({href})")

    if prompt := st.chat_input("Sohbet et veya haber sor..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Hafıza güncelleme
        if any(kelime in prompt.lower() for kelime in ["seviyorum", "hoşlanırım", "ilgileniyorum"]):
            st.session_state.user_data["bilgiler"].append(prompt)
            hafizayi_kaydet(st.session_state.user_data)

        # Güncel Veri / Haber Çekme (Sadece bilgi/haber sorulduğunda arama yap)
        guncel_veri, kaynak_listesi = "", []
        sohbet_kelimeleri = ["nasılsın", "merhaba", "selam", "naber", "iyi misin", "günaydın", "iyi akşamlar"]
        
        if not any(k in prompt.lower() for k in sohbet_kelimeleri):
            with st.spinner("Haberler ve kaynaklar taranıyor..."):
                guncel_veri, kaynak_listesi = internetten_bul(prompt)

        bilinenler = ", ".join(st.session_state.user_data["bilgiler"])
        
        system_prompt = f"""Sen YCA'sın. Karşındaki kişi: {st.session_state.user_data['isim']}.
Hakkında bildiklerin: {bilinenler}.

ELİNDEKİ GÜNCEL BİLGİ/HABERLER: {guncel_veri}

KESİN KURALLAR:
1. Türkçe dilbilgisi kurallarına, akıcılığa ve doğallığa son derece dikkat et. Cümlelerin kopuk, bozuk veya çeviri kokan bir yapıda olması kesinlikle yasaktır.
2. İnternetten gelen verileri tamamen özümseyip kullanıcıya kusursuz ve anlaşılır bir Türkçe ile aktar.
3. Kullanıcıya doğal bir arkadaş gibi samimi, akıcı ve net bir dille hitap et.
4. Asla 'İnternette arama yaptım' veya 'Bulduğum sonuçlara göre' gibi robotik ifadeler kullanma."""

        clean_context = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
        context = [{"role": "system", "content": system_prompt}] + clean_context
        
        completion = client.chat.completions.create(messages=context, model="llama-3.3-70b-versatile")
        cevap = completion.choices[0].message.content
        
        st.session_state.messages.append({
            "role": "assistant", 
            "content": cevap,
            "links": kaynak_listesi
        })

        with st.chat_message("assistant"):
            st.markdown(cevap)
            if kaynak_listesi:
                st.markdown("**Kaynaklar:**")
                for title, href in kaynak_listesi:
                    st.markdown(f"- [{title}]({href})")
