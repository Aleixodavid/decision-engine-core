# 🧠 Decision Engine Core

> **Motor Desacoplado de Regras de Negócio, Decisão & Diagnósticos**  
> Microsserviço extensível baseado em padrões comportamentais e criacionais para alternância de provedores em tempo de execução e auditoria com rastreabilidade ponta a ponta.

---

## 🎯 Objetivo do Subprograma

O **Decision Engine Core** é um motor central de decisão projetado para isolar regras de negócio complexas, modelos heurísticos e integrações com motores de Inteligência Artificial / LLMs externos. Ele permite alternar estratégias de avaliação sem necessidade de refatorar a aplicação principal.

---

## 🏛️ Arquitetura & Padrões de Projeto (*Design Patterns*)

### 1. **Factory Pattern (ProviderFactory)**
- **Arquivo:** `engine.py` / `providers.py`
- **Funcionamento:** Encapsula a criação de instâncias de provedores de decisão (`mock`, `local_rules`, `external_api`), garantindo que novas estratégias possam ser registradas sem alterar o código consumidor.

### 2. **Strategy Pattern (DecisionProvider)**
- **Arquivo:** `providers.py`
- **Estratégias Implementadas:**
  - `MockProvider`: Decisões estocásticas para testes de carga e simulações rápidas.
  - `LocalRuleProvider`: Matriz determinística de regras de negócio locais (score, limites financeiros, nível de risco).
  - `ExternalAPIProvider`: Integração simulada com modelos remotos / LLMs via requisições HTTP seguras.

### 3. **Correlation ID Middleware (Rastreabilidade Ponta a Ponta)**
- **Arquivo:** `correlation.py`
- **Funcionamento:** Intercepta todas as requisições HTTP e garante a presença do header `X-Correlation-ID`. Caso não seja fornecido pelo cliente, um UUID v4 único é gerado e propagado por toda a cadeia de execução.

### 4. **Trilha de Auditoria (Audit Trail)**
- Cada decisão tomada gera um registro imutável com timestamp, latência em milissegundos, contexto de entrada e identificador de correlação.

---

## 🔒 Sanitização & Segurança

- **Chaves de API Remotas:** Utilizam tokens formatados sob o padrão sanitizado `TEST_TOKEN_API_KEY_001`.
- **Identificadores Corporativos:** Referenciados como `CUST_TEST_1000` e `ACT_TEST_9999`.
- **Credenciais de Autenticação:** `admin` / `admin`.

---

## 📡 Endpoints da API (Porta `5003`)

### `POST /api/decide`
Executa o processamento de decisão para um determinado contexto de dados.
- **Body Exemplo:**
  ```json
  {
    "context": {
      "amount": 15000,
      "risk_level": 45,
      "category": "premium"
    }
  }
  ```
- **Resposta Exemplo:**
  ```json
  {
    "correlation_id": "8f3b2a1c-90de-4f5a-b67c-123456789abc",
    "decision": {
      "action": "escalate",
      "confidence": 1.0,
      "provider": "local_rules",
      "reasoning": "Amount exceeds threshold"
    },
    "elapsed_ms": 1.25,
    "status": "ok"
  }
  ```

### `POST /api/diagnose`
Gera um diagnóstico estruturado em JSON avaliando a saúde operacional do motor e de seus componentes.

### `GET /api/providers`
Lista os provedores disponíveis e indica qual está atualmente ativo.

### `POST /api/providers/switch`
Alterna em tempo real (*hot-swap*) o provedor de decisão ativo.
- **Body Exemplo:** `{"provider": "local_rules"}`

### `GET /api/audit-trail`
Consulta o histórico recente de decisões registradas na trilha de auditoria.

---

## 🧪 Testes Unitários

Para executar os testes do Motor de Decisão:

```bash
cd D:\Pessoal\portifolio\decision_engine_core
python -m pytest tests/ -v
```
