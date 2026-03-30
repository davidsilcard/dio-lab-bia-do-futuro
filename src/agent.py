from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from knowledge_base import KnowledgeBase, format_brl


SYSTEM_PROMPT = """\
Você é a BIA Futuro, uma assistente financeira consultiva e prudente.
Seu trabalho é orientar o cliente usando apenas os dados carregados localmente.

Regras:
1. Nunca invente valores, produtos, datas ou políticas que não estejam na base local.
2. Sempre explique de onde veio a resposta: perfil, transações, histórico ou catálogo de produtos.
3. Priorize segurança financeira, reserva de emergência e aderência ao perfil do investidor.
4. Se a pergunta estiver fora do escopo financeiro ou sem base de dados suficiente, diga isso claramente.
5. Não peça nem revele dados sensíveis. Não faça promessas de rentabilidade futura.
"""


@dataclass
class AgentResponse:
    answer: str
    sources: list[str]
    safe: bool = True


class FinanceAgent:
    def __init__(self, project_root: Path) -> None:
        self.knowledge = KnowledgeBase(project_root)

    def respond(self, user_message: str) -> AgentResponse:
        normalized = user_message.lower()

        if self._is_out_of_scope(normalized):
            return AgentResponse(
                answer=(
                    "Posso ajudar apenas com finanças pessoais deste cliente fictício. "
                    "Se quiser, posso analisar gastos, metas, reserva de emergência ou sugerir produtos compatíveis."
                ),
                sources=["Regras do agente"],
            )

        if "aliment" in normalized:
            return self._answer_category_spending("alimentacao", "alimentação")
        if "moradia" in normalized or "aluguel" in normalized:
            return self._answer_category_spending("moradia", "moradia")
        if "transporte" in normalized or "uber" in normalized or "combust" in normalized:
            return self._answer_category_spending("transporte", "transporte")
        if "saúde" in normalized or "saude" in normalized or "farm" in normalized or "academia" in normalized:
            return self._answer_category_spending("saude", "saúde")
        if "resumo" in normalized or "gastei no mês" in normalized or "gastei no mes" in normalized:
            return self._answer_monthly_summary()
        if "reserva" in normalized or "meta" in normalized:
            return self._answer_goal_progress()
        if "invest" in normalized or "produto" in normalized or "aplicar" in normalized or "recomenda" in normalized:
            return self._answer_recommendation()
        if "atendimento" in normalized or "histórico" in normalized or "historico" in normalized:
            return self._answer_service_history()
        if "perfil" in normalized:
            return self._answer_profile()

        return AgentResponse(
            answer=(
                "Não encontrei base suficiente para responder isso com segurança. "
                "Tente perguntar sobre gastos por categoria, resumo mensal, metas, perfil ou recomendações de produtos."
            ),
            sources=["Regras do agente"],
            safe=False,
        )

    def starter_questions(self) -> list[str]:
        return [
            "Quanto gastei com alimentação?",
            "Como está minha reserva de emergência?",
            "Qual produto combina com meu perfil?",
            "Me dê um resumo financeiro do mês.",
        ]

    def _answer_category_spending(self, category_key: str, category_label: str) -> AgentResponse:
        transactions = self.knowledge.list_transactions(category=category_key)
        total = self.knowledge.sum_transactions(category=category_key)

        if not transactions:
            return AgentResponse(
                answer=f"Não encontrei transações da categoria {category_label} na base atual.",
                sources=["data/transacoes.csv"],
            )

        details = "; ".join(
            f"{item['data']}: {item['descricao']} ({format_brl(float(item['valor']))})"
            for item in transactions
        )
        return AgentResponse(
            answer=(
                f"No período carregado, você gastou {format_brl(total)} com {category_label}. "
                f"Lançamentos considerados: {details}."
            ),
            sources=["data/transacoes.csv"],
        )

    def _answer_monthly_summary(self) -> AgentResponse:
        income = self.knowledge.sum_transactions(kind="entrada")
        expenses = self.knowledge.sum_transactions(kind="saida")
        balance = self.knowledge.monthly_balance()
        categories = self.knowledge.spending_by_category()
        top_category, top_value = next(iter(categories.items()))

        return AgentResponse(
            answer=(
                f"Seu resumo do período mostra receitas de {format_brl(income)}, despesas de {format_brl(expenses)} "
                f"e saldo estimado de {format_brl(balance)}. "
                f"A maior categoria de gasto foi {top_category}, com {format_brl(top_value)}. "
                f"Isso sugere espaço para revisar despesas variáveis antes de aumentar o risco dos investimentos."
            ),
            sources=["data/transacoes.csv", "data/perfil_investidor.json"],
        )

    def _answer_goal_progress(self) -> AgentResponse:
        gap = self.knowledge.emergency_fund_gap()
        current = float(self.knowledge.profile["reserva_emergencia_atual"])
        monthly_balance = self.knowledge.monthly_balance()

        if gap == 0:
            status = "Sua reserva de emergência já atingiu a meta definida na base."
        else:
            status = (
                f"Faltam {format_brl(gap)} para completar a meta da reserva de emergência. "
                f"O valor atual registrado é {format_brl(current)}."
            )

        suggestion = (
            f"Com o saldo mensal estimado de {format_brl(monthly_balance)}, "
            "priorizar aportes em liquidez diária é a estratégia mais prudente neste momento."
        )

        return AgentResponse(
            answer=f"{status} {suggestion}",
            sources=["data/perfil_investidor.json", "data/transacoes.csv"],
        )

    def _answer_recommendation(self) -> AgentResponse:
        profile = self.knowledge.profile
        recommendations = self.knowledge.recommend_products()
        lines = []

        for product in recommendations:
            lines.append(
                f"{product['nome']}: risco {product['risco']}, aporte mínimo de "
                f"{format_brl(float(product['aporte_minimo']))}, indicado para {product['indicado_para'].lower()}."
            )

        rationale = (
            f"Como o perfil é {profile['perfil_investidor']} e o objetivo principal é "
            f"'{profile['objetivo_principal']}', priorizei produtos de menor risco e boa liquidez."
        )

        return AgentResponse(
            answer=f"{rationale} Recomendações: {' '.join(lines)}",
            sources=["data/perfil_investidor.json", "data/produtos_financeiros.json"],
        )

    def _answer_service_history(self) -> AgentResponse:
        latest = self.knowledge.service_history[-3:]
        details = "; ".join(
            f"{item['data']} via {item['canal']}: {item['tema']}" for item in latest
        )
        return AgentResponse(
            answer=(
                "Os últimos atendimentos registrados mostram interesse recorrente em investimentos conservadores "
                f"e metas financeiras. Registros recentes: {details}."
            ),
            sources=["data/historico_atendimento.csv"],
        )

    def _answer_profile(self) -> AgentResponse:
        profile = self.knowledge.profile
        return AgentResponse(
            answer=(
                f"O cliente {profile['nome']} tem {profile['idade']} anos, renda mensal de "
                f"{format_brl(float(profile['renda_mensal']))}, patrimônio de "
                f"{format_brl(float(profile['patrimonio_total']))} e perfil {profile['perfil_investidor']}. "
                f"O objetivo principal é {profile['objetivo_principal'].lower()}."
            ),
            sources=["data/perfil_investidor.json"],
        )

    def _is_out_of_scope(self, normalized: str) -> bool:
        forbidden_topics = ["tempo", "futebol", "política", "politica", "senha", "cliente x"]
        return any(topic in normalized for topic in forbidden_topics)
