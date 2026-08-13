# Security & Defense-in-Depth: Inventory SQL AI Assistant

## Security Philosophy
In AI-driven database systems, prompt instructions alone are **never** considered a security boundary. The Inventory SQL Assistant implements programmatic, defense-in-depth controls across every layer of the stack.

## Threat Model & Mitigations

| Threat Vector | Mitigation Strategy | Component |
| :--- | :--- | :--- |
| **SQL Injection (Adversarial Prompts)** | Strict AST parsing with `sqlglot` blocking stacked queries, multiple statements, and non-SELECT expressions. | `app/agents/validator.py` |
| **Data Destruction (`DROP`, `DELETE`, `TRUNCATE`)** | Programmatic blocklist of all DDL and DML statements. Analytical execution operates read-only. | `app/agents/validator.py` / `executor.py` |
| **Privilege Escalation** | 3-tier Role-Based Access Control (`viewer`, `manager`, `admin`) enforced via cryptographic JWT verification on every route. | `app/security/rbac.py` |
| **Unauthorized Mutations** | LLM cannot emit raw mutation SQL. Changes must go through parameterized ORM routines with 2-step confirmation. | `app/services/mutation_service.py` |
| **Denial of Service (OOM from Large Queries)** | Hard row limits (`MAX_QUERY_ROWS=100`) and query execution timeouts. | `app/agents/executor.py` |
| **System Database Attachment** | Blacklisting of `ATTACH`, `DETACH`, and SQLite `PRAGMA` commands. | `app/agents/validator.py` |
| **Credential Leakage** | Sanitized logging: passwords and JWT secrets are excluded from logs and error payloads. | `app/main.py` |

## RBAC Permissions Matrix

| Capability | Viewer | Manager | Admin |
| :--- | :---: | :---: | :---: |
| Natural Language Analytics (Chat) | ✅ | ✅ | ✅ |
| View Chat History & Sessions | ✅ (Own) | ✅ (Own) | ✅ (All) |
| CSV Data Ingestion & Preview | ❌ | ✅ | ✅ |
| Safe Record Creation & Updates | ❌ | ✅ | ✅ |
| Safe Record Deletions | ❌ | ❌ | ✅ |
