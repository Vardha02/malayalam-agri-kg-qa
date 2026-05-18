import streamlit as st
from direct_qa import ask_graph

st.set_page_config(
    page_title="Malayalam Agriculture KG QA",
    layout="wide"
)

st.title("🌱 Malayalam Agriculture Knowledge Graph QA")
st.caption("Ask agriculture questions in Malayalam or English")

question = st.text_input(
    "Ask your question",
    placeholder="കാന്താരിയെ ബാധിക്കുന്ന കീടങ്ങൾ?"
)

if st.button("Ask"):
    if question.strip():
        with st.spinner("Searching Knowledge Graph..."):
            answer = ask_graph(question)
            st.success(answer)