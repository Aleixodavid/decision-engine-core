"""
Decision Engine Core — Motor Desacoplado de Regras e Diagnósticos
Arquitetura: Factory + Strategy patterns para alternância de provedores,
diagnósticos estruturados em JSON e rastreabilidade com Correlation ID.

Credenciais de demonstração: admin / admin
"""

import os
import json
import uuid
import logging
from flask import Flask, request, jsonify, g

from engine import DecisionEngine
from providers import MockProvider, LocalRuleProvider, ExternalAPIProvider
from correlation import CorrelationMiddleware

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

config = load_config()

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(name)s — %(levelname)s — %(message)s")
logger = logging.getLogger("DecisionEngine")

app = Flask(__name__)
app.secret_key = config.get("secret_key", "decision_demo_secret")

# Registrar middleware de Correlation ID
correlation = CorrelationMiddleware(app)

# Inicializar engine com provedores disponíveis
engine = DecisionEngine(config)


def require_auth(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == "admin" and auth.password == "admin":
            return f(*args, **kwargs)
        data = request.get_json(silent=True) or {}
        if data.get("username") == "admin" and data.get("password") == "admin":
            return f(*args, **kwargs)
        return jsonify({"error": "Unauthorized"}), 401
    return decorated


@app.route("/api/health")
def health():
    return jsonify({
        "status": "online",
        "service": "Decision Engine Core",
        "version": "1.0.0",
        "providers": engine.list_providers(),
        "active_provider": engine.active_provider_name,
    })


@app.route("/api/decide", methods=["POST"])
@require_auth
def decide():
    """Executa decisão usando o provedor ativo."""
    data = request.get_json(silent=True) or {}
    context = data.get("context", {})
    correlation_id = g.get("correlation_id", str(uuid.uuid4()))

    result = engine.decide(context, correlation_id)
    return jsonify(result)


@app.route("/api/diagnose", methods=["POST"])
@require_auth
def diagnose():
    """Gera relatório de diagnóstico operacional."""
    data = request.get_json(silent=True) or {}
    target = data.get("target", "system")
    correlation_id = g.get("correlation_id", str(uuid.uuid4()))

    report = engine.diagnose(target, correlation_id)
    return jsonify(report)


@app.route("/api/providers")
@require_auth
def list_providers():
    """Lista todos os provedores de decisão disponíveis."""
    return jsonify({"providers": engine.list_providers(), "active": engine.active_provider_name})


@app.route("/api/providers/switch", methods=["POST"])
@require_auth
def switch_provider():
    """Alterna o provedor de decisão ativo."""
    data = request.get_json(silent=True) or {}
    provider_name = data.get("provider", "")
    success = engine.switch_provider(provider_name)
    if success:
        return jsonify({"status": "ok", "active_provider": engine.active_provider_name})
    return jsonify({"error": f"Unknown provider: {provider_name}"}), 400


@app.route("/api/audit-trail")
@require_auth
def audit_trail():
    """Retorna trilha de auditoria com Correlation IDs."""
    limit = min(int(request.args.get("limit", 50)), 200)
    return jsonify({"trail": engine.get_audit_trail(limit)})


if __name__ == "__main__":
    print("=" * 60)
    print("  Decision Engine Core — Motor de Regras")
    print("  Credenciais: admin / admin")
    print("  Endpoint: http://127.0.0.1:5003")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5003, debug=False)
