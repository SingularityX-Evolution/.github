# Merge Notes

| Item | Content |
|---|---|
| Package version | V2.0.0 (Second Version) |
| Release date | 2026-06-12 |
| Rule interpretation body | SingularityX / 零界演化 |

This package merges the SingularityX organization homepage with the open research challenge homepage into a single external-facing GitHub homepage package.

## This revision

- Marks this package as V2.0.0 (Second Version) / V2.0.0（第二版）.
- Keeps version information and rule-interpretation body fields in the homepage, challenge board, challenge pages, difficulty documents, contribution guide, package manifest, and important legal statement documents.
- Updates the important legal statement documents to cover platform bounty task boundaries, user responsibility, third-party rights, submitted-solution rights, non-certified submission use limits, and agreement to platform rules.
- Removes the redundant homepage consolidation paragraph from `README.md` and `README.zh-CN.md`.
- Preserves the SingularityX logo path and company introduction.
- Keeps two homepage versions: `README.md` for English and `README.zh-CN.md` for Chinese.
- Clarifies the two participation routes: public challenge bounty submission and formal organization membership.
- Keeps exactly four independent public challenge pages under `challenge-board/tasks/`.
- Uses direct GitHub-rendered Markdown challenge entry points.
- Public problem pages show background, core problem, public task scope, grade closure rules, deliverable standards, recognition standards, S / A bounty tiers, grade status rules, version information, and rule-interpretation body.
- Keeps challenge submission private by email by default; public Pull Requests remain optional only for contributors who intentionally want public disclosure.
- Records updated task-page hashes in `challenge-board/TASK_FILE_SHA256.txt` and `docs/challenge-source-integrity.md`.
- Adds S / A grade status tables and concurrent-submission closure handling.
- Defines five-calendar-day response types and limits certified-work display to desensitized summaries or reviewed public materials.
- Clarifies that non-certified, non-adopted, non-settled submissions are not directly used for production, commercialization, relicensing, or public release except for necessary review, audit, dispute, and compliance purposes.

## Challenge set and bounty caps

| ID | Difficulty | CNY bounty cap | Grade closure rule | Task page |
|---|---:|---:|---:|---|
| SX-CH-001 | Advanced | Up to RMB 7,000 | No fixed time limit; S / A grades close independently once certified | `challenge-board/tasks/SX-CH-001-causal-chain-uncertainty.md` |
| SX-CH-002 | Hard | Up to RMB 8,800 | No fixed time limit; S / A grades close independently once certified | `challenge-board/tasks/SX-CH-002-market-data-consistency.md` |
| SX-CH-003 | Hard | Up to RMB 9,500 | No fixed time limit; S / A grades close independently once certified | `challenge-board/tasks/SX-CH-003-paper-strategy-runtime-contract.md` |
| SX-CH-004 | Flagship | Up to RMB 12,000 | No fixed time limit; S / A grades close independently once certified | `challenge-board/tasks/SX-CH-004-public-alpha-selection.md` |

## Submission email

```text
join@singularityx.tech
```

Recommended subject:

```text
[Challenge Submission] <Challenge ID> - <Contributor Name or GitHub Username>
```
