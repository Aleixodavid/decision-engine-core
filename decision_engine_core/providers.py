"""
Decision Providers — Implementações concretas do padrão Strategy.
Cada provedor implementa a interface DecisionProvider.
"""

import time
import random
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger("Providers")


class DecisionProvider(ABC):
    """Interface base para provedores de decisão (Strategy Pattern)."""

    @abstractmethod
    def decide(self, context: dict) -> dict:
        """Processa contexto e retorna decisão estruturada."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass


class MockProvider(DecisionProvider):
    """Provedor mock para testes e demonstração."""

    def __init__(self, config: dict = None):
        self.config = config or {}

    def get_name(self) -> str:
        return "mock"

    def decide(self, context: dict) -> dict:
        options = ["approve", "reject", "review", "escalate"]
        confidence = round(random.uniform(0.5, 1.0), 3)
        decision = random.choice(options)

        return {
            "provider": self.get_name(),
            "action": decision,
            "confidence": confidence,
            "reasoning": f"Mock decision based on random selection (confidence: {confidence})",
            "input_keys": list(context.keys()),
        }


class LocalRuleProvider(DecisionProvider):
    """Provedor baseado em regras locais determinísticas."""

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.rules = [
            {"condition": lambda ctx: ctx.get("risk_level", 0) > 80, "action": "reject", "reason": "High risk level"},
            {"condition": lambda ctx: ctx.get("amount", 0) > 10000, "action": "escalate", "reason": "Amount exceeds threshold"},
            {"condition": lambda ctx: ctx.get("category") == "premium", "action": "approve", "reason": "Premium category auto-approved"},
            {"condition": lambda ctx: ctx.get("score", 0) >= 70, "action": "approve", "reason": "Score above threshold"},
        ]

    def get_name(self) -> str:
        return "local_rules"

    def decide(self, context: dict) -> dict:
        matched_rules = []
        for rule in self.rules:
            try:
                if rule["condition"](context):
                    matched_rules.append({"action": rule["action"], "reason": rule["reason"]})
            except Exception:
                continue

        if matched_rules:
            primary = matched_rules[0]
            return {
                "provider": self.get_name(),
                "action": primary["action"],
                "confidence": 1.0,
                "reasoning": primary["reason"],
                "rules_matched": len(matched_rules),
                "all_matches": matched_rules,
            }

        return {
            "provider": self.get_name(),
            "action": "review",
            "confidence": 0.5,
            "reasoning": "No rules matched — flagged for manual review",
            "rules_matched": 0,
        }


class ExternalAPIProvider(DecisionProvider):
    """Provedor simulado de API externa (LLM/serviço remoto)."""

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.api_key = config.get("api_key", "TEST_TOKEN_API_KEY_001")
        self.endpoint = config.get("external_endpoint", "https://api.example.com/v1/decide")

    def get_name(self) -> str:
        return "external_api"

    def decide(self, context: dict) -> dict:
        """
        Simula chamada a API externa.
        Em produção, faria request HTTP real com self.api_key e self.endpoint.
        """
        # Simulação de latência de rede
        latency = round(random.uniform(0.05, 0.3), 3)
        time.sleep(latency)

        # Simular resposta de LLM/serviço externo
        actions = ["approve", "reject", "review"]
        weights = [0.6, 0.15, 0.25]
        action = random.choices(actions, weights=weights, k=1)[0]
        confidence = round(random.uniform(0.7, 0.99), 3)

        return {
            "provider": self.get_name(),
            "action": action,
            "confidence": confidence,
            "reasoning": f"External API decision (simulated, latency: {latency}s)",
            "simulated": True,
            "api_endpoint": self.endpoint,
            "latency_ms": round(latency * 1000, 1),
        }
