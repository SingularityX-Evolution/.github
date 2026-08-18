# Fair Value Distribution: Public Protocol

**Rule interpretation body:** SingularityX

This protocol explains how assessed long-term contributions enter a distribution boundary, form a confirmed value pool, receive reference allocations, and proceed through review and appeal. Public challenge bounties are separately administered under the applicable challenge statement and review rules and do not share the member long-term contribution pool.

This is a public governance framework, not a promise of a fixed bonus, profit share, equity, option, Token, or cash amount. All economic arrangements remain subject to formal agreements, applicable law, tax requirements, and organizational approval.

## 1. Define the distribution boundary first

Before a settlement period begins, the applicable agreement should define:

- the settlement period, covered projects, and outcome-confirmation window;
- the value eligible for distribution and how it will be confirmed;
- eligible participants, contribution records, and shared assets;
- distribution purposes, caps, deferral, review, and correction rules;
- exclusions, duplicate-counting rules, and conflict treatment;
- the rule version, approval process, and appeal window.

Rules should not be changed after the outcome simply to produce a preferred distribution.

## 2. Confirmed value pool

The distributable total should be constrained by actual outcomes, risk adjustment, evidence confidence, the applicable agreement, and compliance requirements. A value pool enters pre-settlement only after its source and scope are clear and the required review is complete.

Core principles include:

- do not distribute value that remains unconfirmed or lacks a traceable source;
- do not use short-term outcomes without considering tail risk, execution cost, model risk, and compliance risk;
- do not exceed the formal agreement, budget arrangement, or another applicable cap;
- do not force uncertain value into distribution merely to make the percentages complete;
- do not create overlapping pools for the same underlying outcome.

Specific calculation settings and caps are governed by the applicable agreement and controlled rule versions. They do not create a standing public ratio or amount.

## 3. Distribution purposes

To avoid rewarding only the last visible contributor, an applicable agreement may divide the value pool by purpose:

| Distribution purpose | Primary objective |
|---|---|
| Baseline participation | Recognizes eligible participation and basic responsibility under the agreement. |
| Collective contribution | Recognizes team collaboration, shared infrastructure, validation, risk control, and outcomes that cannot be fully decomposed. |
| Marginal contribution | Recognizes a verifiable increase in the overall result caused by a person, component, or working group. |
| Long-term reuse | Recognizes work that others independently adopt, maintain, and retain as organizational capability. |

Applicable ratios should be established in advance and versioned when rules change. Any public example is illustrative only and is not a fixed distribution promise.

## 4. Basic eligibility

Before a contribution enters formal distribution, it should normally satisfy:

1. A traceable contribution record exists and is linked to the necessary evidence.
2. Participants, dependencies, and actual adoption can be confirmed.
3. Material facts are verified and material claims have independent review.
4. No unresolved duplicate, conflict, or permission issue remains.
5. The outcome has reached the required verification or maturity state.
6. Appeal, compliance, and settlement procedures permit recognition.

Self-report, title, hours, lines of code, submission count, or personal influence cannot establish eligibility by itself.

## 5. Fair-attribution principles

### 5.1 Consider several forms of contribution

Distribution does not depend on one score. It considers:

- direct delivery and its quality;
- marginal impact compared with the outcome without the contribution;
- necessity under a reasonable alternative;
- reduction of risk, uncertainty, or decision error;
- durable impact through independent reuse by other members or projects;
- support for validation, shared assets, and team collaboration.

### 5.2 Recognize shared outcomes

Data, research, engineering, validation, execution, risk control, documentation, and human judgment may jointly produce an outcome. The last code submitter, deployer, named author, or direct producer of a visible gain does not automatically own the entire value.

### 5.3 Check collaboration stability

In multi-person work, average marginal contribution and working-group checks may support fairness review and identify whether an essential team or shared asset has been overlooked. These methods must disclose their limits and uncertainty and cannot replace human review automatically.

## 6. Conservation and deduplication

Every distribution should satisfy:

- confirmed allocations, deferred portions, and unallocated portions do not exceed the confirmed value pool;
- the same outcome is not counted again as direct delivery, long-term reuse, a shared asset, or a human adjustment;
- person shares, collective shares, and distribution purposes remain consistent;
- rounding residuals, caps, and reasons for non-allocation are recorded;
- human adjustments trigger a fresh consistency and conservation check.

Value that cannot yet be attributed reliably may remain unallocated until additional evidence is available rather than being forced onto existing participants.

## 7. Uncertainty and maturity

Contribution value may mature over time through actual adoption, reuse, maintenance, and later outcomes. A portion that remains immature, weakly evidenced, or disputed may be deferred and reviewed again when new evidence appears.

Later maturity and correction records should be appended without overwriting the original history. Any deferral, release, or adjustment should state its basis and follow the applicable agreement.

## 8. Risk, error, and responsibility

Records of adverse impact should remain visible, but an algorithmic output alone cannot create an automatic personal debit or disciplinary decision. Formal treatment should distinguish good-faith error, capability gaps, repeated error, rule bypass, and intentional concealment while also examining system design, access, process, training, and management responsibility.

Good-faith, evidence-based dissent should remain protected even when ultimately incorrect. A material avoided-loss claim likewise requires prudent estimation and independent review and should not be booked at the worst-case amount automatically.

## 9. Fairness review

Each settlement period should consider:

- whether the distribution is excessively concentrated;
- whether essential teams and shared assets are appropriately recognized;
- whether low-confidence or immature value was confirmed too early;
- whether adverse impacts, deferred portions, and non-allocation reasons are clear;
- whether appeals and human adjustments changed the original attribution logic;
- whether totals, evidence, and rule versions remain consistent.

An apparent anomaly should lead to human review. Fairness review identifies questions that require explanation; it does not impose automatic equal distribution.

## 10. Human adjustments

A material human adjustment must:

- record the before and after outcomes, reason, evidence, and applicable rule;
- record the proposer, approver, time, and conflict treatment;
- remain within the confirmed value pool and formal agreement;
- rerun conservation and fairness checks;
- provide an understandable explanation to affected contributors during the appeal window.

An adjustment without evidence, a record, or an applicable rule cannot enter final settlement.

## 11. Settlement and appeal process

    Confirm distribution boundary
    → Check contribution eligibility and evidence
    → Confirm value pool
    → Perform multi-factor attribution
    → Review conservation and fairness
    → Issue pre-settlement report
    → Open appeal window
    → Conduct independent review and human adjustment
    → Obtain final approval
    → Issue Reward Proof

Settlement may be deferred where evidence is insufficient, the value-pool scope is unclear, duplicate counting remains, rule versions are inconsistent, an appeal is open, a conflict remains, or a material compliance issue is unresolved.

## 12. Reward Proof

A Reward Proof should state:

    reward_proof_id
    settlement_period
    contribution_record_id
    evidence_summary_hash
    rule_version
    confirmed_value_pool
    allocation_policy_hash
    allocation_result
    deferred_or_unallocated_amount
    manual_adjustment_record
    review_status
    appeal_status
    correction_record
    timestamp

A Reward Proof shows which rules and boundaries supported the result. It does not itself create a payment, security, or equity right.

## 13. Relationship to public challenges

Public challenge bounties follow the applicable statement, acceptance, and settlement rules and do not share the member long-term contribution pool. If a challenge result is later formally adopted, reused, or maintained, only the new long-term contribution under a new formal agreement may enter member value assessment. The original bounty and the same underlying value cannot be counted twice.
