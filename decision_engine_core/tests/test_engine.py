"""Testes unitários do Decision Engine Core."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from engine import DecisionEngine, ProviderFactory
from providers import MockProvider, LocalRuleProvider, ExternalAPIProvider


class TestProviders:
    def test_mock_provider(self):
        p = MockProvider()
        res = p.decide({"test": 1})
        assert res["provider"] == "mock"
        assert "action" in res
        assert 0.0 <= res["confidence"] <= 1.0

    def test_local_rule_provider_high_risk(self):
        p = LocalRuleProvider()
        res = p.decide({"risk_level": 90})
        assert res["action"] == "reject"
        assert res["confidence"] == 1.0

    def test_local_rule_provider_premium(self):
        p = LocalRuleProvider()
        res = p.decide({"category": "premium"})
        assert res["action"] == "approve"

    def test_local_rule_provider_default(self):
        p = LocalRuleProvider()
        res = p.decide({})
        assert res["action"] == "review"

    def test_external_api_provider(self):
        p = ExternalAPIProvider({"api_key": "TEST_TOKEN_001"})
        res = p.decide({"prompt": "test"})
        assert res["provider"] == "external_api"
        assert res["simulated"] is True


class TestProviderFactory:
    def test_list_available(self):
        available = ProviderFactory.available()
        assert "mock" in available
        assert "local_rules" in available
        assert "external_api" in available

    def test_create_valid(self):
        p = ProviderFactory.create("mock")
        assert isinstance(p, MockProvider)

    def test_create_invalid_raises(self):
        with pytest.raises(ValueError):
            ProviderFactory.create("nonexistent")


class TestDecisionEngine:
    def test_engine_initialization(self):
        engine = DecisionEngine({"default_provider": "mock"})
        assert engine.active_provider_name == "mock"

    def test_engine_decide_and_audit(self):
        engine = DecisionEngine({"default_provider": "mock"})
        res = engine.decide({"key": "val"}, "cid-123")
        assert res["status"] == "ok"
        assert res["correlation_id"] == "cid-123"

        trail = engine.get_audit_trail()
        assert len(trail) == 1
        assert trail[0]["correlation_id"] == "cid-123"

    def test_switch_provider(self):
        engine = DecisionEngine({"default_provider": "mock"})
        assert engine.switch_provider("local_rules") is True
        assert engine.active_provider_name == "local_rules"

        res = engine.decide({"risk_level": 95})
        assert res["decision"]["action"] == "reject"

    def test_diagnose(self):
        engine = DecisionEngine({"default_provider": "mock"})
        report = engine.diagnose("test_target", "cid-diag")
        assert report["overall_status"] == "healthy"
        assert report["correlation_id"] == "cid-diag"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
