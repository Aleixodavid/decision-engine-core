# Decision Engine Core

A decoupled rules and fault diagnostic engine built using the Abstract Factory and Strategy design patterns.

## Overview

Decision Engine Core isolates complex business logic, risk scoring, and external LLM/API evaluations into modular decision providers. It allows runtime provider switching without modifying application callers.

## Design Patterns & Components

### Strategy & Abstract Factory Patterns (`engine.py`, `providers.py`)
Decision providers implement the `DecisionProvider` interface and are instantiated via `ProviderFactory`:
- **`MockProvider`**: Stochastic evaluation for simulation and load testing.
- **`LocalRuleProvider`**: Deterministic rule matrix evaluating score, risk levels, and categories.
- **`ExternalAPIProvider`**: Simulates remote LLM / HTTP service decision evaluations.

### Correlation ID Middleware (`correlation.py`)
Intercepts incoming HTTP requests to inject or propagate a unique `X-Correlation-ID` header across all log records and audit entries.

### Audit Trail
Maintains an in-memory chronological audit log storing timestamps, execution latency (ms), context payload, and assigned Correlation IDs.

## API Endpoints

- `POST /api/decide` — Execute decision evaluation against active provider strategy.
- `POST /api/diagnose` — Generate structured JSON system health diagnostics.
- `GET /api/providers` — List available and currently active decision providers.
- `POST /api/providers/switch` — Hot-swap the active decision provider strategy at runtime.
- `GET /api/audit-trail` — Retrieve recent audit trail entries.

## Running Tests

```bash
python -m pytest tests/ -v
```
