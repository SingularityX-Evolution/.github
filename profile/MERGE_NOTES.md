# Merge Notes

| Item | Content |
|---|---|
| Package version | V1.0.0 (First Public Version) |
| Release date | 2026-05-20 |
| Rule interpretation body | SingularityX / 零界演化 |

This package merges the SingularityX organization homepage with the open research challenge homepage into a single external-facing GitHub homepage package.

## This revision

- Marks this package as V1.0.0 (First Public Version) / V1.0.0（第一版）.
- Keeps version information and rule-interpretation body fields in the homepage, challenge board, challenge pages, difficulty documents, contribution guide, package manifest, and important legal statement documents.
- Updates the important legal statement documents to cover platform bounty task boundaries, user responsibility, third-party rights, submitted-solution rights, and agreement to platform rules.
- Removes the redundant homepage consolidation paragraph from `README.md` and `README.zh-CN.md`.
- Preserves the SingularityX logo path and company introduction.
- Keeps two homepage versions: `README.md` for English and `README.zh-CN.md` for Chinese.
- Clarifies the two participation routes: public challenge bounty submission and formal organization membership.
- Keeps exactly four independent public challenge pages under `challenge-board/tasks/`.
- Replaces downloadable Word/TXT challenge entry points with direct GitHub-rendered Markdown problem pages.
- Public problem pages show background, core problem, public task scope, task period, deliverable standards, recognition standards, bounty tiers, version information, and rule-interpretation body.
- Keeps challenge submission private by email by default; public Pull Requests remain optional only for contributors who intentionally want public disclosure.
- Records updated task-page hashes in `challenge-board/TASK_FILE_SHA256.txt` and `docs/challenge-source-integrity.md`.

## Challenge set and bounty caps

| ID | Difficulty | CNY bounty cap | Task period | Task page |
|---|---:|---:|---:|---|
| SX-CH-001 | Advanced | Up to RMB 7,200 | 21 calendar days | `challenge-board/tasks/SX-CH-001-causal-chain-uncertainty.md` |
| SX-CH-002 | Hard | Up to RMB 9,000 | 21 calendar days | `challenge-board/tasks/SX-CH-002-market-data-consistency.md` |
| SX-CH-003 | Hard | Up to RMB 9,600 | 21 calendar days | `challenge-board/tasks/SX-CH-003-paper-strategy-runtime-contract.md` |
| SX-CH-004 | Flagship | Up to RMB 12,000 | 28 calendar days | `challenge-board/tasks/SX-CH-004-public-alpha-selection.md` |

## Submission email

```text
join@singularityx.tech
```

Recommended subject:

```text
[Challenge Submission] <Challenge ID> - <Contributor Name or GitHub Username>
```
