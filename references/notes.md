# Notes — rationale, evidence, examples

Load when a finding needs justification, when a practice's mechanism is unclear, or when writing new code. SKILL.md is the operational checklist; this is the why.

## Contents
1. Verify before asserting (commands)
2. Provenance of the practices
3. Extended notes on the practices that testing proved necessary
4. Corpus: six repos, what each taught
5. Migration notes for legacy-era code

---

## 1. Verify before asserting

Middleware names and kwargs drift between versions (`SummarizationMiddleware` already carries `**deprecated_kwargs`). Before telling a user a signature is wrong:

```bash
python -c "import langchain, inspect; from langchain.agents import middleware; from langchain.agents.middleware import PIIMiddleware; print(langchain.__version__); print(sorted(middleware.__all__)); print(inspect.signature(PIIMiddleware.__init__))"
```

No environment available → mark API-level findings "verify against your version" rather than asserting. The principles are stable; the kwargs are not.

Verified at time of writing (langchain v1): `ModelCallLimitMiddleware(*, thread_limit=, run_limit=, exit_behavior=)`; `ToolCallLimitMiddleware(*, tool_name=, thread_limit=, run_limit=)`; `HumanInTheLoopMiddleware(interrupt_on={...}, *, description_prefix=)`; `SummarizationMiddleware(model, *, trigger=, keep=, token_counter=, summary_prompt=)`; `ModelFallbackMiddleware(first_model, *additional)`; `PIIMiddleware(pii_type, *, strategy="redact", detector=, apply_to_input=True, apply_to_output=False, apply_to_tool_results=False)`. Agent result key: `result["structured_response"]`.

## 2. Provenance

- **1–18**: read off the LangChain repo — the `create_agent` signature (17 params, three typed overloads), the middleware catalog (21 modules ≈ a census of what production agents need), `model-profiles`, `standard-tests`, and the team's own AGENTS.md style rules.
- **19–20**: general agent-engineering practice; the repo's `standard-tests` and tracing hooks support but don't prove them.
- **21**: the preserved legacy-vs-current diff in `langchain-ai/open_deep_research`.
- **22**: `beenuar/AiSOC`'s untrusted-input handling, plus the enforcement-layer failure in `chatchat-space/Langchain-Chatchat`.

## 3. Extended notes

**#5 — the best form of model config.** Onyx and AiSOC both route a *logical role* (`aisoc-triage`) through a gateway (LiteLLM) that owns alias → model mapping, with per-role env overrides. Operators re-point models, add fallbacks, or swap providers with no code change and no deploy. In a regulated setting this is also the natural seam for enforcing which models are approved for which data classification.

**#10 — why parse-failure defaults are 🔴.** AiSOC's five agents each do `verdict = data.get("verdict", "true_positive")` and coerce unknown values to the same default. Fail-closed is defensible; the defect is that the default is *indistinguishable* from a real verdict — no provenance flag, no `parse_degraded` marker. Analyst trust erodes invisibly. The fix isn't a different default, it's an explicit `undetermined` state the UI can render differently.

**#17 — what middleware order does and doesn't do.** Hooks compose onion-style, so earlier entries are outer. Order decides what each middleware *sees*: summarization before redaction summarizes un-redacted text. It does **not** govern tracing, because tracers are callbacks on the model/tool call. Keeping raw PII out of LangSmith/OTel is `apply_to_*` flags plus tracer config.

**#21 — the evidence.** ODR's legacy design was six hand-designed stages (`generate_report_plan → human_feedback → generate_queries → search_web → write_section(grade) → write_final_sections → compile_final_report`) over a rich ontology (`Section`, `Queries`, `Feedback(grade: pass|fail)`). The current design is two generic loops (supervisor → researchers) over verbs (`ConductResearch`, `ResearchComplete`, `think_tool`). Forced reflection became an optional tool; HITL moved from mid-flight plan approval to upfront scoping; parallelism went dynamic with a config governor. The one thing *added* was a dedicated compression stage — removing hand-designed process required adding infrastructure to manage what the freed-up process produces.

**#22 — enforcement layer, worked example.** Chatchat's text-to-SQL guards read-only two ways: an LLM asked whether the query is read-only (gated by substring match on its prose), then a SQLAlchemy interceptor checking `statement.strip().lower().startswith(op)` against eight keywords. The interceptor misses leading comments, CTEs, `EXPLAIN ANALYZE DELETE`, stacked statements, and `MERGE`/`REPLACE`/`GRANT`/`SET`/`CALL`/`LOAD`. The SQL is LLM-written from user text, so an attacker controls the prefix. Correct enforcement: connect as a read-only DB role.

**Counter-example worth knowing (#10, fail-loud done right).** CyberVerse ships a hash-bucket `HashEmbeddings` fallback that would destroy retrieval quality — but it's reachable only when the provider is *explicitly* configured `fake`, and a missing `langchain-openai` raises `RuntimeError` with an actionable message. Same ingredient as AiSOC's bug, opposite outcome, because degradation requires opt-in.

## 4. Corpus

| Repo | Shape | Finding | Class |
|---|---|---|---|
| langchain-ai/open_deep_research | graph-native | `or True` making an error classifier dead code; every exception silently ends research | guarantee neutralized |
| beenuar/AiSOC | graph-native | parse failure → confident `true_positive` | fallback indistinguishable from real |
| chatchat-space/Langchain-Chatchat | legacy | read-only via `startswith`; `langchain_experimental` in prod | enforcement in wrong layer |
| Lynpoint/CyberVerse | library use | (none of this class) — path containment only | control case |
| onyx-dot-app/onyx | library use | unbounded `tenant:model` caches and lock dicts; DB commit per LLM call | wrong lifetime / frequency |
| khoj-ai/khoj | library use | hardcoded context table w/ magic default; quadratic truncation on hot path | wrong cost |

**Best-in-corpus practices to imitate:** Onyx — tenant-scoped cache keys with the reason in a comment, per-(tenant, model) locks chosen over a global lock, cost tracking gated on two flags and failing soft. Khoj — dropping a `tool_call` also drops its orphaned `tool_result`; system messages extracted before truncation; per-tier rate limits. AiSOC — `wrap_untrusted()` delimiting, and a `safe_ainvoke` wrapper enforcing a message contract at every call site (middleware reinvented for a graph-native app). CyberVerse — `VectorStoreBackend` ABC with lazy provider imports; allowlist-regex name sanitization.

## 5. Migration notes (legacy → v1)

`LLMChain` → LCEL (`prompt | llm`), usually ~4 lines. `initialize_agent`/`AgentExecutor` → `create_agent`. `ConversationBufferMemory` → checkpointer + thread_id. `RetrievalQA` → retriever + `create_agent` or an explicit LCEL chain. `langchain_community` imports for OpenAI/Anthropic/etc. → partner packages.

**Review legacy code on its merits first.** Migration carries defects straight across; the defect is the finding, the migration is housekeeping.
