# Package Manifest

Package: `SingularityX_public_homepage_bilingual_v1.0.0_first_public_version`

| Item | Content |
|---|---|
| Package version | V1.0.0 (First Public Version) |
| Release date | 2026-05-20 |
| Rule interpretation body | SingularityX |
| Chinese rule interpretation body | 零界演化 |


## Included

```text
assets/singularityx-logo.png
README.md
README.zh-CN.md
VALUE-DISTRIBUTION-PROTOCOL.md
VALUE-DISTRIBUTION-PROTOCOL.zh-CN.md
challenge-board/README.md
challenge-board/README.zh-CN.md
challenge-board/TASK_FILE_SHA256.txt
challenge-board/tasks/SX-CH-001-causal-chain-uncertainty.md
challenge-board/tasks/SX-CH-002-market-data-consistency.md
challenge-board/tasks/SX-CH-003-paper-strategy-runtime-contract.md
challenge-board/tasks/SX-CH-004-public-alpha-selection.md
docs/difficulty-and-amounts.md
docs/difficulty-and-amounts.zh-CN.md
docs/challenge-source-integrity.md
docs/legal-notice-and-compliance.md
docs/legal-notice-and-compliance.zh-CN.md
docs/user-agreement-challenge-rules-and-legal-statement.zh-CN.md
docs/value-assessment-system.md
docs/value-assessment-system.zh-CN.md
.github/ISSUE_TEMPLATE/challenge-inquiry.yml
.github/PULL_REQUEST_TEMPLATE.md
CONTRIBUTING.md
.gitignore
```

## Main changes in this package

1. Marks the package as V1.0.0 (First Public Version) / V1.0.0（第一版）.
2. Keeps version information and the rule-interpretation body fields in the bilingual homepage, challenge board, challenge pages, difficulty documents, contribution guide, important legal statement documents, and package manifest.
3. Removes standalone explanatory paragraphs from version information and rule-interpretation blocks, while retaining the formal rule-interpretation body where applicable.
4. Updates the important legal statement documents to cover platform bounty task boundaries, user responsibility, third-party rights, submitted-solution rights, and agreement to platform rules.
5. Keeps the previously removed redundant homepage consolidation paragraph out of both Chinese and English homepage files.
6. Preserves exactly four independent challenge pages under `challenge-board/tasks/` and preserves their task periods, deliverable standards, recognition standards, and revised bounty tiers.
7. Keeps private email submission as the default channel; public Pull Requests remain optional only when the contributor intentionally wants public disclosure.
8. Updates task-page SHA256 records after removing the standalone version-block remarks.

## Challenge set

| ID | Difficulty | CNY bounty cap | Task period | Task page |
|---|---:|---:|---:|---|
| SX-CH-001 | Advanced | Up to RMB 7,200 | 21 calendar days | `challenge-board/tasks/SX-CH-001-causal-chain-uncertainty.md` |
| SX-CH-002 | Hard | Up to RMB 9,000 | 21 calendar days | `challenge-board/tasks/SX-CH-002-market-data-consistency.md` |
| SX-CH-003 | Hard | Up to RMB 9,600 | 21 calendar days | `challenge-board/tasks/SX-CH-003-paper-strategy-runtime-contract.md` |
| SX-CH-004 | Flagship | Up to RMB 12,000 | 28 calendar days | `challenge-board/tasks/SX-CH-004-public-alpha-selection.md` |

## Submission channel

Unless a challenge statement specifies a dedicated submission address, challenge submissions should be sent privately to:

```text
join@singularityx.tech
```

Email subject format:

```text
[Challenge Submission] <Challenge ID> - <Contributor Name or GitHub Username>
```
