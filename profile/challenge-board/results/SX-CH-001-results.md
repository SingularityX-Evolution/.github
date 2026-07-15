# SX-CH-001 Review Results Announcement

[← Back to challenge board](../README.md) ｜ [中文](./SX-CH-001-results.zh-CN.md) ｜ [Phase 1 results](./SX-CH-001-phase-1-results.md)

| Item | Details |
|---|---|
| First publication | June 15, 2026 |
| Latest update | July 2, 2026 |
| Challenge ID | SX-CH-001 |
| Challenge | Multi-Hop Causal Chain Uncertainty Quantification |
| Phase 1 | Review completed; one Grade B and one Grade C recognition |
| Phase 2 | Grade A certification and bounty payment completed |
| Current grade status | Grade S open; Grade A awarded and closed |

Thank you to everyone who participated in or followed the SingularityX public challenges. `SX-CH-001` has completed its Phase 1 review and the Phase 2 Grade A certification and bounty payment. Following technical review, code inspection, and reproducibility checks, this page publishes the recognized grades, bounty status, and anonymized solution summaries.

## Phase 1 review results

The Phase 1 review was completed on June 22, 2026. Several solutions were received, and two received recognition: one at Grade B and one at Grade C.

| Anonymous ID | Grade | Recognized bounty | Public solution summary |
|---|---:|---:|---|
| SX-CH-001-P1-B-001 | Grade B | RMB 2,700 | Examines confidence decay and error propagation in multi-hop causal chains, compares several non-naive aggregation approaches, combines confidence intervals, information gain, and hop limits into stopping conditions, and outlines calibration evaluation on synthetic data. |
| SX-CH-001-P1-C-001 | Grade C | RMB 900 | Presents a structured workflow from per-hop confidence to end-to-end confidence, covering multiple aggregators, external interruption factors, stopping conditions, calibration checks, and parameter-sensitivity analysis. |

The two recognized approaches address the central question from different angles: how uncertainty should propagate through multi-hop reasoning and when a chain should stop expanding. They offer useful directions for further research and engineering validation.

## Phase 2 review result

Following code review, data inspection, reproducibility runs, acceptance-criteria checks, and functional verification, one submission met the Grade A standard and received a bounty of **RMB 4,000**. The bounty was paid on July 2, 2026, and Grade A closed at the same time.

| Public record | Grade | Recognized bounty | Anonymized solution summary |
|---|---:|---:|---|
| SX-CH-001 Phase 2 recognized solution | Grade A | RMB 4,000 (paid) | Provides a substantially complete engineering structure and execution workflow. For multi-hop causal chains, it uses log-odds evidence accumulation, depth decay, and non-naive aggregation; outputs confidence estimates and intervals; and implements stopping rules, a calibration framework, and baseline comparisons. The solution meets the “substantially solved” standard but does not yet satisfy every Grade S requirement for historical sample size, calibration metrics, and complete validation evidence. |

As of this update, Grade S for `SX-CH-001` remains open and Grade A is closed. New Grade A recognition applications are no longer accepted. For current submission requirements, grade status, and recognition rules, refer to the [challenge page](../tasks/SX-CH-001-causal-chain-uncertainty.md) and the [status page](../STATUS.md).

## Public information note

- The Phase 1 section continues to show anonymous IDs, recognized grades, bounty amounts, and anonymized solution summaries without disclosing contributors' legal identities.
- The Phase 2 section publishes only the recognized grade, bounty status, and an anonymized technical summary. It does not disclose account information, private code, non-public strategy details, or restricted data.
- The authorized GitHub profiles and code materials completed their one-week public display. Related links, code directories, and download entry points are no longer provided.
- The summaries are intended only to help the public understand the technical direction. They do not replace the full technical materials or create additional performance or applicability commitments.
