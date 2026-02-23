
import streamlit as st
import json
from dotenv import load_dotenv
from rag import get_clients, retrieve, generate_answer

load_dotenv()

st.set_page_config(page_title="Leeds AI Policy Advisor", layout="wide")
st.title("Leeds AI Policy Advisor")
st.caption("Evidence-first RAG · AI recommends, humans decide")

question = st.text_input("Ask a policy question:")

if st.button("Ask") and question:
    with st.spinner("Retrieving evidence..."):
        client, index, metadata = get_clients()
        evidence = retrieve(client, index, metadata, question)

    with st.spinner("Generating recommendation..."):
        raw = generate_answer(client, question, evidence)
        data = json.loads(raw)

    st.subheader("Recommendation")
    st.write(data.get("recommendation", ""))

    st.subheader("Confidence")
    st.progress(min(max(float(data.get("confidence", 0)), 0), 1))

    st.subheader("Tradeoffs")
    for t in data.get("tradeoffs", []):
        st.write(f"- {t}")

    st.subheader("Evidence")
    for e in data.get("evidence", []):
        st.markdown(f"**{e['source_id']}** — {e['quote']}")

    st.subheader("Decision Owner")
    st.write(data.get("decision_owner", ""))

    st.subheader("Appeal Path")
    for a in data.get("appeal_path", []):
        st.write(f"- {a}")

    st.subheader("Uncertainties")
    for u in data.get("uncertainties", []):
        st.write(f"- {u}")

    st.subheader("What Would Change My Mind")
    for w in data.get("what_would_change_my_mind", []):
        st.write(f"- {w}")
