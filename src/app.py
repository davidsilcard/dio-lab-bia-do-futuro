from __future__ import annotations

from pathlib import Path

import streamlit as st

from agent import FinanceAgent, SYSTEM_PROMPT


PROJECT_ROOT = Path(__file__).resolve().parents[1]
AGENT = FinanceAgent(PROJECT_ROOT)


st.set_page_config(page_title="BIA Futuro", page_icon="💰", layout="wide")

st.title("BIA Futuro")
st.caption("Assistente financeiro com respostas ancoradas nos dados mockados do desafio.")

with st.sidebar:
    st.subheader("Contexto do cliente")
    st.write(AGENT.knowledge.context_snapshot())
    st.subheader("Regras de segurança")
    st.code(SYSTEM_PROMPT, language="text")

col1, col2 = st.columns([2, 1])

with col2:
    st.subheader("Perguntas sugeridas")
    for suggestion in AGENT.starter_questions():
        if st.button(suggestion, use_container_width=True):
            st.session_state["pending_prompt"] = suggestion

with col1:
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {
                "role": "assistant",
                "content": (
                    "Posso analisar gastos, metas e produtos financeiros usando apenas a base local. "
                    "Pergunte algo como 'Quanto gastei com alimentação?'"
                ),
            }
        ]

    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sources"):
                st.caption("Fontes: " + ", ".join(message["sources"]))

    prompt = st.chat_input("Digite sua pergunta financeira")
    if not prompt and st.session_state.get("pending_prompt"):
        prompt = st.session_state.pop("pending_prompt")

    if prompt:
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        response = AGENT.respond(prompt)
        assistant_payload = {
            "role": "assistant",
            "content": response.answer,
            "sources": response.sources,
        }
        st.session_state["messages"].append(assistant_payload)

        with st.chat_message("assistant"):
            st.markdown(response.answer)
            st.caption("Fontes: " + ", ".join(response.sources))
