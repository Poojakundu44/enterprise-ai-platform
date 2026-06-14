#!/usr/bin/env python3
"""
Build ARCHITECT_REASONING_AND_INTERVIEW_GUIDE.md and .docx
Principal Engineer training manual — WHY, theory, trade-offs, interview defense.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MD_OUT = ROOT / "ARCHITECT_REASONING_AND_INTERVIEW_GUIDE.md"
DOCX_OUT = ROOT / "ARCHITECT_REASONING_AND_INTERVIEW_GUIDE.docx"

SECTIONS = [
    "1. What Problem Does This Solve?",
    "2. Theoretical Foundations",
    "3. Architect's Thought Process",
    "4. Alternative Designs Considered",
    "5. Trade-Off Analysis",
    "6. Failure Theory",
    "7. Scalability Theory",
    "8. Interview Defense",
    "9. Principal Engineer Challenge Questions",
    "10. Real Production Lessons",
    "11. Evolution Roadmap",
    "12. CTO Review",
]


def comp(title, parts):
    """parts: dict with keys s1..s12"""
    lines = [f"\n## {title}\n"]
    for i, heading in enumerate(SECTIONS, 1):
        key = f"s{i}"
        lines.append(f"\n### {heading}\n\n")
        lines.append(parts.get(key, "_Pending._") + "\n")
    return "".join(lines)


def cs_block(srp="", dist="", db="", sec=""):
    out = []
    if srp:
        out.append(f"**Computer Science Theory:** {srp}")
    if dist:
        out.append(f"**Distributed Systems Theory:** {dist}")
    if db:
        out.append(f"**Database Theory:** {db}")
    if sec:
        out.append(f"**Security Theory:** {sec}")
    return "\n\n".join(out)


def alts_block(options, chosen, why):
    lines = []
    for label, pros, cons in options:
        lines.append(f"**{label}**\n- Pros: {pros}\n- Cons: {cons}\n")
    lines.append(f"**Chosen Design:** {chosen}\n\n**Why it won:** {why}")
    return "\n".join(lines)


def trade_block(benefits, costs, ops, scale, sec, maint, flex):
    return (
        f"**Benefits gained:** {benefits}\n\n"
        f"**Costs introduced:** {costs}\n\n"
        f"**Operational burden:** {ops}\n\n"
        f"**Scalability impact:** {scale}\n\n"
        f"**Security impact:** {sec}\n\n"
        f"**Maintenance impact:** {maint}\n\n"
        f"**Future flexibility impact:** {flex}"
    )


def fail_block(modes):
    return modes


def scale_block(cur, x10, x100, x1000, b1, b2, changes, limits):
    return (
        f"**Current capacity:** {cur}\n\n"
        f"**10x growth:** {x10}\n\n"
        f"**100x growth:** {x100}\n\n"
        f"**1000x growth:** {x1000}\n\n"
        f"**First bottleneck:** {b1}\n\n"
        f"**Second bottleneck:** {b2}\n\n"
        f"**Required architectural changes:** {changes}\n\n"
        f"**Theoretical limitations:** {limits}"
    )


def interview_block(q, weak, senior, staff, principal, followups):
    return (
        f"**Question:** {q}\n\n"
        f"**Weak answer:** {weak}\n\n"
        f"**Strong Senior answer:** {senior}\n\n"
        f"**Strong Staff answer:** {staff}\n\n"
        f"**Strong Principal answer:** {principal}\n\n"
        f"**Likely follow-ups:** {followups}"
    )


def challenge_block(q, defense):
    return f"**Strongest challenge:** {q}\n\n**Strongest defense:** {defense}"


# ---------------------------------------------------------------------------
# COMPONENT DEFINITIONS
# ---------------------------------------------------------------------------

COMPONENTS = []

def add(title, **kwargs):
    COMPONENTS.append((title, kwargs))


# --- PLATFORM DECISIONS ---

add("Platform Decision: Domain Microservices in a Maven Monorepo",
    s1="""**Business:** Centralize governed AI over fragmented enterprise knowledge without unsafe shadow IT LLM usage.
**Technical:** Isolate identity, connectors, ingestion, vectors, retrieval, and generation so each can evolve and scale independently.
**Scalability:** Ingestion bursts must not force scaling RAG pods; search QPS must not load PDF parsers.
**Reliability:** Parser or embedder failure must not deny login.
**If removed:** One team ships a tangled monolith; blast radius spans auth + chat; you cannot optimize cost per workload.""",
    s2=cs_block(
        srp="Each deployable owns one bounded context (auth, connect, ingest, embed, search, rag, govern). High cohesion inside; loose coupling via HTTP + DTOs only (Information Hiding).",
        dist="Blast-radius isolation; independent failure domains; prepares Temporal Decoupling via future Kafka (not yet). PACELC: ingestion favors Availability + eventual consistency with embed index; auth favors Consistency for credentials.",
        db="Database-per-service for auth, ingestion, embedding — avoids shared-table coupling anti-pattern.",
        sec="Defense in Depth planned: edge JWT + future document ACL + audit; Least Privilege per service account (future).",
    ),
    s3="""We separated authentication because identity evolves on a different calendar than RAG prompts—SSO, OIDC, SCIM, and MFA land in auth without redeploying embedding math. Connectors were isolated because third-party APIs (Confluence rate limits, OAuth token rotation) are the noisiest dependency. Ingestion and embedding split because batch vectorization has different hardware and cost curves than millisecond retrieval. We kept a monorepo so shared contracts (`platform-common`) version atomically—avoiding the 'distributed monolith' of divergent DTOs across repos. Constraints: MVP team size, need demonstrable vertical slice in weeks, Java/Spring enterprise standard, local Postgres acceptable.""",
    s4=alts_block(
        ("Option A: Modular monolith", "Single deploy, transactional ingest+embed, easy debug", "Cannot scale embed workers; security change redeploys all"),
        ("Option B: Polyrepo microservices", "Team autonomy per repo", "DTO drift; painful cross-service refactors"),
        ("Option C: Monorepo microservices (chosen)", "Atomic contract changes + independent runtime scale", "10 JVMs in dev; needs K8s maturity"),
        "Monorepo microservices",
        "Balances organizational boundaries with contract stability; matches how mature platform teams run internal developer platforms.",
    ),
    s5=trade_block(
        "Clear ownership, independent scaling, interview-defensible enterprise reference architecture.",
        "Network latency, partial failures, no cross-service ACID, operational surface area.",
        "High until K8s + Helm + centralized logging exist.",
        "Positive at 100x+ when hot paths differ.",
        "Larger attack surface until mTLS and internal auth.",
        "More repos to patch but monorepo reduces version hell.",
        "Can insert Kafka, vector DB, OIDC without renaming services.",
    ),
    s6=fail_block("""**Service crash:** K8s restarts pod; gateway 503 for that route. **DB crash:** Per-service outage (auth blocks login; embed blocks search quality). **Queue (future):** backlog, connector backpressure. **Cache (future):** latency spike, not correctness if TTL bounded. **Region:** total outage without multi-region. **Partition:** split-brain risk on DB—use single writer primary; search may serve stale vectors (eventual consistency). **Detection:** health probes, RED metrics, synthetic login+chat canaries. **Recovery:** replay Kafka, re-embed from `document_chunks`. **Customer:** degraded answers or upload failures. **Consistency:** ingest committed + embed failed = orphaned chunks (known MVP gap)."""),
    s7=scale_block(
        "Single-machine dev; ~10-50 RPS gateway.",
        "Add gateway replicas; first pain in sync embed chain.",
        "O(N) vector scan breaks; LLM cost dominates RAG.",
        "Sharded vector index, async ingest, multi-region read replicas, model gateway.",
        "Embedding full-table scan (Amdahl: serial fraction of request).",
        "OpenAI rate limits and spend.",
        "Kafka, pgvector HNSW, Redis cache, strip internal trust.",
        "Little's Law: blocking WebClient increases queue depth; CAP prevents global strong consistency without cost.",
    ),
    s8=interview_block(
        "Why microservices instead of a monolith?",
        "Microservices are best practice.",
        "Different scale and failure profiles per domain.",
        "Plus monorepo for DTO safety; measure ops cost; plan merge if team<5 and low QPS.",
        "Explicit trade: reject cross-service ACID for evolution speed; use sagas/outbox for ingest→embed; define merge triggers on metrics not dogma.",
        "When would you merge? — No independent scale proof after 6 months. How do you avoid distributed monolith? — No shared DB tables, only DTOs.",
    ),
    s9=challenge_block(
        "You have 10 services and almost no traffic—this is resume-driven development.",
        "Scaffold services (agent, audit, notification) cost one health endpoint each and prove routing topology. MVP implements the revenue path: auth→upload→RAG. Empty services are placeholders in a strangler roadmap, not production load. We would delete scaffolds if executive mandate forced single-team monolith before PMF.",
    ),
    s10="""**Seen in production:** 'Distributed monolith' with shared database—avoided here for auth/ingest/embed. **Scaling:** synchronous chains under load—Uber/Netflix moved to async. **Security:** flat internal network trusted—Google BeyondCorp says never. **Ops mistake:** deploying all 10 without ownership—each service needs an on-call label. **Mature pattern:** Shopify modular monolith first, extract hot path when metrics justify.""",
    s11="""**Startup:** sync REST MVP, HS256, hash embeddings. **Growth:** Kafka, OIDC, pgvector, audit events. **Enterprise:** ACL, dedicated vector tier, SLOs, mTLS. **Global:** multi-region index, model gateway, tenant shards, data residency.""",
    s12="""**Cost:** 10 JVM footprints vs one—higher until scale. **Risk:** ops overwhelm small team. **Scalability:** strong boundaries. **Team:** enables squad per domain if headcount exists. **Ops burden:** high now. **Maintainability:** good if contracts tested; bad if scaffolds never staffed.""",
)

# Gateway
add("Service: gateway-service (Spring Cloud Gateway)",
    s1="""**Business:** Single governed front door for employees and future UI—no direct access to internal services.
**Technical:** Terminate north-south traffic, enforce authentication, route by domain path, propagate identity headers.
**Scalability:** Stateless edge scales horizontally behind load balancer.
**Reliability:** Isolate clients from backend topology changes (ports → K8s DNS).
**Without gateway:** Every service exposes auth, CORS, rate limits—policy drift and larger attack surface.""",
    s2=cs_block(
        srp="Edge does routing + security only—no business rules (Separation of Concerns).",
        dist="Reverse proxy pattern; API Gateway pattern (Fowler); reactive stack for future SSE streaming (backpressure-friendly Netty pipeline).",
        sec="Defense in Depth layer 1: JWT validation before any backend; fail closed on bad token.",
    ),
    s3="""We chose Spring Cloud Gateway over NGINX alone because JWT validation, custom filters (`UserEmailGatewayFilter`), and dynamic routes live naturally in the same ecosystem as Spring Boot services—reducing language split for a Java platform team. Reactive Netty anticipates streaming RAG responses. Constraints: local dev with localhost URIs; production will externalize routes to ConfigMap/service discovery.""",
    s4=alts_block(
        ("NGINX/Envoy only", "Maximum performance, industry standard data plane", "JWT logic in Lua/WASM or separate auth service hop"),
        ("Kong/AWS API Gateway", "Managed policies, plugins", "Vendor lock-in, cost at scale"),
        ("Spring Cloud Gateway (chosen)", "Unified stack, filter chain, OAuth2 resource server", "JVM memory per edge pod"),
        "Spring Cloud Gateway",
        "Team skill fit and filter extensibility outweighed raw NGINX efficiency at current scale.",
    ),
    s5=trade_block(
        "Central policy enforcement, single public URL, path-based ownership.",
        "SPoF without replicas; route table drift; reactive/servlet impedance if filters misused.",
        "Must keep route map in sync with deployments—CI contract tests.",
        "Excellent horizontal scale.",
        "Concentrates auth at edge—good if done right.",
        "Route YAML changes need review.",
        "Can add rate limit, WAF integration, mTLS to backends.",
    ),
    s6=fail_block("""**Crash:** LB routes to other replicas. **DB:** N/A. **Partition:** stale routes to dead backend—need health-checked upstream (Spring Cloud LoadBalancer + K8s endpoints). **Customer:** total API outage if all gateways down. **Recovery:** roll back deployment; HPA. **Consistency:** N/A (stateless)."""),
    s7=scale_block("Thousands RPS per pod with TLS termination.", "5-10 pods + HPA.", "Regional edge + WAF.", "Global anycast; separate chat streaming from REST.", "TLS handshake CPU.", "Connection counts to backends.", "HTTP/2 to upstream, circuit breakers.", "Central edge saturates without CDN for static assets."),
    s8=interview_block(
        "Why a gateway instead of clients calling services directly?",
        "Security.",
        "Hides internal topology; central JWT; future rate limits.",
        "Plus identity propagation (`X-User-Email`), observability injection, SSE termination.",
        "Edge is policy plane not business plane; backends stay internal in VPC; Zero Trust still requires service auth east-west.",
        "How handle WebSocket/SSE? — Gateway long timeouts + reactive chain.",
    ),
    s9=challenge_block(
        "NGINX is faster—why JVM gateway?",
        "At our RPS, JVM is sufficient; developer velocity and OAuth2 integration matter more. We can put CloudFront/NGINX in front later without removing Gateway for auth filters.",
    ),
    s10="""**Failures:** route typo → 404 storms; JWT clock skew → 401 spikes. **Scale:** under-provisioned gateway during launch. **Security:** permissive CORS added at gateway 'temporarily'. **Mature:** Envoy data plane + external authz (OPA) at Stripe scale.""",
    s11="""**Startup:** localhost routes. **Growth:** K8s DNS, Resilience4j. **Enterprise:** WAF, per-tenant rate limits. **Global:** geo-DNS, edge caching.""",
    s12="""Essential for enterprise narrative; moderate cost; low build risk; requires SRE ownership of route config.""",
)

# Auth service - condensed for script length; more components follow same pattern
add("Service: auth-service (Identity & JWT Issuance)",
    s1="""**Business:** Prove who the employee is before accessing knowledge upload or RAG.
**Technical:** Credential verification, user lifecycle storage, JWT minting.
**Scalability:** Login is write-light; token validation should move to edge JWKS cache.
**Reliability:** Auth outage blocks new sessions; existing JWTs work until expiry (stateless).
**Without auth-service:** No tenant-safe platform—everyone is anonymous or secrets embedded in clients.""",
    s2=cs_block(
        srp="Auth is sole owner of credentials and token format.",
        dist="Stateless sessions (JWT) — no server-side session store → partition tolerance for read path at gateway. CAP: CP for user registration (unique email).",
        db="ACID on `users` table; unique constraint on email.",
        sec="Authentication (something you know); future Federation (OIDC). Least privilege: auth DB has no document content.",
    ),
    s3="""Identity is a bounded context that must not absorb RAG logic. We anticipated Entra ID/Okta—keeping auth separate means swapping `AuthService` internals for OIDC without touching embedding code. BCrypt for MVP passwords; HS256 JWT for simplicity with shared secret to gateway—explicitly dev-grade. Flyway + `ddl-auto: validate` signals production intent. Dev seed user accelerates demos but must be disabled in prod profiles.""",
    s4=alts_block(
        ("Embed auth in gateway", "One less hop", "Gateway becomes god-object; OIDC ugly"),
        ("Dedicated auth-service (chosen)", "Clear boundary, SSO path", "Extra deployable"),
        ("Fully external IdP only, no auth-service", "Less code", "Still need user mapping, API tokens for connectors"),
        "Dedicated auth-service",
        "Enterprise buyers expect an identity plane; custom JWT is bridge to OIDC.",
    ),
    s5=trade_block(
        "Isolated security reviews, independent DB backup/rotation.",
        "HS256 shared secret coupling to gateway.",
        "Flyway migrations, secret rotation ceremonies.",
        "Read replicas later for profile lookups.",
        "Central secret—rotate or move RS256.",
        "Security patches isolated.",
        "OIDC plug-in without RAG redeploy.",
    ),
    s6=fail_block("""**Crash:** login/register fail; valid JWTs still work. **DB down:** startup fails (`validate`). **Customer:** cannot login. **Recovery:** failover replica. **Consistency:** registration is transactional."""),
    s7=scale_block("Hundreds logins/sec on small Postgres.", "Connection pool tuning.", "Read replicas; offload verify to JWKS.", "OIDC only; auth-service becomes token exchange.", "BCrypt CPU on register.", "DB connections.", "Cache JWKS; rate limit register.", "Password hashing is O(work factor)."),
    s8=interview_block(
        "Why separate auth DB?",
        "Security.",
        "Blast radius, retention policy, compliance scope differ from document content.",
        "Audit DB also separate—auth PII not mixed with query logs.",
        "Defense: stolen ingest DB does not yield password hashes.",
        "Why HS256 not RS256?",
    ),
    s9=challenge_block(
        "Why not let Okta handle everything day one?",
        "MVP must run locally without corporate IdP; JWT bridge is intentional strangler. Production path: OIDC at gateway, auth-service becomes resource server + user directory sync.",
    ),
    s10="""**Failures:** default Spring user with random password logged at startup. **Scale:** BCrypt on hot register endpoint abused. **Security:** JWT never expires configured wrong. **Mature:** Entra ID + refresh rotation + step-up MFA.""",
    s11="""**Startup:** local users + HS256. **Growth:** OIDC, RS256 JWKS. **Enterprise:** SCIM provisioning. **Global:** regional IdP federation.""",
    s12="""Non-negotiable service; moderate cost; high compliance value; must fix dev secrets before prod.""",
)

# Continue with more components - embedding, rag, kafka planned, etc.
add("Service: embedding-service (Vector Index & Similarity)",
    s1="""**Business:** Make ingested text retrievable by meaning for RAG grounding.
**Technical:** Persist vectors per chunk; answer similarity queries.
**Scalability:** Write path batch-heavy; read path must become sub-linear (not O(N) in MVP).
**Reliability:** Stale/missing embeddings → wrong or empty RAG answers.
**Without it:** search is keyword-only; enterprise acronyms and paraphrases fail.""",
    s2=cs_block(
        srp="Only service that knows vector representation and distance metrics.",
        dist="Eventual consistency with ingestion if async (future); read-your-writes not guaranteed across services in MVP sync chain.",
        db="Denormalized `chunk_embeddings` — trades normalization for retrieval speed (avoid join at query time).",
    ),
    s3="""We accepted hash-based deterministic vectors to ship MVP without OpenAI API dependency in CI. Storing JSON in Postgres defers pgvector ops complexity. Separating from search keeps open the option to move index to Pinecone/OpenSearch without changing search API contract. Architect knew O(N) scan is technical debt with clear remediation: HNSW index + approximate nearest neighbor theory.""",
    s4=alts_block(
        ("Vectors in ingestion DB", "One DB", "Couples parse pipeline to index schema"),
        ("Dedicated embedding-service (chosen)", "Model upgrades isolated", "Extra network hop"),
        ("Managed Pinecone only", "Fast ANN", "Data residency concerns in EU enterprise"),
        "Dedicated embedding-service",
        "Enterprise architects routinely separate embedding workers from retrieval API.",
    ),
    s5=trade_block(
        "Independent model rollout, GPU node pools possible.",
        "O(N) scan; duplicate chunk text stored.",
        "Re-embed jobs on model change.",
        "Becomes first bottleneck.",
        "Embeddings may leak semantic info—encrypt at rest.",
        "Model migration scripts.",
        "Swap math without changing ingestion tables.",
    ),
    s6=fail_block("""**Crash:** search returns errors. **DB:** index unavailable. **Customer:** RAG says no knowledge. **Recovery:** re-index from chunks. **Consistency:** partial index after failed batch."""),
    s7=scale_block("Thousands chunks OK.", "10k chunks slow.", "100k needs ANN index.", "Millions need sharded vector DB.", "Full table scan.", "Memory per query.", "pgvector IVFFlat/HNSW; partition by tenant.", "ANN is approximate—recall vs latency trade-off (VC dimension theory)."),
    s8=interview_block(
        "Why not pgvector from day one?",
        "MVP velocity; math interface stable; migration is column type + index not service split.",
        "Staff: contract freeze at POST /embeddings/search.",
        "Principal: measure recall@k before buying Pinecone.",
        "Follow-up: embedding model upgrade strategy?",
    ),
    s9=challenge_block(
        "Hash embeddings are fake—this is toy code.",
        "Explicitly labeled dev-only; architectural value is service boundary and API, not production quality vectors. Would block GA without real model + ANN.",
    ),
    s10="""**Production lesson:** teams ship O(N) cosine in Postgres and die at 50k chunks—always plan ANN. **Security:** embeddings invert partially on sensitive text—treat as confidential.""",
    s11="""**Startup:** hash vectors. **Growth:** OpenAI embeddings + pgvector. **Enterprise:** dedicated vector cluster. **Global:** regional indexes with async replication.""",
    s12="""Core IP path; must fund vector infra before marketing 'semantic search'.""",
)

add("Service: rag-service (RAG Orchestration)",
    s1="""**Business:** Employees ask questions in natural language and receive grounded answers with citations for trust and compliance.
**Technical:** Orchestrate retrieval → context assembly → LLM generation → citation packaging.
**Scalability:** Dominated by LLM latency and token cost, not JVM CPU.
**Reliability:** Must degrade gracefully (stub mode, search-only fallback).
**Without rag-service:** employees use raw ChatGPT—data leakage.""",
    s2=cs_block(
        srp="RAG orchestration only—no chunking or vector math.",
        dist="Saga across search + OpenAI; no distributed transaction—compensate with stub on failure.",
        sec="Prompt constrains model to context-only answers (mitigates some hallucination; not full prompt-injection defense).",
    ),
    s3="""RAG is the product surface. Isolating it isolates LLM spend accounting, prompt templates, and safety filters. `LlmAnswerService` switches on API key—supports demo without external dependency. Temperature 0.2 reduces creativity/hallucination. Citations built from search hits regardless of LLM success—audit trail foundation. We rejected fine-tuning as primary approach (see platform decision doc) because enterprise knowledge changes daily.""",
    s4=alts_block(
        ("RAG in search-service", "One hop", "Mixes retrieval SLO with generative SLO"),
        ("RAG in gateway", "Convenient", "Terrible separation; prompts in edge"),
        ("Dedicated rag-service (chosen)", "Clear cost and policy boundary", "Extra service"),
        "Dedicated rag-service",
        "Generation is optional capability on top of search; different failure and cost model.",
    ),
    s5=trade_block(
        "Prompt evolution without touching index.",
        "Blocking WebClient chain; LLM vendor lock-in.",
        "Monitor token spend.",
        "LLM rate limits first.",
        "Prompt injection surface.",
        "Prompt versioning needed.",
        "Add model gateway later.",
    ),
    s6=fail_block("""**Crash:** chat down. **OpenAI down:** stub answer with citations. **Customer:** no AI answers. **Consistency:** may answer from stale index."""),
    s7=scale_block("Concurrent chats limited by threads blocking on WebClient.", "Need async + SSE.", "Model gateway + cache.", "FAQ precomputation tier.", "LLM tokens.", "Thread pool.", "Streaming, queue long jobs.", "Context window limits (information theory)."),
    s8=interview_block(
        "Why RAG not fine-tuning?",
        "Fine-tuning is stale day one; RAG cites sources; ACL at retrieval time.",
        "Staff: cost and update frequency.",
        "Principal: regulated enterprises require provenance per sentence.",
        "Follow-up: hallucination controls?",
    ),
    s9=challenge_block(
        "Why call search service—embed retrieval in RAG?",
        "Preserves retrieval SLO and reuse by agents/APIs; search team owns ACL filtering future.",
    ),
    s10="""**Failures:** unbounded context prompts blow token budget. **Security:** prompt injection via uploaded docs. **Mature:** LlamaGuard, citation-required evals, human feedback loop.""",
    s11="""**Startup:** stub + optional OpenAI. **Growth:** streaming SSE, eval harness. **Enterprise:** private LLM, policy engine. **Global:** geo-routed model gateway.""",
    s12="""Highest business visibility; LLM opex must be modeled; strong differentiation if citations trustworthy.""",
)

add("Planned: Apache Kafka (Event Backbone — Not Yet in Repository)",
    s1="""**Business:** Ingest millions of documents without blocking upload HTTP response.
**Technical:** Decouple connector from ingestion from embedding via durable log.
**Scalability:** Load leveling (distributed systems theory) — smooth spikes.
**Reliability:** Retry without losing work; replay for re-embed on model upgrade.
**Without Kafka:** sync chain latency and failure coupling remain (current MVP).""",
    s2=cs_block(
        dist="Temporal decoupling; at-least-once delivery; idempotent consumers; backpressure via consumer lag; PACELC: EL—latency for ingestion path when partition unavailable.",
    ),
    s3="""Architect deferred Kafka until HTTP contracts for ingest and embed stabilized—classic strangler. Topics planned: `ingestion.document.received`, `ingestion.chunk.created`, `audit.event`. Partition key = document or source id for ordering. Outbox pattern from ingestion DB recommended before dual-write bugs.""",
    s4=alts_block(
        ("Keep REST sync", "Simple MVP", "Does not scale"),
        ("SQS", "Managed", "Ordering weaker; on-prem enterprises prefer Kafka"),
        ("Kafka (planned)", "Industry standard for log-based replay", "Ops complexity"),
        "Kafka (future)",
        "Replay and multiple consumers (audit, embed, notify) justify log-based bus.",
    ),
    s5=trade_block(
        "Burst absorption, replay, audit fan-out.",
        "Consumer lag ops, schema registry, exactly-once complexity.",
        "High—need Kafka SRE skills.",
        "Enables 100x ingest.",
        "ACL on topics.",
        "More moving parts.",
        "High.",
    ),
    s6=fail_block("""**Broker down:** producers block or buffer; ingest stalls. **Detection:** lag metrics. **Recovery:** consumer replay. **Consistency:** eventual between DB and index."""),
    s7=scale_block("N/A today.", "Single cluster.", "Multi-AZ cluster.", "Cluster per region + mirroring.", "Partition throughput.", "Consumer CPU.", "Increase partitions.", "Ordering vs parallelism trade-off."),
    s8=interview_block(
        "Why Kafka not REST?",
        "REST for request/response; Kafka for durable async with replay—different problems.",
        "Staff: outbox pattern, idempotent consumers.",
        "Principal: compare to Pulsar only if multi-tenancy geo requirements.",
        "Follow-up: exactly-once?",
    ),
    s9=challenge_block(
        "Kafka is overkill for your MVP.",
        "Correct—which is why it is not in the repo yet. Architecture pre-positions boundaries so Kafka slots in without splitting services again.",
    ),
    s10="""**Lessons:** consumers without idempotency duplicate chunks; no DLQ → poison pill blocks partition. **Mature:** Confluent Cloud, schema registry, ksqlDB for metrics.""",
    s11="""**Startup:** sync. **Growth:** Kafka. **Enterprise:** governed topics per tenant. **Global:** MirrorMaker 2.""",
    s12="""Defer CAPEX until ingest SLA proven; budget ops headcount with adoption.""",
)

add("Planned: Redis (Cache & Rate Limiting — Not Yet in Repository)",
    s1="""**Business:** Reduce latency and LLM cost for repeated questions; protect platform from abuse.
**Technical:** Distributed cache for search results and JWKS; token bucket rate limits at gateway.
**Scalability:** Sub-ms reads vs Postgres/vector round trips.
**Reliability:** Must degrade safely when unavailable.
**Without Redis:** higher latency and cost; still functional (MVP).""",
    s2=cs_block(
        dist="Cache-aside pattern; CAP: AP for cache—stale reads possible; load leveling for hot keys.",
        sec="Cache keys MUST include tenant id—prevent cross-tenant leakage.",
    ),
    s3="""Not implemented because MVP traffic does not justify another datastore. Architect reserved gateway filter slot for Redis rate limiter. TTL 1-5 min for search; longer for JWKS.""",
    s4=alts_block(
        ("Caffeine local cache", "Zero ops", "Not shared across gateway pods"),
        ("Redis (planned)", "Shared; rate limits", "Another failure point"),
        ("No cache", "Simplest", "Slow/expensive at scale"),
        "Redis when >500 RPS search or LLM cost pain",
        "Economic trigger not ideological.",
    ),
    s5=trade_block(
        "Latency and cost savings.",
        "Consistency complexity; cache stampede risk.",
        "Redis HA (sentinel/cluster).",
        "High for hot queries.",
        "Key design critical.",
        "Low.",
        "Medium.",
    ),
    s6=fail_block("""**Redis down:** miss storm; choose fail-open vs fail-closed for rate limit. **Customer:** slower answers, higher cost—not data loss."""),
    s7=scale_block("N/A.", "Single Redis.", "Cluster.", "Redis Enterprise multi-region.", "Hot keys.", "Memory.", "Client-side caching L1.", "Working set size."),
    s8=interview_block(
        "Why Redis not local cache?",
        "Gateway has N replicas—need shared rate limit counters.",
        "Staff: single-flight on cache miss.",
        "Principal: hot key sharding with hashtags.",
        "Follow-up: cache invalidation on re-index?",
    ),
    s9=challenge_block(
        "Redis adds state—why not CDN?",
        "Different layer—CDN for static assets; Redis for dynamic query results and rate limits.",
    ),
    s10="""**Failures:** caching PII without TTL; forgetting tenant in key. **Mature:** Elasticache with auto-failover.""",
    s11="""**Startup:** none. **Growth:** Redis. **Enterprise:** dedicated cluster per env. **Global:** regional replicas with invalidation bus.""",
    s12="""OpEx line item; enable when unit economics of LLM require it.""",
)

# APIs
add("API: POST /api/v1/auth/login",
    s1="""**Business:** Employee obtains bearer token for subsequent governed API calls.
**Technical:** Credential verification against `users` table.
**Without it:** no authenticated upload or RAG.""",
    s2=cs_block(sec="Authentication; fail closed with 401; same error for bad user vs bad password (information hiding against enumeration)."),
    s3="""Public at gateway by design—login must precede JWT. Returns opaque bearer, not session cookie, for SPA/mobile friendliness.""",
    s4=alts_block(
        ("Session cookies only", "CSRF protections familiar", "Harder for mobile/CLI"),
        ("JWT bearer (chosen)", "Stateless microservices", "Revocation harder—use short TTL"),
        "JWT bearer",
        "Matches gateway resource server.",
    ),
    s5=trade_block("Enables stateless scale.", "Token theft if XSS.", "Low.", "Login not hot path.", "Brute force risk—need rate limit.", "Low.", "OIDC swap later."),
    s6=fail_block("**Auth down:** 401/503. **Customer:** cannot work."),
    s7=scale_block("BCrypt bounded.", "Rate limit.", "OIDC offload.", "Federation.", "BCrypt.", "DB.", "Cache nothing sensitive.", "Work factor tuning."),
    s8=interview_block("Why public?", "Gateway permit list.", "Standard OAuth2 resource owner bridge for MVP.", "Move to OIDC redirect in enterprise.", "Principal: threat model for brute force.", "MFA?"),
    s9=challenge_block("Why not HttpOnly cookie?", "Bearer chosen for API-first; BFF can wrap later."),
    s10="""Credential stuffing—need CAPTCHA/rate limit.""",
    s11="""MVP password. Growth OIDC. Enterprise conditional access.""",
    s12="""Required; low marginal cost.""",
)

add("API: POST /api/v1/rag/chat",
    s1="""**Business:** Natural language Q&A over corporate knowledge with citations.
**Technical:** Orchestrates search + LLM.
**Without it:** platform is search-only—lower adoption.""",
    s2=cs_block(
        dist="Multi-step saga; no 2PC; fallback stub on LLM failure (graceful degradation).",
        sec="Authorization at gateway; future document ACL at search.",
    ),
    s3="""Core product endpoint. topK balances recall vs token cost. Citations mandatory in response shape for compliance narrative.""",
    s4=alts_block(
        ("GraphQL single endpoint", "Flexible", "Harder to govern at gateway"),
        ("REST POST chat (chosen)", "Simple curl demos", "Multiple round trips if not composed"),
        "REST composed internally",
        "MVP clarity.",
    ),
    s5=trade_block("High value.", "LLM cost per call.", "Monitor tokens.", "LLM limits first.", "Prompt injection.", "Prompt versions.", "Model routing."),
    s6=fail_block("**Search down:** empty citations. **OpenAI down:** stub. **Customer:** poor answers."),
    s7=scale_block("Few concurrent blocking threads.", "Async/SSE.", "Cache retrieval.", "Precomputed FAQs.", "LLM.", "Threads.", "Queue.", "Context limits."),
    s8=interview_block("Why sync not SSE?", "MVP; streaming is growth stage.", "Staff: backpressure on streams.", "Principal: timeout alignment gateway→rag→OpenAI.", "Eval metrics?"),
    s9=challenge_block("Why not client call OpenAI directly?", "Data leaves enterprise; no audit; no ACL on context."),
    s10="""Prompt injection via uploaded docs; token bombs in message field.""",
    s11="""Stub→OpenAI→private LLM→streaming.""",
    s12="""Revenue surface; model COGS critical.""",
)

# Database tables
add("Database Table: users (enterprise_ai_auth)",
    s1="""**Business:** Persistent identity for employees using the platform.
**Technical:** Source of truth for login validation and JWT claims.
**Without it:** only hardcoded dev user.""",
    s2=cs_block(
        db="ACID; 3NF (single entity); unique index on email for O(log n) lookup; rejects denormalized duplicate emails.",
        sec="password_hash only—never store plaintext (least storage of secret).",
    ),
    s3="""UUID PK for global uniqueness in future multi-region federation. Email case-insensitive application logic + unique index. Separate DB so backup/encryption policies differ from document content.""",
    s4=alts_block(
        ("Users in shared platform DB", "Joins easy", "Couples auth to ingest migrations"),
        ("Dedicated auth DB (chosen)", "Isolation", "More connections"),
        "Dedicated auth DB",
        "Compliance and blast radius.",
    ),
    s5=trade_block("Clean security boundary.", "Another DB to manage.", "Medium.", "Fine to  millions users.", "PII concentration.", "Flyway.", "Federation later."),
    s6=fail_block("**DB down:** no login. **Recovery:** restore backup."),
    s7=scale_block("Small.", "Read replica.", "Shard rarely needed.", "Federated identity reduces local rows.", "Index on email.", "Connections.", "PgBouncer.", "Write skew N/A."),
    s8=interview_block("Why UUID?", "Distributed ID generation without coordinator.", "Staff: vs bigint—trade storage for merge safety.", "Principal: ULID if time-sortable needed.", "GDPR delete?"),
    s9=challenge_block("Why not external IdP only?", "Still need local user row for connector ownership mapping until full SCIM."),
    s10="""Leaked DB exposes hashes—need strong BCrypt work factor.""",
    s11="""Local users→hybrid→IdP-primary.""",
    s12="""Small cost; high risk if breached.""",
)

add("Database Table: chunk_embeddings (enterprise_ai_embedding)",
    s1="""**Business:** Enable semantic retrieval for RAG.
**Technical:** Stores vector + denormalized text for hit display.
**Without it:** search returns nothing.""",
    s2=cs_block(
        db="Denormalization: duplicates title/content from ingestion to avoid cross-DB join at query time (CQRS read model style).",
        dist="Eventually consistent with `document_chunks` if embed fails.",
    ),
    s3="""`chunk_id` PK aligns with ingestion chunk UUID—idempotent upserts possible. JSON vector column is migration path to pgvector `vector(1536)`.""",
    s4=alts_block(
        ("Normalize: store only vector", "Less storage", "Join latency across services"),
        ("Denormalized (chosen)", "Fast hits", "Stale title if doc renamed"),
        "Denormalized read model",
        "Query latency dominates enterprise SLAs.",
    ),
    s5=trade_block("Fast retrieval.", "Storage duplication.", "Re-embed on change.", "Needs ANN index.", "Content sensitivity.", "Model migrations.", "Move to vector DB."),
    s6=fail_block("**Loss:** rebuild from chunks. **Partial:** wrong answers."),
    s7=scale_block("N small.", "ANN required.", "Shard by tenant.", "Dedicated vector store.", "Memory.", "Disk IO.", "HNSW.", "ANN recall < 1."),
    s8=interview_block("Why JSON not pgvector yet?", "MVP portability; migration planned.", "Staff: recall@k testing.", "Principal: data residency for vectors in EU.", "Re-embed strategy?"),
    s9=challenge_block("Denormalization violates purity.", "Read model pattern—ingestion is write model; intentional CQRS lite."),
    s10="""Teams forget re-embed on model change—stale semantics.""",
    s11="""Postgres JSON→pgvector→managed ANN.""",
    s12="""Storage cost grows with corpus; budget it.""",
)

# Class-level: UserEmailGatewayFilter
add("Class: UserEmailGatewayFilter (Gateway Global Filter)",
    s1="""**Business:** Downstream services need stable employee identity for ownership on uploaded documents without re-parsing JWT.
**Technical:** Extract `email` claim post-authentication; inject `X-User-Email` header.
**Without it:** ingestion cannot set `owner_email` from gateway path.""",
    s2=cs_block(
        srp="Single responsibility: identity propagation only.",
        dist="Trusted header pattern—relies on network policy (mTLS future); not a security boundary alone.",
        sec="Defense in depth layer 2—must strip/spoof-proof internal network.",
    ),
    s3="""Reactive filter order `LOWEST_PRECEDENCE - 10` runs after JWT authentication. Chose header over re-encoding JWT to backends to keep internal services simple in MVP—explicit debt: internal services must not be exposed publicly.""",
    s4=alts_block(
        ("Pass full JWT internal", "Backends can validate", "Every service needs OAuth2"),
        ("X-User-Email header (chosen)", "Simple", "Spoofing if network breached"),
        ("Service mesh JWT", "Strong", "Heavier ops"),
        "Header for MVP, mesh later",
        "Progressive hardening.",
    ),
    s5=trade_block("Simple ingest ownership.", "Spoof risk.", "Low.", "N/A.", "Needs mTLS.", "Low.", "Swap to signed internal token."),
    s6=fail_block("**Missing claim:** no header; owner null. **Spoof:** wrong attribution if network open."),
    s7=scale_block("O(1) per request.", "Fine.", "Fine.", "Fine.", "None.", "None.", "Signed headers.", "None."),
    s8=interview_block("Is X-User-Email secure?", "No alone—network trust; production mTLS + service JWT.", "Staff: gateway strips inbound spoof.", "Principal: Zero Trust east-west.", "Spoofing test?"),
    s9=challenge_block("Why not OAuth2 token relay?", "MVP speed; roadmap item."),
    s10="""Classic mistake: expose ingestion port publicly—header forge.""",
    s11="""Header→signed service account→SPIFFE.""",
    s12="""Acceptable MVP; block prod without network policies.""",
)

# Scaffold services template
for name, port, future in [
    ("agent-service", "8087", "multi-step tool-using workflows with human-in-the-loop"),
    ("audit-service", "8088", "append-only compliance log of queries and retrievals"),
    ("notification-service", "8089", "async email/Slack for agent completion and failures"),
]:
    add(f"Service: {name} (Scaffold :{port})",
        s1=f"""**Business (planned):** {future}.
**Current:** health check only proves deploy slot and gateway route.
**Without scaffold:** gateway routes 404; harder to add service later without routing churn.""",
        s2=cs_block(srp="Placeholder bounded context reserved.", dist="Strangler fig—empty implementation until feature prioritized."),
        s3=f"""Architect included {name} in topology early so teams do not debate service existence later—cost is one JVM in dev, zero production traffic. Gateway route already maps `/api/v1/{name.split('-')[0]}s/**` pattern.""",
        s4=alts_block(
            ("No scaffold", "Less noise", "Route addition later"),
            ("Scaffold now (chosen)", "Topology complete", "Looks like over-engineering"),
            "Scaffold",
            "Enterprise architecture diagrams match repo.",
        ),
        s5=trade_block("Future speed.", "Confusion in interviews if unexplained.", "Low until enabled.", "N/A.", "N/A.", "Delete if never used.", "High when needed."),
        s6=fail_block("**Crash:** no user impact today."),
        s7=scale_block("N/A.", "Design when built.", "Queue workers.", "Partitioned audit store.", "N/A.", "N/A.", "Build properly.", "N/A."),
        s8=interview_block(f"Why is {name} empty?", "Roadmap placeholder with gateway route; not production feature.", "Staff: strangler pattern.", "Principal: delete if no 6-month plan.", "Priority vs RAG?"),
        s9=challenge_block("Delete scaffolds.", "Keep if funded on roadmap; else YAGNI—honest answer either way with trade-off."),
        s10="""Empty services confuse ops—label `tier=scaffold` in metrics.""",
        s11=f"""**Startup:** health. **Growth:** implement {future.split(' ')[0]}. **Enterprise:** full compliance. **Global:** multi-region audit storage.""",
        s12="""Zero ROI today; optional CAPEX; remove or fund explicitly.""",
    )

# Remaining services - ingestion, connector, search, platform-common, infra
add("Service: ingestion-service",
    s1="""**Business:** Turn raw uploaded text into durable, chunked knowledge ready for embedding.
**Technical:** Transactional persistence + chunk algorithm + sync embed call.
**Scalability:** Must become async; CPU scales with document size.
**Reliability:** Partial failure leaves DB without vectors.
**Without it:** uploads go nowhere.""",
    s2=cs_block(srp="Owns chunking policy and document write model.", dist="Local ACID for document+chunks; cross-service eventual consistency to embed index.", db="Normalized documents vs chunks; FK CASCADE.", sec="owner_email from trusted header."),
    s3="""800/100 chunking is embedding-model placeholder. @Transactional ensures document and chunks atomic; embed call intentionally outside XA—accept saga. Flyway validates schema discipline.""",
    s4=alts_block(
        ("Chunk in connector", "Fewer hops", "Connector becomes fat"),
        ("ingestion-service (chosen)", "Reusable for all sources", "Sync latency"),
        "ingestion-service",
        "All connectors share pipeline.",
    ),
    s5=trade_block("Uniform chunking.", "Blocking embed.", "Flyway.", "CPU on large docs.", "Trust X-User-Email.", "Medium.", "Kafka later."),
    s6=fail_block("**Embed fail after commit:** inconsistent. **DB down:** upload fails."),
    s7=scale_block("Serial per request.", "Thread pool exhaustion.", "Worker pool + queue.", "Partitioned processing.", "Embed HTTP.", "DB writes.", "Outbox+Kafka.", "Large doc memory."),
    s8=interview_block("Why sync embed?", "MVP INDEXED status in one call.", "Staff: outbox pattern next.", "Principal: 202 Accepted async.", "Chunk size tuning?"),
    s9=challenge_block("800 chars arbitrary?", "Placeholder for token-based chunking tied to embedding model."),
    s10="""Poison pills in PDF parsing—need DLQ.""",
    s11="""Text→PDF→OCR→multimodal.""",
    s12="""Core pipeline; fund before connectors scale.""",
)

add("Service: connector-service",
    s1="""**Business:** Abstract external systems (Confluence, etc.) behind one upload API.
**Technical:** MVP manual proxy to ingestion.
**Scalability:** Connector workers scale per upstream API limits.
**Reliability:** Upstream 429 should not crash ingestion JVM.
**Without it:** every source couples to ingestion.""",
    s2=cs_block(srp="Integration boundary.", dist="Anti-corruption layer between enterprise APIs and platform DTOs."),
    s3="""Manual controller proves contract before OAuth complexity. WebClient to ingestion with owner header.""",
    s4=alts_block(
        ("Ingestion only", "Simple", "OAuth in wrong place"),
        ("connector-service (chosen)", "Isolate credentials", "More services"),
        "connector-service",
        "Third-party volatility containment.",
    ),
    s5=trade_block("Safe credential scope.", "Extra hop.", "OAuth maintenance.", "Per-source workers.", "Vault for secrets.", "High.", "Many sources."),
    s6=fail_block("**Ingestion down:** upload fails."),
    s7=scale_block("Low.", "Per-source rate limits.", "Worker pools.", "Regional connectors.", "Upstream APIs.", "Connections.", "Bulk sync.", "API quotas."),
    s8=interview_block("Why not upload direct to ingestion?", "Future OAuth webhooks belong here.", "Staff: anti-corruption.", "Principal: data residency per source.", "Webhook security?"),
    s9=challenge_block("Pass-through service?", "Will gain sync state, credentials, DLQ—MVP is thin intentionally."),
    s10="""Storing Confluence tokens in env vars—use Vault.""",
    s11="""Manual→Confluence→full ECM.""",
    s12="""Integration tax; necessary for enterprise sale.""",
)

add("Service: search-service",
    s1="""**Business:** Employee and RAG retrieval API abstracting vector store.
**Technical:** Passthrough to embedding search today; future ACL + hybrid BM25.
**Without it:** RAG couples to embedding schema.""",
    s2=cs_block(srp="Query semantics owner.", dist="CQRS read path.", db="No local DB—stateless."),
    s3="""Thin service intentional—stable contract while embedding backend changes from Postgres to Pinecone.""",
    s4=alts_block(
        ("RAG calls embedding direct", "One less hop", "Leaky abstraction"),
        ("search-service (chosen)", "ACL/rerank home", "Latency"),
        "search-service",
        "Retrieval SLO ownership.",
    ),
    s5=trade_block("Stable API.", "Extra hop.", "Low.", "Cache here later.", "ACL enforcement point.", "Low.", "Hybrid search."),
    s6=fail_block("**Embedding down:** search empty."),
    s7=scale_block("Stateless scale.", "Cache.", "Shard.", "Geo.", "Backend.", "Network.", "Rerankers.", "Recall."),
    s8=interview_block("Why separate from embedding?", "Different release cycle and SLO.", "Staff: pre-filter ACL.", "Principal: evaluate cross-encoder here.", "p99 target?"),
    s9=challenge_block("Passthrough worthless?", "Not yet—boundary is the asset."),
    s10="""Skipping ACL—data leak between departments.""",
    s11="""Vector→hybrid→learned rerank.""",
    s12="""Low cost stateless; high value boundary.""",
)

add("Shared Module: platform-common (ApiResponse & DTOs)",
    s1="""**Business:** Client SDKs and services parse responses uniformly.
**Technical:** Shared records for cross-service contracts.
**Without it:** copy-paste DTO drift.""",
    s2=cs_block(srp="Shared kernel in DDD—minimize, only stable types.", dist="Coupling risk if abused—no business logic in common jar."),
    s3="""ApiResponse envelope allows evolving metadata without breaking `data` parsers. Java records for immutability.""",
    s4=alts_block(
        ("OpenAPI generate only", "Language agnostic", "Java still needs classes"),
        ("Shared JAR (chosen)", "Compile-time safety", "Tight coupling temptation"),
        "Shared JAR",
        "Monorepo makes version sync free.",
    ),
    s5=trade_block("Consistency.", "Coupling.", "Low.", "N/A.", "N/A.", "Version discipline.", "Medium."),
    s6=fail_block("**Breaking change:** all services must release together."),
    s7=scale_block("N/A.", "N/A.", "N/A.", "Split jar if too large.", "N/A.", "N/A.", "Semver.", "N/A."),
    s8=interview_block("Shared kernel vs duplicated DTOs?", "Monorepo favors kernel with discipline.", "Staff: never put entities in common.", "Principal: bounded context rules.", "Breaking change process?"),
    s9=challenge_block("Distributed monolith?", "Only DTOs—no repositories or services in common."),
    s10="""Teams dump business logic into common—forbidden.""",
    s11="""DTOs→OpenAPI→client SDKs.""",
    s12="""Essential glue; low cost.""",
)

add("Infrastructure: PostgreSQL (infra/docker-compose)",
    s1="""**Business:** Durable storage for users, documents, vectors (MVP).
**Technical:** Relational ACID for auth and ingest metadata.
**Without it:** in-memory demo only.""",
    s2=cs_block(db="ACID, indexes, FK integrity.", dist="Single-node CP in MVP—not HA."),
    s3="""Four logical databases in one instance for dev cost. Production: RDS with Multi-AZ.""",
    s4=alts_block(
        ("Single shared DB", "Cheaper dev", "Blast radius"),
        ("DB per service (chosen)", "Isolation", "More admin"),
        "DB per service on shared instance dev",
        "Production separates instances.",
    ),
    s5=trade_block("Familiar ops.", "Connection limits.", "Backup/restore.", "Vertical then read replicas.", "Encryption at rest needed.", "Flyway per service.", "Medium."),
    s6=fail_block("**Postgres down:** platform hard down. **Recovery:** restore RPO/RTO."),
    s7=scale_block("Dev single node.", "Bigger instance.", "Read replicas.", "Sharding rare for auth.", "Disk IO.", "Connections.", "PgBouncer.", "Single writer."),
    s8=interview_block("Why Postgres not Cassandra for audit?", "Audit not implemented; Postgres append-only partitions suffice until write rate proves NoSQL.", "Staff: time-series extension.", "Principal: compliance retention.", "When Cassandra?"),
    s9=challenge_block("One docker postgres for all DBs?", "Dev ergonomics; prod separates."),
    s10="""postgres/postgres in prod—breach magnet.""",
    s11="""Local→RDS→Aurora global.""",
    s12="""Known cost; fund HA before GA.""",
)

# Platform cross decisions
add("Platform Decision: RAG vs Fine-Tuning",
    s1="""**Business:** Answers must reflect today's policies and docs, with citations.
**Technical:** Retrieval injects fresh context; fine-tuning bakes static knowledge.
**Without RAG:** model stale; hallucination on new policies.""",
    s2=cs_block(dist="RAG = runtime information retrieval + generation; fine-tune = offline batch weight update."),
    s3="""Enterprise knowledge changes hourly (HR, security). Fine-tuning cycle weeks; cannot cite source. RAG chosen; fine-tune only for tone/format if ever.""",
    s4=alts_block(
        ("Fine-tune only", "Lower inference tokens", "Stale; no citations"),
        ("RAG (chosen)", "Fresh; provenance", "Retrieval quality dependency"),
        "RAG primary",
        "Regulated enterprises require provenance.",
    ),
    s5=trade_block("Compliance narrative.", "Retrieval must work.", "Eval harness.", "Index cost.", "ACL at retrieval.", "Two systems.", "Model choice."),
    s6=fail_block("**Bad retrieval:** confident wrong answers—worse than stub."),
    s7=scale_block("Index scales.", "ANN.", "Multi-index.", "Global shards.", "Retrieval.", "LLM.", "Hybrid.", "Context window."),
    s8=interview_block("Why RAG?", "Freshness and citations.", "Staff: cost.", "Principal: right to erasure maps to index deletes.", "Fine-tune when?"),
    s9=challenge_block("GPT-5 knows everything.", "Not your private Confluence; RAG is only path for internal data."),
    s10="""Hallucination lawsuits—citations mandatory.""",
    s11="""RAG→RAG+rerank→agents.""",
    s12="""Aligns with buyer compliance checklist.""",
)

add("Platform Decision: Synchronous REST vs Kafka (Current vs Target)",
    s1="""**Business:** MVP demo requires INDEXED in one HTTP response.
**Technical:** WebClient blocking chain connector→ingestion→embedding.
**Scalability:** Fails beyond moderate concurrent uploads.
**Without sync:** simpler ops for first demo—chosen temporarily.""",
    s2=cs_block(dist="Sync = strong coupling of latency; Kafka = temporal decoupling + load leveling."),
    s3="""Architect chose sync to validate contracts before broker ops. Known debt documented. Migration: outbox from ingestion, consumer on embedding.""",
    s4=alts_block(
        ("Kafka day 1", "Scale ready", "Slower MVP"),
        ("REST sync (current)", "Fast demo", "Coupling"),
        "REST now, Kafka at growth gate",
        "Measured migration.",
    ),
    s5=trade_block("Speed to MVP.", "Coupling failures.", "Low now.", "Poor at 100x ingest.", "Internal trust.", "Replace chain.", "Kafka ready."),
    s6=fail_block("**Timeout cascade:** upload fails if embed slow."),
    s7=scale_block("OK for demo.", "Pain starts.", "Kafka required.", "Partitioned pipeline.", "Chain length.", "Threads.", "Async.", "Little's Law."),
    s8=interview_block("Why REST now?", "Prove product; insert Kafka without boundary change.", "Staff: outbox.", "Principal: define growth metric to switch.", "Saga state?"),
    s9=challenge_block("Sync is amateur.", "Appropriate for MVP gate; enterprise path documented."),
    s10="""Cascading timeouts under load—classic.""",
    s11="""Sync→outbox→Kafka.""",
    s12="""Acceptable with explicit milestone to async.""",
)

# Global sections
GLOBAL_PRINCIPAL = """
# Part VII — Global Principal Engineer Challenges

## Challenge: Why microservices instead of a monolith?

**Weak defense:** Microservices are industry standard.

**Principal defense:** We optimize for independent scaling and failure isolation across workloads whose resource profiles differ by orders of magnitude—ingestion is CPU/IO bound and bursty; RAG is latency-bound and dominated by external LLM APIs; auth is security-bound and changes with enterprise IdP projects. We accept operational cost only where boundaries are already proven by the MVP vertical slice. Merge criteria are explicit: if inter-service traffic stays low and team size <5 for two quarters, collapse embedding+search into one deployable while keeping logical modules. The monorepo preserves refactorability so physical decomposition is reversible.

## Challenge: Why Kafka instead of REST?

**Principal defense:** We do not use Kafka in the MVP—REST validates contracts. Kafka enters when measured ingest backlog or p99 upload latency violates SLO despite horizontal ingestion scale. Kafka provides log-based replay (re-embed on model upgrade), load leveling, and fan-out to audit/notification without N synchronous hops. REST remains correct for request/response queries (search, chat). The theory is temporal decoupling, not religion.

## Challenge: Why PostgreSQL instead of Cassandra?

**Principal defense:** Access patterns are relational: unique emails, FK chunks→documents, transactional ingest. Write volume today is far below Cassandra's sweet spot. Audit at extreme scale may use Cassandra or ClickHouse—partition when write metrics demand it, not before. Postgres + partitioning + read replicas handle enterprise-stage audit until proven otherwise (PACELC: we choose consistency for auth, accept operational simplicity).

## Challenge: Why Redis instead of local cache?

**Principal defense:** We do not run Redis in MVP. When gateway replicas >1, rate limits and hot-query caches require shared state—Caffeine cannot coordinate. Redis is an economic optimization triggered by LLM cost or search p99, not a day-one dependency.

## Challenge: Why Gateway instead of direct service access?

**Principal defense:** Zero Trust requires no public microservice ports. Gateway concentrates JWT validation, future WAF/rate limits, and identity propagation—backends stay private. Direct access would duplicate OAuth2 resource servers in N services (violation of DRY and security review surface).

## Challenge: Why RAG instead of fine-tuning?

**Principal defense:** Fine-tuning optimizes weights for static distributions; enterprise knowledge is non-stationary and confidential. RAG provides provenance (citations) required for compliance interviews with legal. Fine-tuning may supplement style, not replace retrieval.

## Challenge: Why Vector DB instead of relational search?

**Principal defense:** Relational `LIKE` cannot solve semantic paraphrase ("PTO policy" vs "vacation days"). Vectors approximate semantic similarity in high-dimensional embedding space. We start with Postgres JSON + brute force for MVP; production requires ANN index (pgvector HNSW or managed vector store)—the service boundary exists before the storage engine choice finalizes.
"""

GLOBAL_CTO = """
# Part VIII — CTO Review (Full Platform)

## Cost

- **Current:** Ten JVM processes + single Postgres in dev—high fixed cost for small team.
- **Unit economics:** RAG COGS dominated by LLM tokens, not Java hosting.
- **Decision:** Accept microservice ops cost only when revenue or compliance mandates; otherwise merge hot paths after metrics review.

## Risk

| Risk | Severity | Mitigation |
|------|----------|------------|
| Open internal ports | High | mTLS, network policies |
| HS256 dev secret | High | Vault + RS256 |
| O(N) search | High | pgvector before GA |
| No audit trail | High | audit-service + events |
| Prompt injection | High | policy + evals |

## Scalability

Boundaries are correct; implementations are MVP-grade. Path to millions: async ingest, ANN index, gateway scale-out, model gateway, multi-region read replicas.

## Team structure

Services map to future squads: Platform (gateway/auth), Knowledge (connect/ingest/embed), Intelligence (search/rag/agent), Governance (audit/notification). Do not staff all squads until traffic exists.

## Operational burden

High for current maturity—require CI matrix, Helm umbrella chart, centralized logging before selling enterprise SLA.

## Long-term maintainability

Monorepo + clear DTOs + Flyway = strong. Risk: scaffolds without owners—delete or fund within two quarters.

## Executive recommendation

Proceed to Growth stage investments: real embeddings, OIDC, audit events, observability, and async ingestion when upload SLO breaches threshold. Delay agent features until RAG eval scores meet compliance bar.
"""

CLASS_INDEX = """
# Appendix A — Class & Component Index (Reasoning Pointers)

| Component | Location | Defend in one line |
|-----------|----------|-------------------|
| GatewayServiceApplication | gateway | Bootstraps reactive edge |
| GatewayHealthController | gateway | Local health—not proxied |
| GatewaySecurityConfig | gateway | JWT resource server—fail closed |
| UserEmailGatewayFilter | gateway | Identity propagation post-auth |
| AuthController | auth | Thin HTTP adapter |
| AuthService | auth | Transactional register; stateless login |
| JwtTokenService | auth | Token format owner |
| User / UserRepository | auth | Persistence boundary |
| DevUserInitializer | auth | Demo only—disable in prod |
| ManualDocumentConnectorController | connector | Anti-corruption entry |
| IngestionClient | connector | WebClient to ingestion |
| DocumentController | ingestion | HTTP adapter |
| DocumentIngestionService | ingestion | Saga orchestrator |
| TextChunker | ingestion | Chunking policy isolated |
| EmbeddingClient | ingestion | Cross-service embed invoke |
| EmbeddingController | embedding | Index + search API |
| EmbeddingIndexService | embedding | Write path |
| EmbeddingSearchService | embedding | Read path—O(N) debt |
| EmbeddingMath | embedding | Pure functions—testable |
| SearchController | search | Stable retrieval API |
| EmbeddingSearchClient | search | Delegates to embedding |
| RagChatController | rag | Product API |
| RagChatService | rag | Orchestration only |
| LlmAnswerService | rag | LLM + stub degradation |
| SearchClient | rag | Retrieval delegate |
| ApiResponse | platform-common | Envelope evolution |
| All *DTO records | platform-common | Contract stability |
| ServiceHealthController ×9 | all services | K8s probe uniformity |
"""

def main():
    parts = [
        "# Architect Reasoning & Interview Guide\n",
        "## Enterprise AI Platform — Principal Engineer Training Manual\n\n",
        "> **Do not read this as code documentation.** Read it as the reasoning record of architectural decisions, "
        "the theories that justify them, and the language to defend them to Senior through Distinguished engineers and CTOs.\n\n",
        "**Repository:** `enterprise-ai-platform` · **Version:** 0.0.1-SNAPSHOT · **Maturity:** Phase 1 MVP\n\n",
        "---\n",
        "# How to Use This Guide\n\n",
        "Each component includes twelve sections: problem, theory, architect reasoning, alternatives, trade-offs, "
        "failure theory, scalability theory, interview defense, principal challenges, production lessons, evolution roadmap, "
        "and CTO lens. Study in order: Platform decisions → Services → APIs → Data → Planned infrastructure → Global reviews.\n\n",
        "---\n",
        "# Part I — Platform-Wide Architectural Decisions\n",
    ]
    for title, kwargs in COMPONENTS:
        parts.append(comp(title, kwargs))
    parts.append(GLOBAL_PRINCIPAL)
    parts.append(GLOBAL_CTO)
    parts.append(CLASS_INDEX)
    parts.append("\n---\n*End of Architect Reasoning & Interview Guide*\n")

    MD_OUT.write_text("".join(parts), encoding="utf-8")
    print(f"Wrote {MD_OUT} ({MD_OUT.stat().st_size // 1024} KB)")

    # Convert to docx
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from md_to_docx import convert
    convert(MD_OUT, DOCX_OUT)
    print(f"Wrote {DOCX_OUT}")


if __name__ == "__main__":
    main()
