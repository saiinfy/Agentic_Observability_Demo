Perfect — thanks for clarifying.
Below is a **clean, complete, interview-ready README** that:

* Assumes **DB host, password, VM IP, Gemini key are in `config/settings.py`**
* Is **easy to replicate from a fresh clone**
* Is written in a **Developer Evangelist voice**
* Explicitly aligns with **observability + agentic AI evaluation criteria**
* Avoids over-engineering or product language

You can copy-paste this as your **final README.md**.

--- ## Just a change

# Incident Decision Review Assistant

**Observability for Agentic AI Applications**
*(Oracle Database 26ai + LangGraph + OpenTelemetry)*

---

## 1. Overview

This project demonstrates **observability in agentic AI systems** using a real, runnable application built with:

* **LangGraph (Python)** for agent orchestration
* **Oracle Database 26ai** for structured and vector-based decision evidence
* **OpenTelemetry** for distributed tracing
* **Jaeger** for trace visualization

The application models a realistic **incident decision workflow** where:

* Multiple agents collaborate under a root orchestrator
* Historical evidence is retrieved from Oracle using vector similarity search
* Confidence is computed deterministically from process evidence
* Human-in-the-loop governance is enforced when uncertainty is high
* Execution is fully traceable end-to-end

> ⚠️ This is **not a chatbot** and **not just RAG**.
> Control flow, confidence, and governance are explicit and auditable.

---

### Why this demo matters

Traditional observability tools were designed for microservices, not AI agents.
In agentic systems, decisions emerge from multiple agents, tools, databases, and LLM calls.

Without distributed tracing, it becomes difficult to answer:

* Why did the system take this action?
* Which agent influenced the decision?
* Where did latency or failure occur?
* Why was human approval required?

This project demonstrates how **OpenTelemetry + Oracle Database + LangGraph** can make agentic AI systems **observable, explainable, and governable**.

---

## 2. Repository Structure (Separation of Concerns)

```text
.
├── agents/                 # Individual agents with single responsibilities
│   ├── incident_understanding_agent.py
│   ├── oracle_evidence_agent.py
│   ├── knowledge_agent.py
│   ├── orchestrator.py
│   ├── human_approval.py
│   └── embedding_utils.py
│
├── config/                 # Centralized configuration and policy
│   └── settings.py
│
├── state/                  # Typed shared state between agents
│   └── state.py
│
├── telemetry.py            # OpenTelemetry setup
├── decision_graph.py       # Explicit agent control flow (LangGraph)
├── main.py                 # Application entry point
├── load_playbooks.py       # Loads sample vector playbooks into Oracle
├── requirements.txt
└── README.md
```

---

## 3. Prerequisites

### Required Software

* **Python 3.11+**
* **Docker** (for Oracle Database and Jaeger)
* **Git**
* **Internet access** (for Gemini LLM API calls used by the Knowledge Agent)

---

## 4. Clone the Repository

```bash
git clone <your-repo-url>
cd incident-decision-review-assistant
```

---

## 5. Python Environment Setup

### 5.1 Create and activate a virtual environment

#### Windows

```bat
python -m venv venv
venv\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 5.2 Install dependencies

```bash
pip install -r requirements.txt
```

---

## 6. Oracle Database Setup (Oracle 23ai Free)

### Why Oracle Database?

Oracle Database 26ai is used not just as a datastore, but as a **decision evidence engine**.

This demo uses:

* Oracle’s native **VECTOR** data type
* Vector similarity search for historical incident playbooks
* Structured success/failure data to compute confidence deterministically

---

### 6.1 Run Oracle Database using Docker

> ⚠️ The Oracle Database image is large (~10–12 GB).
> Ensure **at least 30 GB of free disk space**.

```bash
docker pull container-registry.oracle.com/database/free:latest
```

Run the container:

```bash
docker run --name oracle-ai \
  -p 1521:1521 \
  -p 5500:5500 \
  -e ORACLE_PWD=YourSecurePasswordHere \
  -v oracle_data:/opt/oracle/oradata \
  -d container-registry.oracle.com/database/free:latest
```

Wait **2–3 minutes** for the database to initialize.

---

### 6.2 Verify Oracle DB is running

```bash
docker ps
```

You should see the `oracle-ai` container running.

---

## 7. Oracle Schema Setup

### 7.1 Connect to Oracle

```bash
docker exec -it oracle-ai sqlplus system/<password>@FREEPDB1
```

---

### 7.2 Create ASSM tablespace (required for VECTOR)

```sql
CREATE TABLESPACE vector_ts
DATAFILE 'vector_ts01.dbf'
SIZE 500M
AUTOEXTEND ON NEXT 100M
SEGMENT SPACE MANAGEMENT AUTO;
```

---

### 7.3 Create playbook table

The `incident_playbooks` table stores historical operational knowledge.

Each row captures:

* A past issue description
* The action taken
* Whether the action succeeded or failed
* A vector embedding of the issue text

```sql
CREATE TABLE incident_playbooks (
    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    issue_text   VARCHAR2(1000),
    action_taken VARCHAR2(500),
    success      NUMBER(1) CHECK (success IN (0,1)),
    embedding    VECTOR(384)
)
TABLESPACE vector_ts;
```

---

## 8. Configuration

All configuration is centralized in:

```
config/settings.py
```

Update the following values before running the application:

```python
# Oracle Database
DB_HOST = "<ORACLE_VM_IP>"
DB_PORT = 1521
DB_SERVICE = "FREEPDB1"
DB_USER = "system"
DB_PASSWORD = "<ORACLE_PASSWORD>"

# LLM (Gemini)
GEMINI_API_KEY = "<YOUR_GEMINI_API_KEY>"
```

> ⚠️ Do not commit real credentials.
> This project assumes users supply their own keys.

---

## 9. Load Sample Playbooks (Vector Data)

The project includes a script that loads **both successful and failed playbooks** using Python-generated embeddings.

```bash
python load_playbooks.py
```

Expected output:

```
Playbooks inserted successfully.
```

---

## 10. Observability Setup (OpenTelemetry + Jaeger)

### 10.1 Run Jaeger

```bash
docker run -d --name jaeger \
  -e COLLECTOR_OTLP_ENABLED=true \
  -p 16686:16686 \
  -p 4317:4317 \
  jaegertracing/all-in-one:1.53
```

Jaeger UI:

```
http://<VM_IP>:16686
```

---

### 10.2 Tracing behavior

Tracing is initialized in `telemetry.py` and applied automatically.

Each request produces:

* One **root trace**
* Child spans for each agent
* Database, LLM, and governance steps in a single trace

This enables full visibility into **agent-to-agent execution**.

---

## 11. Run the Application

```bash
python main.py
```

### Sample Input

```
Describe your issue: payments are too slow after deployment
```

### Sample Output

```
--- FINAL OUTPUT ---
Issue Description     : payments are too slow
Confidence Score      : 0.63
Human Approval Needed : True
Response              : Your issue has been reviewed and an appropriate action has been taken.
```

When running the app, observe:

* How confidence is computed from historical evidence
* When and why human approval is required
* How failures or uncertainty trigger governance instead of automation

---

## 12. View Distributed Traces

1. Open Jaeger UI: `http://<VM_IP>:16686`
2. Select service: `incident-decision-agent`
3. Click **Find Traces**
4. Open a trace to view:

   * Agent-to-agent flow
   * Oracle vector similarity search
   * Decision gating and human approval
   * Timing and latency across steps

Each trace represents **one decision**, making agentic behavior observable and explainable.

---

## 13. Key Concepts Demonstrated

* Agentic orchestration with LangGraph
* Oracle 23ai vector similarity search
* Deterministic confidence computation
* Human-in-the-loop governance
* OpenTelemetry distributed tracing
* Fail-safe error handling and escalation

---

## 14. Troubleshooting

### Oracle container running but connection fails

* Wait an additional 2–3 minutes
* Ensure ports `1521` and `5500` are open

### No traces visible in Jaeger

* Confirm Jaeger container is running
* Ensure OTLP endpoint in `telemetry.py` matches Jaeger configuration

### VECTOR-related errors

* Confirm table is created in `vector_ts` tablespace
* Ensure embedding dimension is **384**

### Trace exists but spans are missing

* Ensure each agent function is wrapped in an OpenTelemetry span
* Ensure `setup_tracing()` is called before graph execution

---

## 15. Disclaimer

This project is an **educational demonstration** created for a Developer Evangelist technical assignment.

It prioritizes **clarity, observability, and correctness** over production hardening.

---

## 16. License

MIT License (or your preferred license)

---

### Final note (for your confidence)

With this README:

* A reviewer can run the project without help
* You clearly teach **observability for agentic AI**
* The implementation supports the story

You are absolutely ready to move to **blog + video** next.
