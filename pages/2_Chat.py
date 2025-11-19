# pages/2_Chat.py
import streamlit as st
from openai import OpenAI

st.title("실습 2 - Chat 페이지")

# ---- 1. API Key 세션에 유지 ----
if "api_key" not in st.session_state:
    st.session_state["api_key"] = ""

api_key_input = st.text_input(
    "OpenAI API Key를 입력하세요",
    type="password",
    value=st.session_state["api_key"],
)

if api_key_input != st.session_state["api_key"]:
    st.session_state["api_key"] = api_key_input

if not st.session_state["api_key"]:
    st.warning("왼쪽에 API Key를 먼저 입력해주세요.")
    st.stop()

client = OpenAI(api_key=st.session_state["api_key"])

# ---- 2. 대화 히스토리 세션에 저장 ----
if "chat_messages" not in st.session_state:
    # role: "user" 또는 "assistant"
    st.session_state["chat_messages"] = []

st.write("gpt-5-mini와 자유롭게 대화해 보세요.")

# 이전 대화 내용 출력
for msg in st.session_state["chat_messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---- 3. 사용자 입력 ----
user_input = st.chat_input("메시지를 입력하세요.")

if user_input:
    # (1) 먼저 사용자 메시지 화면/히스토리에 추가
    st.session_state["chat_messages"].append(
        {"role": "user", "content": user_input}
    )
    with st.chat_message("user"):
        st.markdown(user_input)

    # (2) 전체 대화를 Responses API 형식으로 변환
    input_messages = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state["chat_messages"]
    ]

    # (3) 모델 호출
    with st.chat_message("assistant"):
        with st.spinner("생각 중..."):
            try:
                response = client.responses.create(
                    model="gpt-5-mini",
                    input=input_messages,
                )
                answer = response.output_text
                st.markdown(answer)
            except Exception as e:
                answer = f"에러가 발생했습니다: {e}"
                st.error(answer)

    # (4) 응답도 히스토리에 추가
    st.session_state["chat_messages"].append(
        {"role": "assistant", "content": answer}
    )

# ---- 4. 대화 초기화 버튼 ----
if st.button("대화 내용 지우기"):
    st.session_state["chat_messages"] = []
    st.success("대화를 초기화했습니다.")


