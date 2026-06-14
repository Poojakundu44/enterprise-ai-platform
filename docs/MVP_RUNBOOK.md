# MVP Vertical Slice — Runbook

End-to-end path: **login → upload document → RAG chat**.  
Architecture overview: [`ARCHITECTURE.md`](ARCHITECTURE.md).

## Prerequisites

- Java 17, Maven 3.9+
- Docker (for Postgres)

## 1. Start Postgres

```bash
cd infra
docker compose up -d
```

Creates databases:

- `enterprise_ai_auth`
- `enterprise_ai_audit`
- `enterprise_ai_ingestion`
- `enterprise_ai_embedding`

## 2. Start services (separate terminals)

Start in this order so ingestion can reach embedding:

```bash
mvn -pl auth-service spring-boot:run
mvn -pl embedding-service spring-boot:run
mvn -pl ingestion-service spring-boot:run
mvn -pl search-service spring-boot:run
mvn -pl connector-service spring-boot:run
mvn -pl rag-service spring-boot:run
mvn -pl gateway-service spring-boot:run
```

Optional: set `OPENAI_API_KEY` when starting `rag-service` for live LLM answers (otherwise stub mode uses retrieved chunks).

## 3. Register or login (via gateway)

**Login (dev admin):**

```bash
curl -s http://localhost:8080/api/v1/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"admin@enterprise.local\",\"password\":\"Enterprise123!\"}"
```

**Register (new user):**

```bash
curl -s http://localhost:8080/api/v1/auth/register ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"you@company.com\",\"password\":\"YourPass123!\",\"displayName\":\"Your Name\"}"
```

Copy `data.accessToken` from the response.

PowerShell example for token variable:

```powershell
$resp = curl -s http://localhost:8080/api/v1/auth/login -H "Content-Type: application/json" -d '{\"email\":\"admin@enterprise.local\",\"password\":\"Enterprise123!\"}' | ConvertFrom-Json
$TOKEN = $resp.data.accessToken
```

## 4. Upload a document

```bash
curl -s http://localhost:8080/api/v1/connectors/documents ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"title\":\"Onboarding Guide\",\"content\":\"Our PTO policy allows 20 days per year. Remote work is permitted twice per week.\",\"sourceType\":\"manual\"}"
```

Expected: `data.documentId`, `data.chunkCount`, `data.status` = `INDEXED`.

## 5. Semantic search (optional)

```bash
curl -s http://localhost:8080/api/v1/search/query ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"query\":\"remote work policy\",\"topK\":3}"
```

## 6. RAG chat

```bash
curl -s http://localhost:8080/api/v1/rag/chat ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"message\":\"What is the remote work policy?\",\"topK\":3}"
```

Expected: `data.answer`, `data.citations[]`, `data.model` (`stub` or OpenAI model name).

## Troubleshooting

| Issue | Check |
|-------|--------|
| `401` on gateway | Token expired (default 1h); login again |
| Ingestion fails connecting to embedding | Start `embedding-service` before `ingestion-service` |
| Auth service won't start | Postgres up; DB `enterprise_ai_auth` exists; Flyway applied |
| Empty RAG answer | Upload a document first; verify `chunkCount` > 0 |
| Build fails `illegal character \ufeff` | Re-save Java files as UTF-8 without BOM |

## Environment variables

| Variable | Used by | Default |
|----------|---------|---------|
| `JWT_SECRET` | gateway, auth | dev secret in `application.yml` |
| `DB_HOST`, `DB_PORT`, `DB_USERNAME`, `DB_PASSWORD` | auth, ingestion, embedding | localhost / postgres |
| `OPENAI_API_KEY` | rag-service | _(empty = stub LLM)_ |
| `OPENAI_MODEL` | rag-service | `gpt-4o-mini` |
