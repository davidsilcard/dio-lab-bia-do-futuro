from __future__ import annotations

from pathlib import Path

import streamlit as st

from agent import FinanceAgent, SYSTEM_PROMPT


PROJECT_ROOT = Path(__file__).resolve().parents[1]
AGENT = FinanceAgent(PROJECT_ROOT)


st.set_page_config(page_title="BIA Futuro", page_icon="💰", layout="wide")

st.markdown(
    """
    <style>
    .insight-card, .evidence-card {
        border: 1px solid rgba(49, 51, 63, 0.12);
        border-radius: 16px;
        padding: 1rem;
        background: linear-gradient(180deg, #ffffff 0%, #f7f9fc 100%);
        min-height: 132px;
        margin-bottom: 0.75rem;
    }
    .insight-title, .evidence-title {
        font-size: 0.85rem;
        color: #5b6577;
        margin-bottom: 0.35rem;
    }
    .insight-value {
        font-size: 1.15rem;
        font-weight: 700;
        color: #16325c;
        margin-bottom: 0.35rem;
    }
    .insight-detail, .evidence-detail {
        font-size: 0.9rem;
        color: #4b5563;
    }
    .evidence-value {
        display: inline-block;
        padding: 0.2rem 0.55rem;
        border-radius: 999px;
        background: #e8f3ff;
        color: #125ea8;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("BIA Futuro")
st.caption("Assistente financeiro com respostas ancoradas nos dados mockados do desafio.")

st.subheader("Insights proativos")
insight_cols = st.columns(3)
for column, insight in zip(insight_cols, AGENT.knowledge.proactive_insights()):
    column.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-title">{insight['title']}</div>
            <div class="insight-value">{insight['value']}</div>
            <div class="insight-detail">{insight['detail']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with st.sidebar:
    st.subheader("Contexto do cliente")
    st.write(AGENT.knowledge.context_snapshot())
    st.subheader("Regras de seguranca")
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
                    "Pergunte algo como 'Quanto gastei com alimentacao?'"
                ),
                "evidence_label": "Base local",
                "next_step": "Use as perguntas sugeridas para explorar a situacao financeira do cliente.",
            }
        ]

    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("evidence_label"):
                st.markdown(
                    f"""
                    <div class="evidence-card">
                        <div class="evidence-title">Evidencia da resposta</div>
                        <div class="evidence-value">{message["evidence_label"]}</div>
                        <div class="evidence-detail">{message.get("next_step", "")}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
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
            "evidence_label": response.evidence_label,
            "next_step": response.next_step,
        }
        st.session_state["messages"].append(assistant_payload)

        with st.chat_message("assistant"):
            st.markdown(response.answer)
            st.markdown(
                f"""
                <div class="evidence-card">
                    <div class="evidence-title">Evidencia da resposta</div>
                    <div class="evidence-value">{response.evidence_label}</div>
                    <div class="evidence-detail">{response.next_step or ""}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.caption("Fontes: " + ", ".join(response.sources))
