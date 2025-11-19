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


