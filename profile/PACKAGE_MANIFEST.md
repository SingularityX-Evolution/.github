# Package Manifest

Package: `SingularityX_public_homepage_bilingual_v2.1.0_second_version_s_a_only`

| Item | Content |
|---|---|
| Package version | V2.1.0 (Second Version) |
| Release date | 2026-06-22 |
| Rule interpretation body | SingularityX |
| Chinese rule interpretation body | 零界演化 |


## Included

```text
assets/singularityx-logo.png
README.md
README.zh-CN.md
MERGE_NOTES.md
VALUE-DISTRIBUTION-PROTOCOL.md
VALUE-DISTRIBUTION-PROTOCOL.zh-CN.md
challenge-board/README.md
challenge-board/README.zh-CN.md
challenge-board/STATUS.md
challenge-board/STATUS.zh-CN.md
challenge-board/TASK_FILE_SHA256.txt
challenge-board/tasks/SX-CH-001-causal-chain-uncertainty.md
challenge-board/tasks/SX-CH-002-market-data-consistency.md
challenge-board/tasks/SX-CH-003-paper-strategy-runtime-contract.md
challenge-board/tasks/SX-CH-004-public-alpha-selection.md
challenge-board/results/SX-CH-001-phase-1-results.md
challenge-board/results/SX-CH-001-phase-1-results.zh-CN.md
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

1. Marks the package as V2.1.0 (Second Version) / V2.1.0（第二版）.
2. Keeps version information and the rule-interpretation body fields in the bilingual homepage, challenge board, challenge pages, difficulty documents, contribution guide, important legal statement documents, and package manifest.
3. Removes standalone explanatory paragraphs from version information and rule-interpretation blocks, while retaining the formal rule-interpretation body where applicable.
4. Updates the important legal statement documents to cover platform bounty task boundaries, user responsibility, third-party rights, submitted-solution rights, non-certified submission use limits, and agreement to platform rules.
5. Keeps the previously removed redundant homepage consolidation paragraph out of both Chinese and English homepage files.
6. Preserves exactly four independent challenge pages under `challenge-board/tasks/` and updates their grade closure rules, deliverable standards, recognition standards, and S / A bounty tiers.
7. Keeps private email submission as the default channel; public Pull Requests remain optional only when the contributor intentionally wants public disclosure.
8. Updates task-page SHA256 records after current rule-text changes.
9. Adds the no-fixed-time-limit, per-grade closure, five-business-day response, and one-week desensitized public-display rules to challenge pages, challenge-board submission guidance, homepage submission guidance, and the public challenge inquiry template.
10. Adds S / A grade status tables marking each remaining grade as open or closed.
11. Clarifies concurrent-submission queueing and grade-closure handling.
12. Establishes one initial submission opportunity per contributor per challenge. A Grade A certification unlocks one Grade S-only upgraded submission within five calendar days (120 hours) after the confirmation email is sent, for a maximum of two submissions; a successful upgrade is settled at Grade S with any paid Grade A bounty credited, while an unsuccessful upgrade preserves the original Grade A certification without duplicate payment. The upgrade opportunity does not reopen a closed Grade S.
13. Defines response types within the five-business-day response window.
14. Limits successful-certification display to desensitized summaries and reviewed public materials.
15. Aligns task rules and intellectual-property statements so that non-certified, non-adopted, non-settled submissions are not directly used for production, commercialization, relicensing, or public release except for necessary review, audit, dispute, and compliance purposes.
16. Presents the Phase 1 review results as a public-facing announcement with anonymized award records and brief solution summaries for the two recognized SX-CH-001 results: 1 Grade B recognition and 1 Grade C recognition.
17. Records that the one-week public display of contributor code materials and authorized GitHub profiles ended on June 22, 2026; those materials, links, and directories are excluded from the current package.
18. Clarifies the SX-CH-001 calibration and uncertainty-quantification rules: real-chain outcomes must be generated independently after model predictions, confidence intervals must represent genuine epistemic uncertainty, and hop-order or cross-method prediction resampling does not satisfy grade-certification requirements.

## Challenge set

| ID | Difficulty | CNY bounty cap | Grade closure rule | Task page |
|---|---:|---:|---:|---|
| SX-CH-001 | Advanced | Up to RMB 7,000 | No fixed time limit; S / A grades close independently once certified | `challenge-board/tasks/SX-CH-001-causal-chain-uncertainty.md` |
| SX-CH-002 | Hard | Up to RMB 8,800 | No fixed time limit; S / A grades close independently once certified | `challenge-board/tasks/SX-CH-002-market-data-consistency.md` |
| SX-CH-003 | Hard | Up to RMB 9,500 | No fixed time limit; S / A grades close independently once certified | `challenge-board/tasks/SX-CH-003-paper-strategy-runtime-contract.md` |
| SX-CH-004 | Flagship | Up to RMB 12,000 | No fixed time limit; S / A grades close independently once certified | `challenge-board/tasks/SX-CH-004-public-alpha-selection.md` |

## Submission channel

Unless a challenge statement specifies a dedicated submission address, challenge submissions should be sent privately to:

```text
join@singularityx.tech
```

Email subject format:

```text
[Challenge Submission] <Challenge ID> - <Contributor Name or GitHub Username>
```
