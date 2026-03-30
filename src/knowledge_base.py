from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path


def format_brl(value: float) -> str:
    formatted = f"{value:,.2f}"
    return f"R$ {formatted.replace(',', 'X').replace('.', ',').replace('X', '.')}"


@dataclass
class KnowledgeBase:
    base_path: Path

    def __post_init__(self) -> None:
        self.data_path = self.base_path / "data"
        self.profile = self._load_json("perfil_investidor.json")
        self.products = self._load_json("produtos_financeiros.json")
        self.transactions = self._load_csv("transacoes.csv")
        self.service_history = self._load_csv("historico_atendimento.csv")

    def _load_json(self, filename: str):
        with (self.data_path / filename).open(encoding="utf-8") as file:
            return json.load(file)

    def _load_csv(self, filename: str) -> list[dict[str, str]]:
        with (self.data_path / filename).open(encoding="utf-8") as file:
            return list(csv.DictReader(file))

    def sum_transactions(self, *, category: str | None = None, kind: str = "saida") -> float:
        total = 0.0
        for transaction in self.transactions:
            if transaction["tipo"] != kind:
                continue
            if category and transaction["categoria"] != category:
                continue
            total += float(transaction["valor"])
        return total

    def list_transactions(self, *, category: str | None = None, kind: str = "saida") -> list[dict[str, str]]:
        results: list[dict[str, str]] = []
        for transaction in self.transactions:
            if transaction["tipo"] != kind:
                continue
            if category and transaction["categoria"] != category:
                continue
            results.append(transaction)
        return results

    def monthly_balance(self) -> float:
        entradas = self.sum_transactions(kind="entrada")
        saidas = self.sum_transactions(kind="saida")
        return entradas - saidas

    def spending_by_category(self) -> dict[str, float]:
        summary: dict[str, float] = {}
        for transaction in self.transactions:
            if transaction["tipo"] != "saida":
                continue
            category = transaction["categoria"]
            summary[category] = summary.get(category, 0.0) + float(transaction["valor"])
        return dict(sorted(summary.items(), key=lambda item: item[1], reverse=True))

    def emergency_fund_gap(self) -> float:
        target = 0.0
        for goal in self.profile["metas"]:
            if goal["meta"].lower().startswith("completar reserva"):
                target = float(goal["valor_necessario"])
                break
        current = float(self.profile["reserva_emergencia_atual"])
        return max(target - current, 0.0)

    def recommend_products(self) -> list[dict]:
        accepted_risks = {"baixo"}
        if self.profile["perfil_investidor"] == "moderado" and self.profile["aceita_risco"]:
            accepted_risks.add("medio")

        goal_text = self.profile["objetivo_principal"].lower()
        recommendations: list[dict] = []

        for product in self.products:
            risk = product["risco"]
            indication = product["indicado_para"].lower()
            if risk not in accepted_risks:
                continue
            if "reserva" in goal_text and "reserva" not in indication and "seguran" not in indication:
                continue
            recommendations.append(product)

        if not recommendations:
            recommendations = [product for product in self.products if product["risco"] == "baixo"]

        return recommendations[:3]

    def context_snapshot(self) -> str:
        categories = self.spending_by_category()
        top_categories = ", ".join(
            f"{name}: {format_brl(total)}" for name, total in list(categories.items())[:3]
        )
        return (
            f"Cliente: {self.profile['nome']} | Perfil: {self.profile['perfil_investidor']} | "
            f"Objetivo: {self.profile['objetivo_principal']} | "
            f"Patrimônio: {format_brl(float(self.profile['patrimonio_total']))} | "
            f"Reserva atual: {format_brl(float(self.profile['reserva_emergencia_atual']))} | "
            f"Saldo mensal estimado: {format_brl(self.monthly_balance())} | "
            f"Principais gastos: {top_categories}"
        )
