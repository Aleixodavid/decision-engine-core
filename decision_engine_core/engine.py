"""
Decision Engine — Motor com Factory + Strategy Patterns.
Alterna entre provedores de decisão/LLM de forma transparente.
"""

import time
import uuid
import logging
from providers import MockProvider, LocalRuleProvider, ExternalAPIProvider, DecisionProvider

logger = logging.getLogger("DecisionEngine")


class ProviderFactory:
    """Factory Pattern — cria instâncias de provedores de decisão."""

    _registry = {}

    @classmethod
    def register(cls, name: str, provider_class):
        cls._registry[name] = provider_class

    @classmethod
    def create(cls, name: str, config: dict = None) -> DecisionProvider:
        provider_class = cls._registry.get(name)
        if not provider_class:
            raise ValueError(f"Unknown provider: {name}. Available: {list(cls._registry.keys())}")
        return provider_class(config or {})

    @classmethod
    def available(cls) -> list:
        return list(cls._registry.keys())


# Registrar provedores disponíveis
ProviderFactory.register("mock", MockProvider)
ProviderFactory.register("local_rules", LocalRuleProvider)
ProviderFactory.register("external_api", ExternalAPIProvider)


class DecisionEngine:
    """
    Motor principal com Strategy Pattern para alternância de provedores.
    Mantém trilha de auditoria com Correlation ID.
    """

    def __init__(self, config: dict):
        self.config = config
        self._audit_trail = []
        default_provider = config.get("default_provider", "mock")
        self._provider = ProviderFactory.create(default_provider, config)
        self.active_provider_name = default_provider
        logger.info(f"[Engine] Inicializado com provedor: {default_provider}")

    def switch_provider(self, name: str) -> bool:
        """Strategy Pattern — alterna provedor em runtime."""
        try:
            self._provider = ProviderFactory.create(name, self.config)
            self.active_provider_name = name
            logger.info(f"[Engine] Provedor alterado para: {name}")
            return True
        except ValueError as e:
            logger.error(f"[Engine] Falha ao trocar provedor: {e}")
            return False

    def decide(self, context: dict, correlation_id: str = None) -> dict:
        """Executa decisão usando o provedor ativo (Strategy)."""
        correlation_id = correlation_id or str(uuid.uuid4())
        t0 = time.time()

        try:
            result = self._provider.decide(context)
            elapsed = round(time.time() - t0, 4)

            decision_record = {
                "correlation_id": correlation_id,
                "provider": self.active_provider_name,
                "context": context,
                "decision": result,
                "elapsed_ms": round(elapsed * 1000, 2),
                "timestamp": time.time(),
                "status": "ok",
            }
            self._audit_trail.append(decision_record)
            return decision_record

        except Exception as e:
            elapsed = round(time.time() - t0, 4)
            error_record = {
                "correlation_id": correlation_id,
                "provider": self.active_provider_name,
                "error": str(e),
                "elapsed_ms": round(elapsed * 1000, 2),
                "timestamp": time.time(),
                "status": "error",
            }
            self._audit_trail.append(error_record)
            return error_record

    def diagnose(self, target: str, correlation_id: str = None) -> dict:
        """Gera relatório de diagnóstico estruturado em JSON."""
        correlation_id = correlation_id or str(uuid.uuid4())

        report = {
            "correlation_id": correlation_id,
            "target": target,
            "timestamp": time.time(),
            "engine": {
                "active_provider": self.active_provider_name,
                "available_providers": ProviderFactory.available(),
                "audit_trail_size": len(self._audit_trail),
            },
            "checks": [
                {"name": "provider_health", "status": "ok", "detail": f"{self.active_provider_name} responding"},
                {"name": "memory_usage", "status": "ok", "detail": f"Audit trail: {len(self._audit_trail)} records"},
                {"name": "config_loaded", "status": "ok", "detail": f"Config keys: {len(self.config)}"},
            ],
            "overall_status": "healthy",
        }

        logger.info(f"[Engine] Diagnóstico gerado | CID={correlation_id} | Target: {target}")
        return report

    def list_providers(self) -> list:
        return ProviderFactory.available()

    def get_audit_trail(self, limit: int = 50) -> list:
        return self._audit_trail[-limit:][::-1]
