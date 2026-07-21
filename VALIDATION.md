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
| 14 | *withheld* | ~15k | L4 | — | — | Under coordinated disclosure | 🔒 held — no private channel available |
| 15 | *withheld* | ~22k | L3 | — | — | Under coordinated disclosure | 🔒 privately disclosed |
| 16 | *withheld* | ~6k | L4 | — | — | Under coordinated disclosure | 🔒 held — no private channel available |
| 17 | [headroom](https://github.com/headroomlabs-ai/headroom) | 61k | L3 | library-use / inverted adapter | current | 🔴 The LangGraph compression node **inflates** context instead of shrinking it: `ToolMessage(...)` is rebuilt without `id=msg.id`, and the node returns a bare `{"messages": [...]}` — under `add_messages` an id-less message is *appended*, not replaced, so the documented wiring doubles history. 🔴 A second: `wrap_tools_with_headroom` returns tools no agent can invoke. | non-security — publicly filable |
| 18 | *withheld* | ~27k | L4 | — | — | Under coordinated disclosure | 🔒 privately disclosed |
| 19 | *withheld* | ~26k | L1–L2 | — | — | Under coordinated disclosure | 🔒 pack ready |
| 20 | *withheld* | ~55k | L4 | — | — | Under coordinated disclosure — incl. a published advisory that **appears unfixed** | 🔒 pack ready |
| 21 | *withheld* | ~12k | L4 | — | — | Under coordinated disclosure | 🔒 pack ready |
| 22 | [LibreChat](https://github.com/danny-avila/LibreChat) | 41k | L3 | SDK-host / graph-native | modern | ❌ **Lead finding refuted.** A file-ownership guard that reads as a tautology — called with the same object as subject and baseline — turned out to be a deliberate model change the maintainer authored two weeks earlier, *inside the audited tree*, rewriting the test to assert exactly that behaviour. Agent ACL, not file ownership, is now the gate. 🟡 One survivor, Low: a shared MCP server config is writable behind a VIEW-only gate. | **refuted + Low → PR, not advisory** |

Repo names for rows 14–22 are withheld along with the findings, and star counts are rounded. Listing a
popular product beside "unfixed vulnerability" is itself a pointer for an attacker and helps no defender
while the fix does not exist. Names are filled in as each advisory publishes.

---

## Summary

| Metric | Result |
|---|---|
| Repos reviewed | **22** (20 LangChain + 1 excluded at the shape gate + 1 out of scope) |
| Security findings under coordinated disclosure | **9 repos** |
| Lead findings **refuted** by adversarial review | **1** |
| Filed or disclosed upstream | 1 public issue + PR · 4 private security disclosures · 5 packs ready |
| Already reported by others | 2 |
| Rejected as unmaintained / dead | 1 audited + 3 screened out before audit |
| Clean / control cases | 2, plus 1 correct **N/A** on authorization |

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

**The one contrast the data does support:** fixes we executed were correct (2 of 2); fixes we only argued
about were rewritten (9 of 9). Execution, not the rubric and not the reviewer, is what separated them.

Treat every number on this page as provisional until an external verdict exists.

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
- **Test whether step 7 changes outcomes or only confidence.** It has caught something in every audit so
  far, which is either strong evidence or a sign the bar for "caught something" is too low. The honest
  test is a finding that survives an adversarial pass entirely unchanged — that has still not happened.
  What *has* now happened is a full refutation (repo 22), which is the stronger evidence: the pass is
  capable of returning "there is no finding here", not only "here are corrections".
- Screening is cheap and worth stating: three candidate repos (35k★, 39k★, 36k★) were dropped before any
  audit — two with no merged PR in over a year, one archived. Liveness first.
