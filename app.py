import streamlit as st
from direct_qa import ask_graph

st.set_page_config(
    page_title="Malayalam Agriculture KG QA",
    page_icon="🌱",
    layout="wide"
)

st.title("🌱 Malayalam Agriculture Knowledge Graph QA")
st.caption("Ask agriculture questions in Malayalam or English")

sample_questions = [
    "പയറിനെ ബാധിക്കുന്ന കീടങ്ങൾ?",
    "കാന്താരിയെ ബാധിക്കുന്ന കീടങ്ങൾ?",
    "കാന്താരിക്ക് വേണ്ട വളങ്ങൾ?",
    "ഇഞ്ചിക്ക് വേണ്ട വളങ്ങൾ?",
    "What pests affect chilli?",
]

question = st.text_input(
    "Ask your question",
    placeholder="പയറിനെ ബാധിക്കുന്ന കീടങ്ങൾ?"
)

st.markdown("### Sample questions")
cols = st.columns(2)
for i, q in enumerate(sample_questions):
    with cols[i % 2]:
        if st.button(q, key=f"sample_{i}"):
            question = q

if st.button("Ask"):
    if question.strip():
        with st.spinner("Searching Knowledge Graph..."):
            answer = ask_graph(question)
        st.text_area("Answer", value=answer, height=220)
    else:
        st.warning("Please enter a question.")
