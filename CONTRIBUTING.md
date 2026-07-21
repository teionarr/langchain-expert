# Contributing

Thanks for being here. This project improves in one specific way: **someone runs the skill on real code
and reports honestly what happened** — including when it found nothing, or found the wrong thing.

## The three contributions that matter most

### 1. 🔍 An audit (most valuable)

Run the skill against a LangChain/LangGraph repo and add a row to [VALIDATION.md](VALIDATION.md).

An audit is accepted when it includes:

- **Repo, stars, LangChain depth** (L0–L4 — see the scale in `VALIDATION.md`), **shape**, and **era**
- **What you found**, qualified against the four checks below
- **What you looked for and didn't find.** Negative results are kept — they're the control.
- **What it taught the rubric**, if anything. Often the answer is "nothing new," and that's a fine result.

Every finding must survive these before it counts:

| Check | Question |
|:--|:--|
| **Reachable?** | Does it trace to a *default* config value and a live call path? (Not dead code, not behind an off-by-default flag.) |
| **Already known?** | Searched the repo's issues *and* open PRs? |
| **Maintained?** | Is the repo still merging PRs? |
| **Real, not intended?** | Confirmed against sibling code, tests, and docs — ideally an adversarial second pass. |

> Roughly half the promising leads in the original audit died at these four checks. That's the point of
> them.

### 2. 🧨 An audit that disproves a practice

The most useful bug report here is *"practice N produced a false positive on this real codebase."*
Practices that survive contact with real code stay; the rest get merged, narrowed, or cut.

### 3. ✍️ A practice change

The bar is deliberately high. From `SKILL.md`:

> Practices may only be **added by replacing or merging** an existing one, unless the new one covers an
> untouched failure class. Keep `SKILL.md` under ~150 lines.

So a proposed practice needs **evidence from a real repo** — not a plausible-sounding rule. Point at the
code that would have been caught.

## Disclosure rules for audits ⚠️

This is non-negotiable, because the golden set contains security findings.

- **Never open a public issue or PR here that is the first public mention of an unfixed vulnerability.**
- If your audit finds a security issue, **disclose it privately to that project first** (their
  `SECURITY.md`, or GitHub's private "Report a vulnerability"), and submit the golden-set row with the
  finding **withheld** until their fix and advisory are published.
- Withheld rows keep the repo's audit metadata but omit the finding. See the rows marked *withheld* in
  `VALIDATION.md` for the format.
- Don't test against systems you don't own or aren't authorised to test. Local clones only.

See [SECURITY.md](SECURITY.md) for the full policy.

## Style

- Keep `SKILL.md` **under ~150 lines**. It's a working checklist, not documentation. Rationale, evidence
  and examples belong in `references/notes.md`.
- Write findings the way the skill reports them: `file:line → what's wrong → the corrected pattern`.
- Prefer being precise over being alarming. Calibrated severity is the whole product — an inflated 🔴
  costs more credibility than a missed 🟡.

## Submitting

Open a PR with your change, or an issue using one of the templates if you'd rather discuss first.
Small, evidence-backed PRs get merged fastest.
