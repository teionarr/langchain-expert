# Validation — the golden set

How the `expert-langchain` skill performs against real, popular open-source LangChain projects.
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
| 5 | *withheld* | — | — | — | — | 🔴 Under coordinated disclosure | 🔒 privately disclosed |
| 6 | *withheld* | — | — | — | — | 🔴 Under coordinated disclosure | 🔒 privately disclosed |
| 7 | [fastapi-langgraph-template](https://github.com/wassim249/fastapi-langgraph-agent-production-ready-template) | 2.5k | L4 | graph-native | modern | 🟠 Model-fallback mutates a process-global singleton and never resets it — one transient error permanently switches the model for every subsequent request | quality issue — unreported |
| 8 | [agent-service-toolkit](https://github.com/JoshuaC215/agent-service-toolkit) | 4.4k | L4 | graph-native | modern | Finding withheld pending disclosure | audited |
| 9 | [aegra](https://github.com/aegra/aegra) | 1.1k | L4 | graph-native server | modern | ✅ **Control case** — server-side authorization is consistently enforced across threads, runs, assistants and store (per-user scoping throughout) | clean |
| 10 | [company-research-agent](https://github.com/guy-hartstein/company-research-agent) | 2.1k | L4 | graph-native | modern | 🟠 Unbounded global in-process job store, never evicted — memory grows with every request for the life of the process | quality issue — unreported |
| 11 | [codeinterpreter-api](https://github.com/shroominic/codeinterpreter-api) | 3.8k | L2 | sessions + exec | legacy deps | Finding withheld — **repo abandoned** (no merged PR since 2023), so not reported | audited |
| 12 | [shell-ai](https://github.com/ricklamers/shell-ai) | 1.2k | L2 | CLI chain | modern | Finding withheld pending disclosure | audited |
| 13 | [RasaGPT](https://github.com/paulpierre/RasaGPT) | 2.5k | L2 | chains + webhook | mixed | Reference/demo project, documented by its authors as unauthenticated by design — excluded from findings | out of scope |

---

## Summary

| Metric | Result |
|---|---|
| Repos reviewed | **13** (12 LangChain + 1 excluded at the shape gate) |
| High-severity findings | **2** — *both* in the authorization class |
| Filed or disclosed | **3** (1 public issue + PR; 2 private security disclosures) |
| Already reported by others | 1 |
| Rejected as unmaintained | 1 |
| Clean / control cases | 2 |

**The headline result: both high-severity findings came from a failure class the rubric did not cover.**
That single fact drove the largest change to the skill.

---

## Lessons distilled → what changed in the skill

| # | Lesson | Skill change |
|---|---|---|
| 1 | Every high-severity finding across the audit was **broken access control**, and the rubric never pointed there. One was a LangChain-specific variant: a tool fetches a resource by an id taken from *model-controlled* arguments, with a docstring ("only use ids from context") standing in for an access control it cannot enforce. | **New practice 23** — authorize every resource fetch, for the *caller*; agent-tool IDOR named explicitly. Added as a third row to *"Where defects actually are."* |
| 2 | One excellent finding was **already reported with two stalled PRs**; another repo had been **abandoned since 2023**. Both audits were wasted effort that a two-minute check would have prevented. | **Procedure step 5** — check issues/PRs for novelty and last-merge activity *before* investing. |
| 3 | Severity was repeatedly over-called until defaults and call paths were checked: one finding sits behind an off-by-default flag; another repo's most alarming lead turned out to be **dead code** with no live writers. | **Procedure step 5** — trace to a default config value and a live call path before assigning severity. |
| 4 | One repo cost a full clone and investigation before revealing it wasn't a LangChain application at all. | **Shape gate** — "not a LangChain app" added to step 1, checked first. |

### Lessons that *confirmed* the rubric (no change needed)

- The two original failure classes predicted real bugs: *guarantee asserted, weakly implemented* → repos 3, 2, 8; *wrong lifetime or frequency* → repos 1, 7, 10.
- The graph-native guardrail ("never demand middleware imports here") prevented false positives on repos 3, 7, 9.
- Keeping negative results honest mattered. Repo 9 has genuinely solid authorization and repo 13's behaviour is by design — a rubric that cannot say "this is clean" is not measuring anything.

---

## Open work

- Extend the golden set to **20 repos**, running the *patched* skill to test whether the authorization
  lens raises the high-severity hit rate.
- Re-audit repos 1, 7, 8, 10, 12 with practice 23 applied — they were reviewed before the
  authorization lens existed.
- Fill in withheld entries as their fixes and advisories publish.
