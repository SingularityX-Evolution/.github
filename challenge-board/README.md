# SingularityX Challenge Board

## Version Information

| Item | Content |
|---|---|
| Rule version | V2.1.0 (Second Version) |
| Release date | 2026-06-22 |
| Rule interpretation body | SingularityX |


This board lists the current public bounty challenges. Each challenge is independent. Challenges are ordered by CNY bounty cap from low to high, and challenge IDs follow the same ascending bounty order. Clicking “Open” leads directly to a GitHub-rendered Markdown problem page.

Public problem pages present background, core problem, public task scope, grade recognition and closure rules, deliverable standards, recognition standards, and S / A bounty tiers.

For competitive bounty challenges, private email submission is recommended by default. Public Pull Requests are appropriate only when the contributor intentionally chooses to disclose code, reports, and implementation details publicly.

## Phase 1 Review Results Announcement

The Phase 1 review for `SX-CH-001` is complete. Following technical review and reproducibility checks, two submissions received recognition: one at Grade B and one at Grade C. We thank all participants for their work on uncertainty quantification for multi-hop causal chains.

| Challenge ID | Stage status | Public recognition results | Announcement |
|---|---|---|---|
| SX-CH-001 | Phase 1 review completed; challenge remains open | 1 Grade B, RMB 2,700; 1 Grade C, RMB 900 | [View results announcement](./results/SX-CH-001-phase-1-results.md) |

The announcement publishes anonymous recognition results, bounty amounts, and anonymized solution summaries. The authorized GitHub profiles and code materials completed their one-week public display on June 22, 2026, and are no longer publicly accessible.


## Current public challenges

| ID | Challenge | Chinese title | Difficulty | CNY bounty cap | Grade closure rule | Challenge content |
|---|---|---|---:|---:|---|---|
| SX-CH-001 | Multi-Hop Causal Chain Uncertainty Quantification | 自建因果链多跳推理的不确定性无法量化 | Advanced | RMB 7,000 | No fixed time limit; S / A grades close independently once certified | [Open](./tasks/SX-CH-001-causal-chain-uncertainty.md) |
| SX-CH-002 | Tardis Historical Data and Binance Real-Time Data Consistency | 提升 Tardis 历史数据与 Binance 实时采集数据在四个永续合约上的一致性，并定位剩余行情与因子差异原因 | Hard | RMB 8,800 | No fixed time limit; S / A grades close independently once certified | [Open](./tasks/SX-CH-002-market-data-consistency.md) |
| SX-CH-003 | Paper Strategy Runtime Contract for Real Backtesting | 从交易论文到真实回测的统一策略运行契约 | Hard | RMB 9,500 | No fixed time limit; S / A grades close independently once certified | [Open](./tasks/SX-CH-003-paper-strategy-runtime-contract.md) |
| SX-CH-004 | Robust High-Sharpe Alpha Mining from a Public Classic Strategy Pool | 公开经典策略池的稳健高夏普 Alpha 挖掘与样本外验证 | Flagship | RMB 12,000 | No fixed time limit; S / A grades close independently once certified | [Open](./tasks/SX-CH-004-public-alpha-selection.md) |

## S / A grade status

The current release status is shown below; later changes should be checked against this section and the latest [`STATUS.md`](./STATUS.md) notice.

| ID | S grade | A grade | Status note |
|---|---:|---:|---|
| SX-CH-001 | Open | Open | S and A grades close independently |
| SX-CH-002 | Open | Open | S and A grades close independently |
| SX-CH-003 | Open | Open | S and A grades close independently |
| SX-CH-004 | Open | Open | S and A grades close independently |

Each contributor has one initial submission opportunity per challenge. Only if that submission is certified at Grade A may the contributor submit one complete upgraded version, solely to seek Grade S certification, within five calendar days (120 hours) from the time the Grade A certification confirmation email is sent. The maximum is two submissions per contributor per challenge, and failure to submit within the window waives the upgrade opportunity. If the upgraded submission meets Grade S, final certification and settlement are at Grade S; if the Grade A bounty has already been paid, only the difference is paid, and the contributor may not collect both grade bounties. If it does not meet Grade S, the original Grade A certification remains effective and no duplicate Grade A bounty is awarded. Each submission is queued by the timestamp at which its complete materials reach the official email address or approved upload channel. After a grade is certified and announced closed by SingularityX, new recognition applications for that grade will no longer be accepted. The Grade A-to-S upgrade opportunity does not reopen a closed Grade S and may be used only if Grade S remains open when the upgraded submission is received. Submissions received before the closure announcement will still receive a response; however, SingularityX does not guarantee that the grade still has an available bounty slot or will continue into bounty review for that grade.

## Difficulty and bounty note

Difficulty levels and CNY bounty caps are assigned at the complete-challenge level. They are not subtask prices, milestone payments, or guaranteed payouts. Actual bounty recognition depends on submitted artifacts, reproducibility results, review conclusions, contribution evidence, applicable agreements, compliance requirements, and the bounty review process.

## Submission channel

Private submissions should be sent to:

```text
join@singularityx.tech
```

Recommended subject:

```text
[Challenge Submission] <Challenge ID> - <Contributor Name or GitHub Username>
```

A valid submission should include reproducible code or a structured delivery package, README and running instructions, test results or an evaluation report, dependency and environment information, known limitations, and a contributor statement confirming that the contributor owns or has the right to submit the work.

Both the initial submission and any Grade A-to-S upgraded submission are independent versions and may not be changed after receipt. The upgraded submission must be delivered as a new complete version and is counted separately. SingularityX will provide a response within five business days after submission or upload. The response may include confirmation that the work has entered review, a request for non-substantive supplementary materials, initial-screen rejection, continued reproduction review, certification at a particular grade, or no grade certification.

After a grade certification succeeds, SingularityX will publicly display only a desensitized work summary, certification grade, challenge ID, and reviewed public materials for one week, without disclosing sensitive information, private code, account information, non-public strategy details, restricted data, or core confidential implementation details.

[← Back to homepage](../README.md)