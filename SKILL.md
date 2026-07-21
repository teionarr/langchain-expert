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
4. **Walk the practices**, weighted by the value table below. Expect most to be N/A on mature code and most to fire on early code — the practices are a floor, not a ranking, so never skip the "basic" ones because a repo looks sophisticated.
5. **Kill candidates cheaply, in this order** — the moment you have a candidate and *before* you invest in writing it up. Each gate is disqualifying and costs seconds; skipping them has cost whole audits.
   - **Already fixed?** `git log --follow` the file. A commit that *created* the line you're calling a bug ends the finding — and if it also rewrote the test to assert that behaviour, the maintainer has told you it's the design.
   - **Already known?** Published advisories **paginated** (`--paginate`, or `per_page=100` — a default page size once truncated 77 advisories to 30 and became a whole audit's baseline), then issues and PRs in all states. An incomplete-fix report is legitimate, but must be framed as the delta.
   - **Actually reachable?** A *default* config value and a live call path. Not dead code, not behind an off-by-default flag.
   - **In scope?** If you intend to disclose, read the project's `SECURITY.md` **exclusions** now, not at submission. Some dismiss static-only findings outright and require a runnable PoC — which can invalidate the whole audit after the fact.
6. **Execute the fix; don't argue about it.** Clone, patch, run their suite. This is the one change with clean evidence behind it: every fix we *ran* held, and every fix we only *reasoned about* was later rewritten — a tautology, a cache bypass, a destroyed admin capability, a name-vs-id mismatch, a broken disaster-recovery path, a shallow copy that shared the very state it meant to isolate, a filter on a column the table doesn't have, and a path prefix that would have rejected every legitimate download. If you genuinely cannot run it, mark the fix **untested** in the report and reason carefully instead: enumerate the callers of whatever you tighten and ask *is the permissive behaviour load-bearing for a system or admin path?* An agent persisting its own messages, an owner revoking someone else's share, a background job — these legitimately bypass an owner check, so the fix is rarely "add the owner filter", it is "owner **or** that specific privileged case". Confirm the key you filter on is the key the lookup actually uses, and that no cache or alternate route reaches the same data without passing the new gate.
7. **Red-team the report before it leaves the room** — for anything you'd disclose or ship (🔴/🟠). Do it in a **fresh context**: hand over the claims and `file:line` refs, *not* your reasoning. Independence is the whole mechanism — re-reading your own finding defends it. (A subagent is the easy way; a colleague who hasn't seen the audit works as well.) Instruct it to **attack** four things — but do *not* tell it to default to refuted: in a controlled re-run, that instruction caused a reviewer to drop two valid findings (CVSS 8.8 and 8.0) and refute a third that a neutral reviewer confirmed. Pressure to reach a verdict produces premature closure, not rigour. Let it keep working. Attack: **scope** — read the project's `SECURITY.md` *exclusions* before you audit, not before you submit: several explicitly dismiss static-only findings and require a runnable PoC, which can invalidate an entire audit after the fact. Then **novelty** — start with `git log --follow` on the file the finding lives in, *before* searching trackers: a recent commit that **created** the line you are calling a bug ends the finding outright, and this is the cheapest check available. Then published advisories — **paginate them**; a default page size silently truncated ours to 30 of 77 and became the baseline for a whole audit (not just issues and PRs — a repo with many advisories will have patched the obvious things, and an incomplete-fix report is legitimate but must be framed as the delta); **the load-bearing claim** — the one sentence the finding dies without, checked against the code rather than the docstring; **the fix** — which shipped behaviour does it break; **severity** — the honest vector given what the attacker must already hold, and whether an enumeration primitive really exists. Red-team the **set**, not each finding alone: only a cross-finding pass catches a mis-ranked lead or a disprovable sub-claim that would discredit the sound ones. Do **not** tell it what outcome to expect, or what previous passes concluded — a reviewer handed a running tally contributes to it. And prefer **executing** the fix over arguing about it — clone, patch, run their suite. Argued fix-verdicts proved *non-reproducible* under a controlled re-run: same inputs, same code, different reviewer framing, materially different conclusions in 3 of 3 trials. An executed fix is evidence; an argued one is an opinion.
8. **Every finding carries a receipt.** One line each: the command you ran and what it showed — the `git log` that proved it wasn't already fixed, the grep showing the default value and the live callers, the test run before and after your patch. **No receipt → it is a lead, not a finding**, and say so. Severity is *your assessment, not a verdict*: state the basis alongside it — what the attacker must already hold, whether an enumeration primitive exists, what actually leaks — because every severity we assigned before doing that was later revised. Give a CVSS vector when disclosing; most policies require one.
9. **Report ≤7 findings**, severity by rule: 🔴 = legacy-era APIs, a security control that doesn't do what it claims, unbounded spend, or a silent-corruption bug. 🟠 = bites under load or over time. 🟡 = rest. Never manufacture findings — "two findings and a long N/A list" is a valid review.

## Where defects actually are

Architecture is rarely the problem. Failures cluster in three classes — check these first:

| Class | Signature | Seen as |
|---|---|---|
| **Guarantee asserted, weakly implemented** | control lives in prompt/parsing layer | `or True` killing an error classifier; parse failure defaulting to a confident verdict; read-only enforced by `startswith` |
| **Correct logic, wrong lifetime or frequency** | fine in single-tenant tests | per-tenant cache with no eviction; DB commit per LLM call; re-tokenizing whole history per truncation step; **a module-level tool/model singleton rebound per request** |
| **Authorization assumed, never enforced** | resource fetched by id alone | handler loads by `id` with no owner filter; agent tool fetches a record id taken from model args, unchecked; batch endpoint drops the per-item check |

In multi-user apps the third class is where the *severe* bugs are — it is where every high-severity finding in a 22-repo audit landed (see practice 23) — though note that counts where the lens fired, not where it was right.

Read error-handling and enforcement blocks **literally**, and ask of anything correct: what's its lifetime, its frequency, whose budget does it spend?

**Gradio/Streamlit-shaped apps deserve a specific look:** there is no request object to make sharing visible, so per-request mutation of a module-level singleton (`TOOL_REGISTRY[name].retrievers = user_scoped`) reads as ordinary code and is the highest-yield bug in that shape — under concurrency it serves one user's private documents inside another user's answer. The tell is a per-request value assigned onto an object that was constructed at import time.

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

23. **Authorize every resource fetch — for the *caller*, not merely "authenticated."** Any handler or tool that loads a resource by id must filter or verify by owner (`user_id`/tenant), never by id alone. **Agent-tool IDOR is the LangChain-specific form:** a tool's args come from the model, so a record id in a tool call is *user-controlled input* — and a docstring saying "only use ids from context" is a prompt instruction, not an access control. A tool must receive the caller's identity and enforce the *same* check the REST path already uses; fail closed when identity is absent. **The shape that prevents it — verified correct in four of six audited multi-user apps:** bind identity into the **tool factory's closure at build time** (`create_tools(user_id, workspace_id, …)`) so it can never be a model argument, and **re-root any model-supplied scope key under the authenticated one** rather than trusting it (`canonical_session_uri(ctx, client_value)`). If a tool's `args_schema` contains a tenant, user, namespace, or owner field, that is the bug. 🔴 when a tool can fetch by id in an app that has per-user or per-tenant permissions. Look hardest at **sub-resources and derived actions** (messages, files, records, exports, share, vote, re-run) — the primary read path is usually guarded; the derived action on the same resource is where the check gets dropped.
**Severity is set by identifier reachability, not by data sensitivity.** Before scoring one of these, establish how an attacker obtains the id: an auto-increment integer PK is enumerable (severe); a random UUID usually is not (`AC:H`) — *unless* a listing endpoint, URL, log, or citation leaks it; and a **name** that is globally unique and human-guessable is as good as enumerable even when the id is not. Then check what actually leaks — an index of file names is `C:L`, message bodies are `C:H`. The same bug class scored 4.3 and 6.5 in two different repos on these questions alone.
**Find it by asymmetry, not pattern-matching.** Grepping for `.where(id == ...)` mostly yields false positives, because the check normally sits one frame up in a helper. Instead: locate the module's canonical guard (`check_*_access`, `_resolve_visible_*`), enumerate its call sites, and diff against every handler touching that resource — **the outliers are the finding**. **Resolve the guard's whole *family* before diffing**, or the diff is worthless: follow the canonical check's callers up one frame to collect every wrapper name (`_ensure_access`, `_ensure_mutable_access`, `_ensure_delete_access`…) and diff against that set — grepping one name produced 13 false positives that buried the 5 real ones. A second, cheaper entry point: **when a design doc or comment asserts a boundary in prose, grep for the predicate that enforces it** — an asserted boundary with no predicate is the finding, and the prose tells you which granularity to check. Two high-yield tells: an identity parameter that is accepted, logged, or even stored but **never appears in a query predicate**; and a guard whose test file has a `rejects_*` case for every sibling but one.
**A guard that is present can still be defeated — check what it is called *with*, and what it then acts *on*.** Two shapes the diff above cannot see, because both answer "guard present, guard called, identity passed": a call site that hands the guard **the same object as both the subject and the baseline**, making the comparison self-satisfying and the ownership branch unreachable; and a guard that authorizes identifier **A** and then operates on an unrelated caller-supplied identifier **B** — checking that you own the session, then signing whatever object key arrived alongside it. The second is the more dangerous, because that handler *reads* as the compliant sibling: the obvious remediation is "make the others look like this one", and the fix ships the hole. So diff the guard's **arguments** across its call sites — the odd one out is the finding — and confirm the object it authorizes is the object it acts on. **Then check whether it is deliberate**: both shapes are also what an intentional model change looks like mid-migration. `git log --follow` the file and read the guard's test. A maintainer who rewrote that test to assert the behaviour you are about to report has already told you it is the design, and the "odd one out" is a designed matrix rather than an outlier.

## Fixing what you find

A finding without a fix is half a review — but an unvalidated fix is worse than none, so run step 6 before you recommend anything, and step 7 before you send it. Every fix below was wrong in at least one real audit *until* an independent pass caught it. Fix shapes by class:

| Class | Fix shape | What the naive fix breaks |
|---|---|---|
| **Guarantee asserted, weakly implemented** | Move the control out of the prompt/parse layer into something *enforceable*: a type contract, a query predicate, a privilege, a sandbox. Fail **closed** — on parse failure emit an explicit `undetermined`, never a plausible default. | "Just return the safe default" usually *is* the bug — it silently disables the control. And swapping in a lenient parser removes the exception the old fallback depended on; add an explicit type guard so a non-conforming result still fails closed. |
| **Wrong lifetime or frequency** | Bound it: `max_size` **and** active eviction — a TTL checked only on read frees nothing. Pop the lock/aux dict alongside the entry it guards. Or build per request. | Per-request construction can regress cost and latency — establish what the singleton was actually buying before deleting it. |
| **Authorization assumed, never enforced** | `owner` **OR** the specific privileged case — never an unconditional owner filter. Bind identity into the tool factory's closure; re-root client-supplied scope keys under the authenticated one. | The system/admin paths that legitimately bypass the check (an agent persisting its own messages; an owner revoking a member's share); filtering on the wrong key (name vs id); a cache or second route that never reaches the layer you fixed. |

Prefer the codebase's **existing** primitive over a new one — reusing the guard it already ships is the difference between a patch a maintainer merges and one they rewrite. And when the permissive behaviour turns out to be load-bearing, say so in the report rather than shipping a fix that breaks their product.

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
