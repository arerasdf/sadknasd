# pages/4_ChatPDF.py
import streamlit as st
from openai import OpenAI

st.title("실습 4 - ChatPDF (PDF + Vector Store)")

# ---- 1. API Key ----
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

# ---- 2. 세션 상태 초기화 ----
if "vector_store_id" not in st.session_state:
    st.session_state["vector_store_id"] = None
if "chatpdf_messages" not in st.session_state:
    st.session_state["chatpdf_messages"] = []


# ---- 3. PDF 업로드 & 벡터 스토어 생성 ----
st.subheader("1) PDF 업로드")

uploaded_files = st.file_uploader(
    "질문하고 싶은 PDF 파일을 업로드하세요.",
    type=["pdf"],
    accept_multiple_files=True,
)

col1, col2 = st.columns(2)

with col1:
    create_vs_btn = st.button("벡터 스토어 만들기 / 새로 만들기")
with col2:
    clear_vs_btn = st.button("벡터 스토어 삭제 및 대화 초기화")

# 벡터 스토어 삭제
if clear_vs_btn:
    vs_id = st.session_state.get("vector_store_id")
    if vs_id:
        try:
            client.vector_stores.delete(vector_store_id=vs_id)
            st.success(f"벡터 스토어({vs_id})를 삭제했습니다.")
        except Exception as e:
            st.warning(f"벡터 스토어 삭제 중 오류: {e}")
    st.session_state["vector_store_id"] = None
    st.session_state["chatpdf_messages"] = []

# 벡터 스토어 생성
if create_vs_btn:
    if not uploaded_files:
        st.error("먼저 PDF 파일을 하나 이상 업로드하세요.")
    else:
        try:
            st.write("벡터 스토어를 생성하고 파일을 업로드 중입니다...")
            vector_store = client.vector_stores.create(name="ChatPDF Store")

            # 업로드한 PDF들을 OpenAI 파일로 올린 뒤 벡터 스토어에 추가
            for uf in uploaded_files:
                # Streamlit UploadedFile은 file-like 객체라 바로 사용 가능
                file_obj = client.files.create(
                    file=uf,
                    purpose="assistants",  # 파일 검색/벡터 스토어용
                )

                client.vector_stores.files.create(
                    vector_store_id=vector_store.id,
                    file_id=file_obj.id,
                )

            st.session_state["vector_store_id"] = vector_store.id
            st.success(f"벡터 스토어 생성 완료! id = {vector_store.id}")
        except Exception as e:
            st.error(f"벡터 스토어 생성 중 에러: {e}")

# 현재 벡터 스토어 상태 표시
if st.session_state["vector_store_id"]:
    st.info(f"현재 사용 중인 Vector Store ID: **{st.session_state['vector_store_id']}**")
else:
    st.warning("아직 활성화된 벡터 스토어가 없습니다. PDF 업로드 후 벡터 스토어를 만들어 주세요.")

st.markdown("---")

# ---- 4. ChatPDF Q&A ----
st.subheader("2) PDF 내용에 대해 질문하기")

# 이전 메시지 보여주기
for msg in st.session_state["chatpdf_messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

question = st.chat_input("PDF 내용에 대해 질문을 입력하세요.")

if question:
    if not st.session_state["vector_store_id"]:
        st.error("먼저 PDF를 업로드하고 벡터 스토어를 생성하세요.")
    else:
        # 히스토리에 사용자 질문 추가
        st.session_state["chatpdf_messages"].append(
            {"role": "user", "content": question}
        )
        with st.chat_message("user"):
            st.markdown(question)

        # system + 히스토리 메시지
        system_msg = {
            "role": "system",
            "content": (
                "너는 사용자가 업로드한 PDF 파일들만을 기반으로 답을 제공하는 어시스턴트이다. "
                "PDF에 나오지 않는 내용은 추측하지 말고 'PDF에 없는 내용입니다.'라고 답해라."
            ),
        }
        messages = [system_msg] + [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state["chatpdf_messages"]
        ]

        with st.chat_message("assistant"):
            with st.spinner("PDF에서 답을 찾는 중입니다..."):
                try:
                    response = client.responses.create(
                        model="gpt-5-mini",
                        input=messages,
                        tools=[
                            {
                                "type": "file_search",
                                "vector_store_ids": [
                                    st.session_state["vector_store_id"]
                                ],
                                # 필요하면 max_num_results 등 옵션 추가 가능
                            }
                        ],
                    )
                    answer = response.output_text
                    st.markdown(answer)
                except Exception as e:
                    answer = f"에러가 발생했습니다: {e}"
                    st.error(answer)

        # 답변도 히스토리에 저장
        st.session_state["chatpdf_messages"].append(
            {"role": "assistant", "content": answer}
        )


