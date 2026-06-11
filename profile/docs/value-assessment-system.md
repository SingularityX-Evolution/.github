# Value Assessment Public Framework

| Item | Content |
|---|---|
| Rule version | V2.0.0 (Second Version) |
| Release date | 2026-06-12 |
| Rule interpretation body | SingularityX |


This document describes the public, code-free value assessment and distribution framework for SingularityX members. It explains how adopted long-term contributions may be recorded, verified, evaluated, attributed, settled, and disputed. Public challenge bounties are governed by the applicable challenge statement and bounty review rules.

This document describes the policy-level framework, algorithmic discipline, governance rules, appeal process, and public version framework. Detailed calculation settings, operational implementation, and case-level materials are handled through controlled review workflows, formal agreements, and applicable compliance requirements.

## 1. Methodology

Assessment is linear; value is nonlinear.

- Linear assessment supports comparison, ranking, explanation, budget conservation, and governance execution.
- Nonlinear value may come from collaboration, substitution effects, path dependency, timing, reuse, market state, and organizational network effects.
- Governance connects both layers by using linear assessment for order, nonlinear attribution for contribution approximation, and ledger constraints for reviewable allocation decisions.

## 2. Public layered framework

| Layer | Name | Role |
|---|---|---|
| L0 | Intake / Router | Routes tasks, review rights, and delivery paths according to capability, historical quality, workload, and permission status. |
| L1 | Protocol | Defines participation, deliverables, acceptance criteria, evidence requirements, pool rules, and appeal rules before work begins. |
| L2 | Contribution Record | Records tasks, code, research, documents, reviews, quality work, corrections, and reuse as auditable events. |
| L3 | Aggregation & Assessment | Converts heterogeneous evidence into interpretable scores, task points, quality tiers, and verification signals. |
| L4 | Rights Mapping | Maps assessment and attribution into bonus weights, resource priority, project opportunities, review eligibility, or other agreed incentives. |
| L5 | Settlement & Audit | Produces periodic settlement reports from assessment results, adopted outcomes, ledger facts, appeals, and applicable allocation rules. |

## 3. Dual-ledger structure

| Ledger | Frequency | Purpose | Properties |
|---|---|---|---|
| Operating Points Ledger | High frequency | Routing, resource priority, project opportunities, review eligibility, and collaboration management. | Fast, simple, interpretable; not equity, tokens, or fixed cash. |
| Economic Settlement Ledger | Low frequency | Additional contribution-based compensation, bonus review, long-term incentive review, or other formal arrangements. | Auditable; tied to adopted outcomes, verification confidence, reuse, governance records, and appeals. |

The operating ledger supports efficiency. The settlement ledger supports fairness.

## 4. Algorithmic discipline

### 4.1 Evidence gate

No evidence, no allocation. A contribution must first become an identifiable, traceable, and reviewable contribution asset.

Core objects include:

| Object | Description |
|---|---|
| Contribution Asset | A code, research, data, documentation, product, governance, review, or community contribution record. |
| Evidence Event | A task, submission, test result, review, correction, reuse record, or acceptance record linked to the asset. |
| Protocol | The role requirements, acceptance criteria, evidence requirements, pool rules, and appeal rules for the task. |
| Settlement Epoch | The agreed settlement period, such as a month, quarter, or project milestone. |
| Reward Proof | A traceable proof of contribution, assessment, rule version, and allocation result. |

Evidence with missing source, weak linkage, or poor reproducibility may be discounted or flagged. Self-attested evidence can be recorded but cannot receive full independent-evidence weight by itself. Contribution shares must satisfy range and conservation constraints. Material allocation decisions should be bound to rule versions, assessment versions, review records, and appeal status.

### 4.2 Linear assessment layer

The assessment layer compresses heterogeneous evidence into comparable, reproducible, and auditable scores. It does not claim to equal true value.

Public rule-level expression:

```text
reward_score
= difficulty_base
× impact_multiplier
× reuse_multiplier
× quality_multiplier
× protocol_compliance_multiplier
× verification_confidence
× risk_discipline_adjustment
```

This expression is used for operating points and governance input. It is not final cash, equity, tokens, or any fixed economic right.

### 4.3 Pool governance

Allocation is split by protocol so that the last visible submitter is not the only party rewarded.

| Pool | Purpose |
|---|---|
| Participant Pool | Direct delivery, research, engineering, testing, documentation, review, and maintenance. |
| Squad Pool | Long-term collaboration, retrospectives, and continued squad-level building. |
| Public Goods Pool | Shared modules, reusable tools, standards, runbooks, audit mechanisms, infrastructure, and shared knowledge assets. |
| Knowledge Asset Pool | Research notes, design documents, ADRs, reviews, retrospectives, tutorials, and related knowledge assets when applicable. |

Pool ratios are determined by task protocols, member agreements, organizational rules, and settlement epochs. Any example ratio is illustrative only and is not a standing commitment.

### 4.4 Nonlinear attribution

When multiple people, modules, or knowledge assets jointly create an outcome, the framework uses nonlinear attribution to handle marginal contribution and collaboration effects.

Publicly described logic:

1. Marginal-Contribution Anchor: average marginal contribution provides an initial fairness anchor and reduces bias toward title, submission order, or the final visible submitter.
2. Counterfactual Necessity: asks whether the result would materially deteriorate without the contribution; shallow, replaceable, or weakly necessary contributions should not receive full allocation.
3. Quality, Risk, and Compliance Adjustment: discounts or blocks contributions with weak reproducibility, poor maintainability, rule violations, or unresolved review issues.
4. Least-Core Stability Constraint: checks whether the allocation materially underpays important collaboration groups and reduces instability in the settlement result.
5. Hybrid Settlement: keeps the marginal-contribution anchor when stability gaps are low and projects toward a more stable allocation when gaps are high.

Public expression: marginal contribution anchors fairness; Least-Core constrains coalition stability; evidence, protocol, quality, risk discipline, counterfactual necessity, ledger facts, and human review determine final settlement discipline.

## 5. Settlement and appeal flow

Typical flow:

```text
contribution registration
→ evidence verification
→ protocol check
→ linear assessment
→ nonlinear attribution
→ quality / reuse / risk review
→ ledger verification
→ pre-settlement report
→ appeal window
→ human review
→ final settlement
→ Reward Proof
```

Settlement may be delayed, discounted, or blocked if evidence is missing, protocol requirements are incomplete, contribution shares do not satisfy conservation constraints, appeals remain unresolved, material compliance, permission, or governance issues remain open, audit chains or rule versions do not match, or reviewer conflicts are undisclosed.

## 6. Governance discipline

AI may assist with evidence summarization, preliminary scoring suggestions, inconsistency detection, and explanation drafts. Final allocation decisions, appeals, conflict arbitration, rule changes, permission approvals, and governance responsibility remain with humans.

Anti-manipulation is part of the rule system. Low-quality asset flooding, circular references, exaggerated attribution, undisclosed assumptions, unreproducible results, protocol bypassing, and undisclosed review conflicts may lead to discounting, delayed settlement, permission limits, or organizational review.

Human adjustment must be reviewable. Adjustments require recorded reasons, conservation checks, conflict-of-interest controls, version records, and an appeal window.

## 7. Reward Proof

Reward Proof helps contributors understand not only the allocation amount, but also why the allocation was calculated that way.

Illustrative public fields:

```text
reward_proof_id
contribution_asset_id
evaluation_round_id
rule_version
allocation_policy_hash
evidence_summary_hash
evaluation_report_hash
settlement_epoch
allocation_result
review_status
appeal_status
timestamp
```

Reward Proof is not a token, security, equity instrument, payment instrument, or fixed cash value. It is a proof record for the contribution assessment and distribution process.

## 8. Public version framework

| Layer | Public Positioning | Description |
|---|---|---|
| Public Homepage | Public GitHub entry point | Challenge board, organization membership, proof of contribution, value assessment framework, governance discipline, and compliance boundary. |
| Contribution Asset Layer | Contribution record layer | Converts code, research notes, design documents, reviews, runbooks, retrospectives, and community work into contribution assets. |
| Evidence & Assessment Layer | Evidence and scoring layer | Connects contribution assets with evidence events, task protocols, quality review, verification confidence, and operating points. |
| Attribution & Stability Layer | Fair allocation layer | Combines marginal-contribution anchoring, counterfactual necessity, pool governance, and Least-Core stability constraints. |
| Settlement & Appeal Layer | Review and settlement layer | Produces pre-settlement reports, handles appeals, applies human review, and records final settlement decisions. |
| Governance Hardening Layer | Rule quality layer | Adds rule-version tracking, policy checks, conflict-of-interest controls, audit records, and appealable Reward Proof. |