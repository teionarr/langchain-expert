<div align="center">

<img src="assets/langchain-expert-banner.gif" alt="langchain-expert banner" width="100%"/>

# langchain-expert

**A code-review skill for LangChain & LangGraph — 23 practices, validated against real production repos.**

[![License: MIT](https://img.shields.io/badge/License-MIT-black.svg)](LICENSE)
[![Practices](https://img.shields.io/badge/practices-23-blue)](SKILL.md)
[![Repos audited](https://img.shields.io/badge/repos%20audited-22-brightgreen)](VALIDATION.md)
[![Findings filed](https://img.shields.io/badge/findings%20filed-10-orange)](VALIDATION.md)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-purple.svg)](CONTRIBUTING.md)

*Find the defects that matter. Skip the noise. Never manufacture a finding.*

</div>

---

Most LangChain review advice is a style guide — import order, naming, "use the latest API." That's not
where production agents break.

This skill is organised around where defects **actually** cluster in real codebases, which — across a
22-repo audit of everything from a 152k-star platform to 1k-star agent templates — is almost never the
architecture:

| Failure class | What it looks like in the wild |
|:--|:--|
| 🎭 **Guarantee asserted, weakly implemented** | `or True` quietly killing an error classifier · a parse failure defaulting to a confident verdict · "read-only" enforced by `startswith` |
| ⏱️ **Correct logic, wrong lifetime or frequency** | a cache with no eviction · a DB commit per LLM call · a shared singleton mutated per request |
| 🔓 **Authorization assumed, never enforced** | a handler — or an **agent tool** — that fetches a resource by id with no owner check |

That third class produced **every** high-severity finding across the audit, and most review checklists
miss it entirely. Once it was written down as a practice, **5 of the next 6** audits produced one — and
the sixth was an honest N/A. → [VALIDATION.md](VALIDATION.md)

## Quick start

**With an agent harness (Claude Code, etc.)** — drop this folder into your skills directory and invoke
it by name, or simply point an agent at `SKILL.md`:

```
Review this repo with langchain-expert.
```

**By hand** — `SKILL.md` is a self-contained checklist. Work the procedure top to bottom.

## How the review works

```mermaid
flowchart LR
    A[Detect shape] --> B[Detect era]
    B --> C[Verify APIs<br/>before asserting]
    C --> D[Walk the<br/>23 practices]
    D --> E[Qualify each<br/>candidate]
    E --> G[Validate<br/>the fix]
    G --> H[Red-team in a<br/>fresh context]
    H --> F[Report<br/>≤7 findings]
    style A fill:#1f6feb,color:#fff
    style E fill:#8957e5,color:#fff
    style H fill:#da3633,color:#fff
    style F fill:#238636,color:#fff
```

The **procedure** matters as much as the practices:

- **Detect shape first.** A graph-native app is not a `create_agent` app — demanding middleware imports
  where they don't belong is the top source of false positives.
- **Verify before asserting.** A confidently wrong correction is worse than no review. Principles are
  stable; kwargs are not.
- **Qualify before investing.** Is it reachable on a *default* path — a real default value and a live
  call path, not dead code behind an off-by-default flag? This one check kills more inflated severity
  than anything else in the rubric.
- **Never recommend a fix you haven't traced.** Nine consecutive audits produced a wrong one; two would
  have caused an outage.
- **Red-team in a fresh context before you send it.** Independence is the mechanism — re-reading your own
  finding defends it. Expect the bug to survive and the report to change.
- **Never manufacture findings.** *"Two findings and a long N/A list"* is a valid review.

## What's inside

```
SKILL.md                            the skill — procedure + 23 practices (start here)
VALIDATION.md                       the golden set: every repo audited, findings, lessons
references/notes.md                 rationale, evidence, verified API signatures
references/gold-standard-agent.py   a reference agent to copy the shape from
```

## Validation

This skill is **tested against real code, and the misses are recorded too.**

| | |
|:--|:--|
| Repos audited | **22** |
| High-severity findings | **every one** authorization-class |
| Repos under coordinated disclosure | **9** |
| Filed / disclosed upstream | 1 public issue + PR · 4 private advisories · 5 packs ready |
| Already reported by others | 2 |
| Clean control cases | 2, plus 1 correct **N/A** |
| Reports corrected by an adversarial pass | **9 of 9** |

Every change to the rubric is traceable to the specific audit that exposed the gap. Full breakdown,
including LangChain-depth ratings per repo → [VALIDATION.md](VALIDATION.md)

> `VALIDATION.md` follows a strict disclosure policy: security findings are named only once already
> public. **It will never be the first public mention of an unfixed vulnerability.**

## Contributing

The most valuable contribution is **an audit** — run the skill on a LangChain repo and add the result
to the golden set, including the false leads. Second most valuable: **an audit that disproves a
practice.** A rubric that can't be wrong isn't measuring anything.

See [CONTRIBUTING.md](CONTRIBUTING.md) · [SECURITY.md](SECURITY.md) · [Code of Conduct](CODE_OF_CONDUCT.md)

## Provenance

Builds on Anthropic's `expert-langchain` skill, extended with a third failure class
(authorization), a severity-qualification step, and the validation harness in
[VALIDATION.md](VALIDATION.md).

## License

[MIT](LICENSE)
