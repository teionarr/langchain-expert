# Validation — the golden set

How the `langchain-expert` skill performs against real, popular open-source LangChain projects.
Each entry is a repo the skill was actually run against, with what it found and what it taught us.

## Disclosure policy

Findings are **named here only when they are already public** — either filed by us upstream, or
previously reported by someone else — **or when they are non-security quality issues**.

Security-relevant findings that have not yet been disclosed to their maintainers are **withheld**: the
repo is listed with its audit metadata, but the finding is not described.

> **This document will never be the first public mention of an unfixed vulnerability.**

Withheld entries are filled in once the corresponding fix and advisory are published.

---

## Method

> ### ⚠️ Sample bias — read before drawing conclusions from this table
> Every repo here is a **popular, actively maintained project built by strong engineers**. That makes it a
> good test of whether the skill finds *subtle* defects in *good* code — and a poor test of everything
> else. Most of the 23 practices never fired in this set, because this code already passes them. That is
> **not** evidence those practices are low-value: on a first LangChain agent, the ones about hand-rolled
> loops, `json.loads` on model prose, provider classes in business logic, and `assert` as a guard are
> exactly the ones that will fire. **Nothing here speaks to how the skill performs on beginner code.**
> Auditing low-star, early-stage repos is open work, and until it is done this table's silence on those
> practices should be read as "untested", not "unnecessary".

A repo enters the golden set only if it is **genuinely built on LangChain** and **actually reviewed** —
not skimmed. Every finding is qualified before it counts:

- **Reachable?** traced to a default config value and a live call path (not dead code, not behind an off-by-default flag)
- **Already known?** checked against existing issues *and* open PRs
- **Maintained?** checked last-merge activity
- **Real, not intended?** confirmed against sibling code, tests, and docs — often via an adversarial second pass

Negative results are kept. "This repo is clean" is a result, and a control against a rubric that
flatters itself.

### LangChain depth scale

| Level | Meaning |
|---|---|
| **L4 Core** | LangGraph / agent loop *is* the application backbone |
| **L3 Heavy** | LangChain components wrapped throughout the product |
| **L2 Applied** | LangChain for LLM wiring / retrievers / embeddings, with custom orchestration |
| **L1 Boundary** | Only `langchain_core` types at an adapter; LLM calls go through another SDK |
| **L0 None** | Not a LangChain app — out of scope |

---

## The golden set

| # | Project | ★ | Depth | Shape | Era | Finding | Status |
|---|---|---|---|---|---|---|---|
| 1 | [langflow](https://github.com/langflow-ai/langflow) | 152k | L3 | server + components | modern | 🟠 In-memory cache never actively frees memory: `max_size` unwired (LRU eviction is dead code), TTL expiry is lazy-only, no eviction when a flow is deleted | quality issue — unreported |
| 2 | [gpt-researcher](https://github.com/assafelovic/gpt-researcher) | 28.5k | L2 | library + hand-rolled + graph | modern | 🟠 Source curator parses LLM JSON with bare `json.loads` while the rest of the codebase uses `json_repair` → fenced model output silently falls back to uncurated sources | **filed: [issue #1953](https://github.com/assafelovic/gpt-researcher/issues/1953) · [PR #1954](https://github.com/assafelovic/gpt-researcher/pull/1954)** |
| 3 | [open_deep_research](https://github.com/langchain-ai/open_deep_research) | 12k | L4 | graph-native | modern | 🔴 `if is_token_limit_exceeded(e) or True:` — the `or True` makes the error classifier dead code, so any exception silently ends all research and is reported as normal completion | **already reported** by others ([#283](https://github.com/langchain-ai/open_deep_research/issues/283); PRs [#185](https://github.com/langchain-ai/open_deep_research/pull/185), [#286](https://github.com/langchain-ai/open_deep_research/pull/286) stalled) |
| 4 | [onyx](https://github.com/onyx-dot-app/onyx) | 31k | L1 | — | — | No finding — LLM layer is litellm; `langchain_core.messages` appears only at an adapter boundary | **excluded at the shape gate** |
| 5 | [pipeshub-ai](https://github.com/pipeshub-ai/pipeshub-ai) | 3.1k | L4 | agent + tools | modern | 🔴 Per-record ACL bypass in the `fetch_full_record` **agent tool** — the fallback path fetched a record by key with no per-user check, so any user could read documents outside their permission scope by getting the agent to call the tool with a record id (agent-tool IDOR, practice 23) | ✅✅ **CONFIRMED + FIXED by maintainer** — [PR #2743](https://github.com/pipeshub-ai/pipeshub-ai/pull/2743) merged 2026-07-22; fix independently re-reviewed as complete |
| 6 | *withheld* | — | — | — | — | 🔴 Under coordinated disclosure | 🔒 privately disclosed |
| 7 | [fastapi-langgraph-template](https://github.com/wassim249/fastapi-langgraph-agent-production-ready-template) | 2.5k | L4 | graph-native | modern | 🟠 Model-fallback mutates a process-global singleton and never resets it — one transient error permanently switches the model for every subsequent request | quality issue — unreported |
| 8 | [agent-service-toolkit](https://github.com/JoshuaC215/agent-service-toolkit) | 4.4k | L4 | graph-native | modern | Finding withheld pending disclosure | audited |
| 9 | [aegra](https://github.com/aegra/aegra) | 1.1k | L4 | graph-native server | modern | ✅ **Control case** — server-side authorization is consistently enforced across threads, runs, assistants and store (per-user scoping throughout) | clean |
| 10 | [company-research-agent](https://github.com/guy-hartstein/company-research-agent) | 2.1k | L4 | graph-native | modern | 🟠 Unbounded global in-process job store, never evicted — memory grows with every request for the life of the process | quality issue — unreported |
| 11 | [codeinterpreter-api](https://github.com/shroominic/codeinterpreter-api) | 3.8k | L2 | sessions + exec | legacy deps | Finding withheld — **repo abandoned** (no merged PR since 2023), so not reported | audited |
| 12 | [shell-ai](https://github.com/ricklamers/shell-ai) | 1.2k | L2 | CLI chain | modern | Finding withheld pending disclosure | audited |
| 13 | [RasaGPT](https://github.com/paulpierre/RasaGPT) | 2.5k | L2 | chains + webhook | mixed | Reference/demo project, documented by its authors as unauthenticated by design — excluded from findings | out of scope |
| 14 | *withheld* | ~15k | L4 | — | — | Under coordinated disclosure | 🔒 held — no private channel available |
| 15 | *withheld* | ~22k | L3 | — | — | Under coordinated disclosure | 🔒 privately disclosed |
| 16 | *withheld* | ~6k | L4 | — | — | Under coordinated disclosure | 🔒 held — no private channel available |
| 17 | [headroom](https://github.com/headroomlabs-ai/headroom) | 61k | L3 | library-use / inverted adapter | current | 🔴 The LangGraph compression node **inflates** context instead of shrinking it: `ToolMessage(...)` is rebuilt without `id=msg.id`, and the node returns a bare `{"messages": [...]}` — under `add_messages` an id-less message is *appended*, not replaced, so the documented wiring doubles history. 🔴 A second: `wrap_tools_with_headroom` returns tools no agent can invoke. | non-security — publicly filable |
| 18 | *withheld* | ~27k | L4 | — | — | Under coordinated disclosure | 🔒 privately disclosed |
| 19 | [kotaemon](https://github.com/Cinnamon/kotaemon) | 26k | L3 | RAG + ReAct/ReWOO agents | modern | 🟠 **Module-global mutable state — confirmed by adversarial red-team (told to refute).** MCP tool allow-list (`enabled_tools`) fails open after the first agent turn — a `.pop()` on the shared cached config voids it for every later turn; plus agent-tool singletons rebind per-user retrievers, leaking documents across concurrent sessions. Novel (no prior issue/advisory) | ✅ **submitted via GitHub advisory 2026-08-03** |
| 20 | [Flowise](https://github.com/FlowiseAI/Flowise) | 55k | L4 | visual agent builder | modern | 🔴 **Incomplete fix of CVE-2026-41279 / GHSA-5fw2 — validated with a live PoC.** `/api/v1/text-to-speech/generate` still whitelisted (unauth) and the `bodyCredentialId` branch unchanged on v3.1.4, so an unauthenticated caller still drives arbitrary stored credentials. Reproduced on the live 3.1.4 image: control routes 401, exploit 200 + `tts_start` | ✅ **submitted via GitHub advisory 2026-08-03** (regression report) |
| 21 | *withheld* | ~12k | L4 | — | — | Under coordinated disclosure | 🔒 pack ready |
| 22 | [LibreChat](https://github.com/danny-avila/LibreChat) | 41k | L3 | SDK-host / graph-native | modern | ❌ **Lead finding refuted.** A file-ownership guard that reads as a tautology — called with the same object as subject and baseline — turned out to be a deliberate model change the maintainer authored two weeks earlier, *inside the audited tree*, rewriting the test to assert exactly that behaviour. Agent ACL, not file ownership, is now the gate. 🟡 One survivor, Low: a shared MCP server config is writable behind a VIEW-only gate. | **refuted + Low → PR, not advisory** |
| 23 | [khoj](https://github.com/khoj-ai/khoj) | 36k | L2–L3 | agent + tools | modern | ✅ **Control — clean.** Full practice-23 pass (two independent sweeps agreed): no reachable per-user IDOR. Two historical IDORs (subscription, Notion OAuth) + a path-traversal all verified **fixed, no incomplete-fix delta**. Agent tools bind `user` from server context; no tool `args_schema` carries a user/tenant field — the correct "identity in closure" shape | clean |
| 24 | [deer-flow](https://github.com/bytedance/deer-flow) | 79k | L4 | graph-native + gateway | modern | ✅ **Control — clean.** Full practice-23 pass. Auth on by default (fail-closed middleware); per-user isolation via an always-active owner-check decorator + fail-closed contextvar repository filter. Prior cross-user IDOR (issue #3472) verified **fixed**; run-scoping unification already tracked → fails novelty. Agent tools resolve identity from runtime, never model args | clean |

| 25 | [rag-web-ui](https://github.com/rag-web-ui/rag-web-ui) | 3.1k | L2 | RAG web app | modern | Per-user IDOR-by-id surface **clean** (24 handlers, all owner-scoped; the one historical IDOR in this class already fixed). One security finding withheld pending disclosure: a missing-authorization / cross-user destructive endpoint (novel; `is_superuser` exists but unchecked) | 🔒 finding withheld — disclosure pending |
| 26 | [Aix-DB](https://github.com/apconw/Aix-DB) | 2.2k | L3 | text2sql multi-agent | modern | Multiple security findings, two Critical + one High **confirmed end-to-end by an adversarial red-team** (told to refute): unauthenticated read/write/delete of the row-permission subsystem; hardcoded default JWT signing key → forge any admin token; privesc via `/user/update` admin password reset. Core row-permission control is an LLM SQL-rewrite that **fails open** | 🔒 withheld — maintainer email channel identified, disclosure pending |

| 27 | [rag_api](https://github.com/danny-avila/rag_api) | 880 | L2 | RAG vector-store API | modern | 🟠 **Cross-tenant document-disclosure IDOR chain — confirmed by adversarial red-team.** `GET /ids` enumerates all tenants' file_ids → `GET /documents` + `GET /documents/{id}/context` read any tenant's document content, none filtering by user while the sibling `/query` does. Novel (issues #301/#303 cover other endpoints) | ✅ **submitted via GitHub advisory** |
| 28 | [restai](https://github.com/apocas/restai) | 510 | L3 | multi-tenant AIaaS | modern | 🟠 **Cross-project KG-entity merge IDOR — confirmed by adversarial red-team.** `kg_merge_entity` authorizes the path project then merges/deletes entities by id with no project scoping; the "authorizes A, acts on B" shape. Every sibling handler scopes correctly — lone outlier | ✅ **submitted via GitHub advisory** |

| 29 | [memanto](https://github.com/moorcheh-ai/memanto) | 1.8k | L1–L2 | memory server / LangGraph BaseStore | modern | ✅ **Control — clean.** Completeness-checked: 15 memory endpoints, 15 `enforce_session_scope` guards, 1:1. Token crypto-bound, no forgeable default; namespace scoping server-derived; UI loopback-gated on real TCP peer; legacy code unreachable | clean |

Repo names for rows 14–22 are withheld along with the findings, and star counts are rounded. Listing a
popular product beside "unfixed vulnerability" is itself a pointer for an attacker and helps no defender
while the fix does not exist. Names are filled in as each advisory publishes.

---

## Summary

| Metric | Result |
|---|---|
| Repos reviewed | **29** (27 LangChain + 1 excluded at the shape gate + 1 out of scope) |
| **External verdicts** | **1 confirmed + fixed** (pipeshub PR #2743) · 1 maintainer-engaged (MaxKB) |
| Security findings under coordinated disclosure | **13 repos** · 3 confirmed by adversarial red-team this round (Aix-DB, rag_api, restai); rag_api + restai have in-platform advisory channels |
| Lead findings **refuted** by adversarial review | **1** |
| Filed or disclosed upstream | 1 public issue + PR · **1 confirmed+fixed** (pipeshub) · **5 GitHub advisories submitted** (MaxKB, rag_api, restai, kotaemon, Flowise) · Flowise carries a live PoC (incomplete-fix of CVE-2026-41279) |
| Already reported by others | 2 |
| Rejected as unmaintained / dead | 1 audited + 3 screened out before audit |
| Clean / control cases | **5** (aegra, khoj, deer-flow, memanto + 1 correct **N/A**) — well-hardened repos where the lens correctly found nothing |

**The headline result: every high-severity finding, in both cohorts, came from the authorization class.**
Before practice 23 existed, the two that surfaced did so on a hunch. With it active, **5 of the next 6
audits** produced an authorization finding — and the sixth was an honest N/A (an in-process library with
no handlers and no caller identity), not a forced one.

> ⚠️ **Read that number carefully — it counts whether the lens *fired*, not whether it was right.** There
> is no false-positive denominator here: we record findings shipped, never candidates dropped. A lens
> firing in 5 of 6 repos is equally consistent with a real epidemic and with over-firing, and the same
> six audits are where our severity deflations cluster (8.1→6.5, 🟠→🟡, 🟠→4.8/5.4, three endpoints→one).
> The six are also the *numbered* entries only; three later audits with worse outcomes sit outside it.

**The second result is a caution about this whole page.** An independent adversarial pass has changed
something in every audit it reviewed — most often the proposed fix, in nine cases: a tautology, a cache
bypass, a destroyed admin capability, a name-vs-id mismatch, a broken disaster-recovery path, a shallow
copy that shared the state it meant to isolate, a prefix rule that would have 403'd every attachment
download, and a fail-closed change that would have taken down inference. Two would have caused an outage.

That is easy to read as "the review catches everything." It is not that. It measures a **gate catching
defects in drafts**, not a defect rate in shipped work — because nothing here has shipped. Across 22
repos: **zero merged fixes, zero published advisories, zero maintainer confirmations.** The one time an
oracle outside our own control was consulted (a maintainer's own merged commit, repo 22) it **refuted**
the finding and showed our fix was worse than the alleged bug.

Nor is the streak "consecutive": two fixes inside the same window — headroom's and one other — were
*executed* against the code and were correct.

**And a controlled re-run disqualified even that.** We re-verified three audits from the same raw inputs
against the same code, changing only the reviewer's framing — removing "expect it to confirm the bug" and
"default to refuted when uncertain". **All three produced materially different conclusions**: two findings
that had been dropped came back at CVSS 8.8 and 8.0; one that had been refuted came back as a real
low-severity issue; a "likely novel" finding turned out to be acknowledged in an existing advisory; and
one severity moved 2.4 points. The neutral reviewers also found evidence all previous passes had missed —
including a named regression commit that was the single strongest piece of evidence in one audit.

Pressure to reach a verdict produced *premature closure*, not rigour.

**So: no number on this page derived from an adversarial pass is a measurement.** Not the fix-defect
count, not the survival rate. What survives is a procedural claim, not a statistical one — an executed
fix is evidence; an argued one is an opinion.

**First external verdict (2026-07-22):** a maintainer confirmed and fixed one finding — pipeshub-ai's
`fetch_full_record` agent-tool ACL bypass, [PR #2743](https://github.com/pipeshub-ai/pipeshub-ai/pull/2743),
merged to main. One real bug, from the agent-tool authorization class, accepted and patched by the people
who own the code. That is the project's first ground-truth confirmation that the skill finds real bugs —
and it is exactly **one finding**. It does not validate the recall rate, the severity calls, or the other
21 practices; those remain provisional. Treat every *other* number on this page as provisional until its
own external verdict exists.

---

## Lessons distilled → what changed in the skill

| # | Lesson | Skill change |
|---|---|---|
| 1 | Every high-severity finding across the audit was **broken access control**, and the rubric never pointed there. One was a LangChain-specific variant: a tool fetches a resource by an id taken from *model-controlled* arguments, with a docstring ("only use ids from context") standing in for an access control it cannot enforce. | **New practice 23** — authorize every resource fetch, for the *caller*; agent-tool IDOR named explicitly. Added as a third row to *"Where defects actually are."* |
| 2 | One excellent finding was **already reported with two stalled PRs**; another repo had been **abandoned since 2023**. Both audits were wasted effort that a two-minute check would have prevented. | **Procedure step 5** — check issues/PRs for novelty and last-merge activity *before* investing. |
| 3 | Severity was repeatedly over-called until defaults and call paths were checked: one finding sits behind an off-by-default flag; another repo's most alarming lead turned out to be **dead code** with no live writers. | **Procedure step 5** — trace to a default config value and a live call path before assigning severity. |
| 4 | One repo cost a full clone and investigation before revealing it wasn't a LangChain application at all. | **Shape gate** — "not a LangChain app" added to step 1, checked first. |
| 5 | The finding survived scrutiny almost every time; the **report** did not. Nine consecutive audits produced a wrong fix, and two of those would have caused an outage. Severity, lead ordering, and one flatly false claim about a return type were also caught only by a second pass. | **Procedure step 7** — red-team in a *fresh context* before disclosing. Attack novelty, the load-bearing claim, the fix, and severity. Review the **set**, since only a cross-finding pass catches a mis-ranked lead. |
| 6 | Two audits independently found a guard that was **present, called, and passed the caller's identity — and still enforced nothing**: one handed the guard the same object as both subject and baseline; one authorized a session id and then acted on an unrelated caller-supplied object key. The asymmetry technique looks for a *missing* guard and sees neither. **The first of the two was then refuted** — the maintainer had authored that exact line two weeks earlier and rewritten its test to assert the behaviour. The *tell* fired correctly; the conclusion did not. | **Practice 23** — diff the guard's **arguments** across call sites, confirm the object it authorizes is the object it acts on, **and then check `git log` and the guard's test for intent**. The second shape is the more dangerous: that handler reads as the compliant sibling, so copying it *becomes* the fix. |
| 7 | The first **full refutation** of the series: a lead finding died because the maintainer had authored the "bug" himself, inside the audited tree, and inverted its test in the same commit. The novelty check had queried advisories and two PRs already in mind — but never the finding's own file, where that commit is the second entry. The proposed fix would also have made a revert button destroy data. | **Procedure step 7 (novelty)** — `git log --follow` the file *first*, before any tracker search. A commit that **created** the line you are calling a bug ends the finding, and it is the cheapest check available. |
| 8 | On a repo with 30 published advisories, two of three findings turned out to be **incomplete patches** of known CVEs rather than new bugs — and one *published* advisory was observably still unfixed. Framing them as new discoveries would have had all three closed as duplicates. | **Procedure step 7 (novelty)** — check published advisories, not just issues and PRs. An incomplete-fix report is legitimate and often stronger, but must be framed as the delta. |

### Lessons that *confirmed* the rubric (no change needed)

- The two original failure classes predicted real bugs: *guarantee asserted, weakly implemented* → repos 3, 2, 8; *wrong lifetime or frequency* → repos 1, 7, 10.
- The graph-native guardrail ("never demand middleware imports here") prevented false positives on repos 3, 7, 9.
- Keeping negative results honest mattered. Repo 9 has genuinely solid authorization and repo 13's behaviour is by design — a rubric that cannot say "this is clean" is not measuring anything.

---

## Open work

- ~~Extend the golden set to **20 repos**~~ — done, at 22. The authorization lens raised the hit rate from
  2/13 to 5/6 on the first cohort that used it.
- Re-audit repos 1, 7, 8, 10, 12 with practice 23 applied — they were reviewed before the
  authorization lens existed.
- Fill in withheld entries as their fixes and advisories publish.
- **Audit early-stage / low-star repos.** The entire golden set is expert-built code, so the basic
  practices are untested rather than unneeded. This is the largest gap in the validation.
- **Record candidates *dropped* per audit**, not only findings shipped — without a denominator no
  false-positive rate can ever be computed.
- **A known-CVE recall test came back NULL (Experiment 3).** 5 LangChain-component CVEs, with-skill vs
  control, both blind: both arms scored 5/5, delta 0. The base model finds these public bugs unaided, and
  the single-file bugs chosen need no skill. It measured nothing about recall — the skill still has zero
  external validation of bug-finding. A discriminating test needs bugs outside training data and hard
  enough that a plain reviewer misses them (the cross-file authz class, or seeded/undisclosed defects).
- **Test whether step 7 changes outcomes or only confidence.** It has caught something in every audit so
  far, which is either strong evidence or a sign the bar for "caught something" is too low. The honest
  test is a finding that survives an adversarial pass entirely unchanged — that has still not happened.
  What *has* now happened is a full refutation (repo 22), which is the stronger evidence: the pass is
  capable of returning "there is no finding here", not only "here are corrections".
- Screening is cheap and worth stating: three candidate repos (35k★, 39k★, 36k★) were dropped before any
  audit — two with no merged PR in over a year, one archived. Liveness first.
