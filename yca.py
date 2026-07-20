import streamlit as st
from groq import Groq

# Groq API kurulumu
client = Groq(api_key="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")

st.title("YCA - Kişisel Asistan")

# 1. Sohbet geçmişini saklamak için hafıza oluşturuyoruz
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": """Sen YCA'sın, Cemil'in dijital asistanısın. 
        Sadece Türkçe konuş. 
        Görevin sadece yazılım, teknik destek ve günlük verimlilik konularında yardımcı olmaktır. 
        Duygusal, felsefi, dini veya yas tutma gibi insani duygular içeren konulara girme. 
        Eğer konu dışına çıkılırsa, nazikçe teknik konulara geri dönmeyi teklif et. 
        Her zaman kısa, net ve profesyonel cevaplar ver."""}
    ]

# 2. Önceki konuşmaları ekrana basıyoruz
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 3. Kullanıcıdan yeni mesaj alıyoruz
if prompt := st.chat_input("Mesajını buraya yaz..."):
    # Mesajı geçmişe ekle
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 4. Asistanın cevabını al
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="llama-3-groq-70b-8192-tool-use-preview"
            messages=st.session_state.messages,
        )
        response = stream.choices[0].message.content
        st.markdown(response)
    
    # Cevabı da geçmişe ekle ki bir sonrakini hatırlasın
    st.session_state.messages.append({"role": "assistant", "content": response}) 
