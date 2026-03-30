from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from knowledge_base import KnowledgeBase, format_brl


SYSTEM_PROMPT = """\
Voce e a BIA Futuro, uma assistente financeira consultiva e prudente.
Seu trabalho e orientar o cliente usando apenas os dados carregados localmente.

Regras:
1. Nunca invente valores, produtos, datas ou politicas que nao estejam na base local.
2. Sempre explique de onde veio a resposta: perfil, transacoes, historico ou catalogo de produtos.
3. Priorize seguranca financeira, reserva de emergencia e aderencia ao perfil do investidor.
4. Se a pergunta estiver fora do escopo financeiro ou sem base de dados suficiente, diga isso claramente.
5. Nao peca nem revele dados sensiveis. Nao faca promessas de rentabilidade futura.
"""


@dataclass
class AgentResponse:
    answer: str
    sources: list[str]
    safe: bool = True
    evidence_label: str = "Base local"
    next_step: str | None = None


class FinanceAgent:
    def __init__(self, project_root: Path) -> None:
        self.knowledge = KnowledgeBase(project_root)

    def respond(self, user_message: str) -> AgentResponse:
        normalized = user_message.lower()

        if self._is_out_of_scope(normalized):
            return AgentResponse(
                answer=(
                    "Posso ajudar apenas com financas pessoais deste cliente ficticio. "
                    "Se quiser, posso analisar gastos, metas, reserva de emergencia ou sugerir produtos compativeis."
                ),
                sources=["Regras do agente"],
                evidence_label="Fora de escopo",
                next_step="Pergunte sobre gastos, metas, perfil ou produtos financeiros.",
            )

        if "aliment" in normalized:
            return self._answer_category_spending("alimentacao", "alimentacao")
        if "moradia" in normalized or "aluguel" in normalized:
            return self._answer_category_spending("moradia", "moradia")
        if "transporte" in normalized or "uber" in normalized or "combust" in normalized:
            return self._answer_category_spending("transporte", "transporte")
        if "saude" in normalized or "farm" in normalized or "academia" in normalized:
            return self._answer_category_spending("saude", "saude")
        if "resumo" in normalized or "gastei no mes" in normalized:
            return self._answer_monthly_summary()
        if "reserva" in normalized or "meta" in normalized:
            return self._answer_goal_progress()
        if "invest" in normalized or "produto" in normalized or "aplicar" in normalized or "recomenda" in normalized:
            return self._answer_recommendation()
        if "atendimento" in normalized or "historico" in normalized:
            return self._answer_service_history()
        if "perfil" in normalized:
            return self._answer_profile()

        return AgentResponse(
            answer=(
                "Nao encontrei base suficiente para responder isso com seguranca. "
                "Tente perguntar sobre gastos por categoria, resumo mensal, metas, perfil ou recomendacoes de produtos."
            ),
            sources=["Regras do agente"],
            safe=False,
            evidence_label="Sem base suficiente",
            next_step="Use uma das perguntas sugeridas para continuar a analise.",
        )

    def starter_questions(self) -> list[str]:
        return [
            "Quanto gastei com alimentacao?",
            "Como esta minha reserva de emergencia?",
            "Qual produto combina com meu perfil?",
            "Me de um resumo financeiro do mes.",
        ]

    def _answer_category_spending(self, category_key: str, category_label: str) -> AgentResponse:
        transactions = self.knowledge.list_transactions(category=category_key)
        total = self.knowledge.sum_transactions(category=category_key)

        if not transactions:
            return AgentResponse(
                answer=f"Nao encontrei transacoes da categoria {category_label} na base atual.",
                sources=["data/transacoes.csv"],
                evidence_label="Baseado em transacoes",
                next_step="Posso comparar outra categoria de gasto se voce quiser.",
            )

        details = "; ".join(
            f"{item['data']}: {item['descricao']} ({format_brl(float(item['valor']))})"
            for item in transactions
        )
        return AgentResponse(
            answer=(
                f"No periodo carregado, voce gastou {format_brl(total)} com {category_label}. "
                f"Lancamentos considerados: {details}."
            ),
            sources=["data/transacoes.csv"],
            evidence_label="Baseado em transacoes",
            next_step="Se quiser, eu tambem posso resumir o mes inteiro ou comparar outra categoria.",
        )

    def _answer_monthly_summary(self) -> AgentResponse:
        income = self.knowledge.sum_transactions(kind="entrada")
        expenses = self.knowledge.sum_transactions(kind="saida")
        balance = self.knowledge.monthly_balance()
        top_category, top_value = self.knowledge.top_spending_category()

        return AgentResponse(
            answer=(
                f"Seu resumo do periodo mostra receitas de {format_brl(income)}, despesas de {format_brl(expenses)} "
                f"e saldo estimado de {format_brl(balance)}. "
                f"A maior categoria de gasto foi {top_category}, com {format_brl(top_value)}. "
                f"Isso sugere espaco para revisar despesas variaveis antes de aumentar o risco dos investimentos."
            ),
            sources=["data/transacoes.csv", "data/perfil_investidor.json"],
            evidence_label="Baseado em transacoes e perfil",
            next_step="O proximo passo prudente e revisar a reserva de emergencia antes de buscar mais risco.",
        )

    def _answer_goal_progress(self) -> AgentResponse:
        gap = self.knowledge.emergency_fund_gap()
        current = float(self.knowledge.profile["reserva_emergencia_atual"])
        monthly_balance = self.knowledge.monthly_balance()

        if gap == 0:
            status = "Sua reserva de emergencia ja atingiu a meta definida na base."
        else:
            status = (
                f"Faltam {format_brl(gap)} para completar a meta da reserva de emergencia. "
                f"O valor atual registrado e {format_brl(current)}."
            )

        suggestion = (
            f"Com o saldo mensal estimado de {format_brl(monthly_balance)}, "
            "priorizar aportes em liquidez diaria e a estrategia mais prudente neste momento."
        )

        return AgentResponse(
            answer=f"{status} {suggestion}",
            sources=["data/perfil_investidor.json", "data/transacoes.csv"],
            evidence_label="Baseado em metas e saldo mensal",
            next_step="Posso sugerir os produtos mais adequados para completar essa reserva.",
        )

    def _answer_recommendation(self) -> AgentResponse:
        profile = self.knowledge.profile
        recommendations = self.knowledge.recommend_products()
        lines = []

        for product in recommendations:
            lines.append(
                f"{product['nome']}: risco {product['risco']}, aporte minimo de "
                f"{format_brl(float(product['aporte_minimo']))}, indicado para {product['indicado_para'].lower()}."
            )

        rationale = (
            f"Como o perfil e {profile['perfil_investidor']} e o objetivo principal e "
            f"'{profile['objetivo_principal']}', priorizei produtos de menor risco e boa liquidez."
        )

        return AgentResponse(
            answer=f"{rationale} Recomendacoes: {' '.join(lines)}",
            sources=["data/perfil_investidor.json", "data/produtos_financeiros.json"],
            evidence_label="Baseado em perfil e catalogo de produtos",
            next_step="Se quiser, posso explicar por que descartei produtos mais arriscados.",
        )

    def _answer_service_history(self) -> AgentResponse:
        latest = self.knowledge.service_history[-3:]
        details = "; ".join(
            f"{item['data']} via {item['canal']}: {item['tema']}" for item in latest
        )
        return AgentResponse(
            answer=(
                "Os ultimos atendimentos registrados mostram interesse recorrente em investimentos conservadores "
                f"e metas financeiras. Registros recentes: {details}."
            ),
            sources=["data/historico_atendimento.csv"],
            evidence_label="Baseado em historico de atendimento",
            next_step="Posso conectar esse historico ao seu perfil atual e aos produtos recomendados.",
        )

    def _answer_profile(self) -> AgentResponse:
        profile = self.knowledge.profile
        return AgentResponse(
            answer=(
                f"O cliente {profile['nome']} tem {profile['idade']} anos, renda mensal de "
                f"{format_brl(float(profile['renda_mensal']))}, patrimonio de "
                f"{format_brl(float(profile['patrimonio_total']))} e perfil {profile['perfil_investidor']}. "
                f"O objetivo principal e {profile['objetivo_principal'].lower()}."
            ),
            sources=["data/perfil_investidor.json"],
            evidence_label="Baseado em perfil do investidor",
            next_step="Posso usar esse perfil para recomendar produtos ou revisar metas.",
        )

    def _is_out_of_scope(self, normalized: str) -> bool:
        forbidden_topics = ["tempo", "futebol", "politica", "senha", "cliente x"]
        return any(topic in normalized for topic in forbidden_topics)
