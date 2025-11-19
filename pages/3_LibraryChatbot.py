# pages/3_LibraryChatbot.py
import streamlit as st
from openai import OpenAI

st.title("실습 3 - 부경대 도서관 규정 챗봇")

# ---- 0. 도서관 규정 텍스트 (직접 붙여넣기) ----
LIBRARY_RULES_TEXT = """
여기에 과제 자료에 있는 '부경대학교 중앙도서관 이용 규정' 원문을
그대로 붙여 넣으세요.

예시)
제1조(목적) ...
제2조(이용시간) ...
...
"""

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
    st.warning("먼저 API Key를 입력해주세요.")
    st.stop()

client = OpenAI(api_key=st.session_state["api_key"])

# ---- 1. 히스토리 ----
if "library_chat" not in st.session_state:
    st.session_state["library_chat"] = []

st.info("※ 이 챗봇은 **도서관 규정 텍스트에 있는 내용만** 기준으로 답합니다.")

# 이전 대화 출력
for msg in st.session_state["library_chat"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---- 2. 입력 ----
question = st.chat_input("도서관 이용 관련 질문을 입력하세요.")

if question:
    st.session_state["library_chat"].append(
        {"role": "user", "content": question}
    )
    with st.chat_message("user"):
        st.markdown(question)

    # 시스템 메시지 + 규정 텍스트 + 대화 히스토리
    system_message = {
        "role": "system",
        "content": (
            "너는 '부경대학교 중앙도서관 이용 규정'만을 근거로 "
            "질문에 답하는 챗봇이다. 규정 텍스트에 없는 내용은 "
            "'해당 내용은 규정에 명시되어 있지 않습니다.'라고 답해라.\n\n"
            f"[도서관 규정 전문]\n{LIBRARY_RULES_TEXT}"
        ),
    }

    conversation = [system_message] + [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state["library_chat"]
    ]

    with st.chat_message("assistant"):
        with st.spinner("규정을 확인하는 중입니다..."):
            try:
                response = client.responses.create(
                    model="gpt-5-mini",
                    input=conversation,
                )
                answer = response.output_text
                st.markdown(answer)
            except Exception as e:
                answer = f"에러가 발생했습니다: {e}"
                st.error(answer)

    st.session_state["library_chat"].append(
        {"role": "assistant", "content": answer}
    )

# ---- 3. 초기화 버튼 ----
if st.button("대화 초기화"):
    st.session_state["library_chat"] = []
    st.success("도서관 챗봇 대화를 초기화했습니다.")


