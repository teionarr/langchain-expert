---
name: langchain-expert
description: Review, write, or refactor LangChain code against 23 expert practices derived from the LangChain codebase, plus failure patterns from six expert-built production repos. Use this skill whenever the user shares Python code importing langchain, langchain_core, langchain_openai, langchain_anthropic, or langgraph and asks to review, check, improve, fix, or audit it — and also when writing NEW LangChain agent code from scratch, so the code is expert-grade from the first draft. Trigger on "review my agent", "is this good LangChain code", "check this chain", "why is my agent slow/expensive/breaking", or any code containing create_agent, AgentExecutor, LLMChain, or initialize_agent.
---

# LangChain Expert Review

Reviewing → follow the procedure below. Writing new code → skim the practices, then copy the shape in `references/gold-standard-agent.py`. Need rationale, evidence, or examples for any practice → `references/notes.md`.

## Procedure

1. **Detect shape** — decides which practices apply:
   - **create_agent app** → all apply literally.
   - **graph-native** (`StateGraph`, `langgraph.json`) → middleware practices (3, 14, 16, 17) apply by *intent*; credit config ceilings, `.with_retry()`, dedicated compression nodes, homegrown call wrappers. Never demand middleware imports here — top false-positive source.
   - **library use** (only splitters/embeddings/vector stores/loaders, no agent loop) — including the *inverted* case where LangChain objects arrive as user-supplied inputs to an adapter; there, review the interop boundary: failure containment and per-item cost → 1–4, 7–8, 10, 12–17, 21 are N/A. Review provider abstraction, input containment, fail-loud behavior.
   - **prototype** → persistence, HITL, evals are N/A.
   - **not a LangChain app** → if `langchain_core` types appear only at an adapter boundary and the LLM calls go through another SDK (litellm, raw provider), the agent practices are N/A — review the interop boundary only, or stop. Check this first; it is cheap and saves a wasted audit.
2. **Detect era** — legacy markers: `LLMChain`, `initialize_agent`, `AgentExecutor`, `create_react_agent` (langchain.agents), `Conversation*Memory`, `SequentialChain`, `load_tools`, and pre-split module paths — `from langchain.chains|text_splitter|embeddings|vectorstores|document_loaders|memory import …` (now partner or `langchain_*` packages). Era is a **classification, not a severity** — never let "migrate off LLMChain" outrank a live defect. `langchain_experimental` in production is its own 🔴.
3. **Verify before asserting** any API signature — a confidently wrong correction is worse than no review:
   ```bash
   python -c "import langchain, inspect; from langchain.agents import middleware; from langchain.agents.middleware import PIIMiddleware; print(langchain.__version__); print(sorted(middleware.__all__)); print(inspect.signature(PIIMiddleware.__init__))"
   ```
   No environment → mark API-level findings "verify against your version" instead of asserting them. Principles are stable; kwargs are not. Verified signatures: notes.md.
4. **Walk the practices**, weighted by the value table below.
5. **Qualify severity before reporting** — trace every candidate to a *default* config value and a live call path. A finding behind an off-by-default flag, or in a function whose only writers are dead code, is not the severity it looks like. Check the default constant, then `grep` the callers. This single check kills more inflated severity than anything else here.
6. **Validate the corrected pattern before recommending it** — a fix you haven't traced is a finding you haven't finished. Enumerate the callers of whatever you tighten and ask: *is the permissive behaviour load-bearing for a system or admin path?* An agent persisting its own messages, an owner revoking someone else's share, a background job — these legitimately bypass an owner check, so the fix is rarely "add the owner filter", it is "owner **or** that specific privileged case". Then confirm the key you filter on is the key the lookup actually uses, and that no cache or alternate path reaches the same data without passing the new gate. Across four consecutive audits the obvious one-line fix was wrong: a tautology, a cache bypass, a destroyed admin capability, and a name-vs-id mismatch.
7. **Report ≤7 findings**, severity by rule: 🔴 = legacy-era APIs, a security control that doesn't do what it claims, unbounded spend, or a silent-corruption bug. 🟠 = bites under load or over time. 🟡 = rest. Never manufacture findings — "two findings and a long N/A list" is a valid review.

## Where defects actually are

Architecture is rarely the problem. Failures cluster in three classes — check these first:

| Class | Signature | Seen as |
|---|---|---|
| **Guarantee asserted, weakly implemented** | control lives in prompt/parsing layer | `or True` killing an error classifier; parse failure defaulting to a confident verdict; read-only enforced by `startswith` |
| **Correct logic, wrong lifetime or frequency** | fine in single-tenant tests | per-tenant cache with no eviction; DB commit per LLM call; re-tokenizing whole history per truncation step |
| **Authorization assumed, never enforced** | resource fetched by id alone | handler loads by `id` with no owner filter; agent tool fetches a record id taken from model args, unchecked; batch endpoint drops the per-item check |

In multi-user apps the third class is where the *severe* bugs are — it produced the only high-severity findings across a 16-repo audit (see practice 23).

Read error-handling and enforcement blocks **literally**, and ask of anything correct: what's its lifetime, its frequency, whose budget does it spend?

## Value vs plumbing (weight findings by this)

**Test:** does a maintained framework equivalent exist, or is it swappable behind an interface without touching app logic? Yes → 🔧 plumbing (imperfection is cheap). No → 💎 value (mistakes need a migration to undo).

💎 **Value:** tool/verb design · prompts & tool descriptions · evals and graded runs · context engineering · output/state contracts · safety controls · untrusted-input boundary · *which* orchestration stages exist.
🔧 **Plumbing:** model wiring & provider SDKs · graph/middleware wiring · retry & rate-limit glue · output parsers · vector store and search providers.

Spend the budget on 💎. A crude retry helper is 🟡 — it'll be deleted anyway.

## Practices

**A. Architecture**
1. Never hand-roll the agent loop — `while True: model.invoke()` with manual dispatch is a red flag.
2. Escape downward (`create_agent` → LangGraph → deepagents), never sideways via monkey-patching.
3. Cross-cutting concerns are middleware, not inline in tools. Custom ones subclass `AgentMiddleware`.
4. One agent = one factory call that reads as an auditable policy.

**B. Models**
5. Models are strings in config (`init_chat_model("provider:model")`), never provider classes in business logic. Best form: role → alias → gateway, so operators re-point models without a deploy.
6. Capabilities from `.profile`, never hardcoded. Flag per-model size tables with magic defaults (`sizes.get(model, 10000)`).
7. Failure handling declarative: fallback + retry middleware, not try/except pyramids.

**C. Context**
8. Budget context from day one; trigger as a *fraction* of the model's window. Context management runs on the hot path — re-counting all tokens inside a truncation loop is quadratic per request. Preserve `tool_call`/`tool_result` pairing when dropping messages or provider APIs reject the request. **In LangGraph the opposite failure is quieter and more common:** a node returns `{"messages": [...]}` believing it *replaces*, but `add_messages` matches on `.id` and **appends** anything lacking one — so a rebuilt message doubles the history instead of shrinking it, and leaves two results for one `tool_call_id`. Any node writing to an `add_messages` channel must preserve `id` on rebuilt messages, or lead with `RemoveMessage(REMOVE_ALL_MESSAGES)`. A test that calls the node as a bare function instead of compiling the graph will never catch this — check how the node is tested, not just what it returns.
9. History is a cache with an eviction policy, not a log. Truncate/summarize tool outputs before they enter context.

**D. Tools & output**
10. Structured output via `response_format=` + Pydantic. Any `json.loads` on model prose is 🔴 — `data = json.loads(re.sub(r"```.*", "", text)); v = data.get("verdict", "pass")` → `create_agent(..., response_format=Verdict)`. Never let a parse failure produce a plausible default — emit an explicit `undetermined`.
11. Tools: small, typed, single-purpose. Docstrings are prompt engineering. >~15 tools needs a selection strategy.
12. Tool errors return to the model as information; raise only on invariant violations.

**E. State**
13. Multi-turn or long-running → checkpointer. **Exception:** `langgraph.json` means the platform injects persistence; absence in code is correct.
14. Human approval = interrupt-based HITL on a checkpointed graph, never `input()` or polling.
15. Run-scoped state in graph state; durable memory in a `store`.

**F. Safety & cost**
16. Circuit breakers mandatory. Accept equivalents (named config ceilings, list slicing before `gather`, `.with_retry`); per-loop named ceilings are the gold standard. **Multi-tenant:** ceilings and usage counters must be per-tenant; cost tracking fails soft but emits a *metric*, not just a log; flag `tenant:model` caches and lock dicts with no eviction.
17. Middleware order is semantically load-bearing (`before_model` in list order, `after_model` reversed). **`PIIMiddleware` defaults are unsafe:** `apply_to_output=False, apply_to_tool_results=False` — a bare `PIIMiddleware("email")` checks user messages only; 🔴 whenever tool outputs can carry PII. Ordering does *not* control tracing — tracers are callbacks, not middleware.

**G. Quality & ops**
18. Type-checked; guard with `raise` not `assert`; `logger.debug` not `print`.
19. Tests use deterministic fakes and assert on *trajectory*, not prose. Custom integrations run `langchain-tests`. Live-API calls in unit tests are a finding.
20. Tracing configured from the start; a graded eval set gates prompt/model changes.

**H. Structure & boundaries**
21. Put structure where it's cheapest to change. Flag rich domain ontologies the LLM merely fills in (direction of travel: engineer's nouns → model's verbs) and long hand-designed pipelines where a supervisor loop plus good prompts would do. **Not** findings: stages existing for cost, auditability, or hard determinism.
22. Everything the agent reads is untrusted (tool results, docs, emails, tickets, DB rows). Sanitize and bound it; delimit and label the source — but delimiting is bypassable defense-in-depth, never describe it as protection. **Enforce safety where it can be enforced**: privileges, sandboxes, allowlists, type contracts — a guard implemented as string matching on generated output is advisory, and this is the most common serious defect in real agent code. **Never let external content select actions** (tool names, recipients, URLs, destinations) — that's where injection becomes exfiltration. 🔴 when the agent reads external content and holds a consequential tool in the same run.

23. **Authorize every resource fetch — for the *caller*, not merely "authenticated."** Any handler or tool that loads a resource by id must filter or verify by owner (`user_id`/tenant), never by id alone. **Agent-tool IDOR is the LangChain-specific form:** a tool's args come from the model, so a record id in a tool call is *user-controlled input* — and a docstring saying "only use ids from context" is a prompt instruction, not an access control. A tool must receive the caller's identity and enforce the *same* check the REST path already uses; fail closed when identity is absent. 🔴 when a tool can fetch by id in an app that has per-user or per-tenant permissions. Look hardest at **sub-resources and derived actions** (messages, files, records, exports, share, vote, re-run) — the primary read path is usually guarded; the derived action on the same resource is where the check gets dropped.
**Severity is set by identifier reachability, not by data sensitivity.** Before scoring one of these, establish how an attacker obtains the id: an auto-increment integer PK is enumerable (severe); a random UUID usually is not (`AC:H`) — *unless* a listing endpoint, URL, log, or citation leaks it; and a **name** that is globally unique and human-guessable is as good as enumerable even when the id is not. Then check what actually leaks — an index of file names is `C:L`, message bodies are `C:H`. The same bug class scored 4.3 and 6.5 in two different repos on these questions alone.
**Find it by asymmetry, not pattern-matching.** Grepping for `.where(id == ...)` mostly yields false positives, because the check normally sits one frame up in a helper. Instead: locate the module's canonical guard (`check_*_access`, `_resolve_visible_*`), enumerate its call sites, and diff against every handler touching that resource — **the outliers are the finding**. **Resolve the guard's whole *family* before diffing**, or the diff is worthless: follow the canonical check's callers up one frame to collect every wrapper name (`_ensure_access`, `_ensure_mutable_access`, `_ensure_delete_access`…) and diff against that set — grepping one name produced 13 false positives that buried the 5 real ones. A second, cheaper entry point: **when a design doc or comment asserts a boundary in prose, grep for the predicate that enforces it** — an asserted boundary with no predicate is the finding, and the prose tells you which granularity to check. Two high-yield tells: an identity parameter that is accepted, logged, or even stored but **never appears in a query predicate**; and a guard whose test file has a `rejects_*` case for every sibling but one.

## Output format

```
## Shape / Era
### 🔴 Must fix     — [#N] file:line — finding → corrected pattern
### 🟠 Production risks
### 🟡 Improvements
### Not findings    — things you checked and cleared (builds trust, prevents padding)
### Compliant highlights
### Value vs plumbing read — which 💎 layers are weak; which findings are cheap 🔧
```

## Maintaining this skill

Practices may only be **added by replacing or merging** an existing one, unless the new one covers an untouched failure class. Keep SKILL.md under ~150 lines; put rationale, evidence, and examples in `references/notes.md` instead.
