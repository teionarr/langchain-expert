# expert-langchain

A code-review skill for **LangChain / LangGraph** Python applications — 23 practices distilled from the
LangChain codebase and from auditing real production repos, plus a procedure for applying them without
manufacturing findings.

It's built for two jobs:

- **Reviewing** existing LangChain code — find the defects that matter, skip the noise
- **Writing** new agent code that's expert-grade from the first draft

## Why this exists

Most LangChain review advice is a style guide. This isn't. The practices are organised around where
defects *actually* cluster in real codebases — which, empirically, is almost never the architecture:

| Failure class | Looks like |
|---|---|
| **Guarantee asserted, weakly implemented** | `or True` killing an error classifier; a parse failure defaulting to a confident verdict |
| **Correct logic, wrong lifetime or frequency** | a cache with no eviction; a DB commit per LLM call; a shared singleton mutated per request |
| **Authorization assumed, never enforced** | a handler — or an agent tool — that fetches a resource by id with no owner check |

That third class produced **both** high-severity findings in a 13-repo audit, and it's the one most
review checklists miss entirely. See [VALIDATION.md](VALIDATION.md).

## Contents

```
SKILL.md                          the skill — procedure + 23 practices (read this first)
references/notes.md               rationale, evidence, and verified API signatures
references/gold-standard-agent.py a reference agent to copy the shape from
VALIDATION.md                     the golden set: every repo audited, what was found, what it taught us
```

## Using it

**With Claude Code / an agent harness:** drop the folder into your skills directory and invoke it by
name, or just point an agent at `SKILL.md` and ask it to review a diff or a repo.

**By hand:** `SKILL.md` is a self-contained checklist. Work the procedure top to bottom —
detect shape → detect era → verify APIs before asserting → walk the practices → **qualify each
candidate** → report ≤7 findings.

The procedure matters as much as the practices:

- **Verify before asserting.** A confidently wrong correction is worse than no review. Principles are
  stable; kwargs are not.
- **Qualify before investing.** Is it reachable on a default path? Already reported? Is the repo even
  maintained? Three cheap checks that prevent most wasted effort and most over-called severity.
- **Never manufacture findings.** "Two findings and a long N/A list" is a valid review.

## Validation

The skill has been run against real open-source LangChain projects — from a 152k-star platform down to
1k-star agent templates — and the results, *including the misses and the false leads*, are recorded in
[VALIDATION.md](VALIDATION.md). Findings have been filed upstream, and every change to the rubric is
traceable to the specific audit that exposed the gap.

`VALIDATION.md` follows a strict disclosure policy: security findings are named only once they are
already public. It will never be the first public mention of an unfixed vulnerability.

## Status

Work in progress. The golden set is being extended toward 20 repos, and practice 23 (authorization) is
new enough that earlier audits predate it and are being revisited.

Contributions welcome — especially audits that *disprove* a practice. A rubric that can't be wrong
isn't measuring anything.

## License

MIT — see [LICENSE](LICENSE).
