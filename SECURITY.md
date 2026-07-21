# Security Policy

This repository contains a **code-review skill** — documentation and a reference file. It has no runtime
and no network surface, so vulnerabilities *in this repo* are unlikely. The policy that matters here is
about **findings produced by using the skill**.

## If you find a vulnerability in another project using this skill

Follow coordinated disclosure. In short:

1. **Don't open a public issue** — not here, not there. A public issue is the fastest way to hand an
   unpatched bug to an attacker.
2. **Report privately to that project**: their `SECURITY.md` contact, or GitHub's private
   *"Report a vulnerability"* advisory if enabled.
3. **Give them time to fix it.** Follow their stated timeline; ~90 days is the common industry default.
4. **Go public only after the fix ships** (or the agreed deadline passes).
5. **Never test against systems you don't own or aren't authorised to test.** Local clones only.

## Adding such a finding to the golden set

`VALIDATION.md` will **never be the first public mention of an unfixed vulnerability.**

Submit the row with the finding **withheld** — keep the repo's audit metadata, omit the finding itself.
Fill it in once the fix and advisory are published; a linked advisory is stronger evidence than a claim
anyway.

Note that redaction has to be real: star count, product category, vulnerability class and disclosure
date **combine** to identify a project. If someone could find the affected repo in ten minutes from what
you wrote, it isn't redacted — drop the identifying fields entirely.

## Reporting an issue with this repository

For anything about the skill itself, open a normal issue.
