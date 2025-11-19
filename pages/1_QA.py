# streamlit_app.py
import streamlit as st

st.set_page_config(page_title="21_Lab Streamlit App", page_icon="💻")

st.title("21_Lab Streamlit 실습 앱")

st.write(
    """
왼쪽 사이드바에서 페이지를 선택해서 실습을 진행하세요.

- 1_QA: gpt-5-mini Q&A
- 2_Chat: Chat 페이지
- 3_LibraryChatbot: 도서관 규정 챗봇
- 4_ChatPDF: PDF 기반 챗봇
"""
)

# pages/1_QA.py
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Q&A with gpt-5-mini", page_icon="❓")

st.title("실습 1 - gpt-5-mini Q&A")

# 1) session_state에 API Key 보관 -----------------------------
if "api_key" not in st.session_state:
    st.session_state["api_key"] = ""

api_key_input = st.text_input(
    "OpenAI API Key를 입력하세요",
    type="password",
    value=st.session_state["api_key"],
    help="이 값은 현재 세션 내에서만 사용됩니다."
)

# 입력이 변경되면 session_state에 저장
if api_key_input != st.session_state["api_key"]:
    st.session_state["api_key"] = api_key_input

# 2) 캐시된 호출 함수 -----------------------------------------
@st.cache_data
def ask_gpt(api_key: str, question: str) -> str:
    """
    같은 (api_key, question) 쌍으로 다시 호출하면
    OpenAI API를 다시 부르지 않고 캐시된 결과를 사용합니다.
    """
    client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model="gpt-5-mini",
        input=question,
    )

    return response.output_text

# 3) 사용자 질문 입력 + 버튼 ------------------------------------
st.subheader("질문을 입력하세요")

question = st.text_area("질문", placeholder="예) 인공지능과 스트림릿의 차이점은 뭐야?")

col1, col2 = st.columns([1, 3])

with col1:
    run_button = st.button("질문 보내기")

if run_button:
    if not st.session_state["api_key"]:
        st.error("먼저 OpenAI API Key를 입력해주세요.")
    elif not question.strip():
        st.error("질문을 입력해주세요.")
    else:
        with st.spinner("모델이 생각 중입니다..."):
            try:
                answer = ask_gpt(st.session_state["api_key"], question)
                st.markdown("### 답변")
                st.write(answer)
            except Exception as e:
                st.error(f"에러가 발생했습니다: {e}")

