# Contributing

| Item | Content |
|---|---|
| Rule version | V2.1.0 (Second Version) |
| Release date | 2026-06-22 |
| Rule interpretation body | SingularityX |


Thanks for contributing to SingularityX Open Research Challenges.

## Submission requirements

Follow the selected challenge file. Depending on the challenge, a complete submission may require:

```text
runnable code
Python prototype
research calibration method or prototype
channel-level diagnostic framework
reproduction command or verification steps
data source description
reports, metrics, logs, or generated positions
known limitations
rights-to-submit statement
open-source license and third-party dependency statement
security and data-source statement
```

## Standard flow

For competitive bounty challenges, private submission is the default:

```text
pick challenge -> implement -> prepare evidence package -> submit by official email or approved private channel -> review -> bounty review result
```

Public Pull Requests are optional and should be used only when the contributor intentionally wants the submitted code, report, and implementation details to be public.

## Default private submission

Unless the challenge statement specifies another approved private channel, submit challenge work by email:

```text
join@singularityx.tech
```

Recommended subject:

```text
[Challenge Submission] <Challenge ID> - <Contributor Name or GitHub Username>
```

Each contributor has one initial submission opportunity per challenge. Only if that submission is certified at Grade A may the contributor submit one complete upgraded version, solely to seek Grade S certification, within five calendar days (120 hours) from the time the Grade A certification confirmation email is sent. The maximum is two submissions per contributor per challenge, and failure to submit within the window waives the upgrade opportunity. Both versions are independent and immutable after receipt. If the upgraded version meets Grade S, final certification and settlement are at Grade S; any paid Grade A bounty is credited and only the difference is paid. If it does not meet Grade S, the original Grade A certification remains effective and no duplicate Grade A bounty is awarded.

SingularityX will provide a response within five business days after submission or upload. The response may include confirmation that the work has entered review, a request for non-substantive supplementary materials, initial-screen rejection, continued reproduction review, certification at a particular grade, or no grade certification.

Each submission is placed in the review queue according to the timestamp at which its complete materials reach the official email address or approved upload channel. After a grade is certified and announced closed by SingularityX, new recognition applications for that grade will no longer be accepted. The Grade A-to-S upgrade opportunity does not reopen a closed Grade S and may be used only if Grade S remains open when the upgraded submission is received. Submissions received before the closure announcement will still receive a response; however, SingularityX does not guarantee that the grade still has an available bounty slot or will continue into bounty review for that grade.

After a grade certification succeeds, SingularityX will publicly display only a desensitized work summary, certification grade, challenge ID, and reviewed public materials for one week, without disclosing sensitive information, private code, account information, non-public strategy details, restricted data, or core confidential implementation details.

## Evidence bundle

Each submission should make review possible:

```text
challenge ID
contributor name and GitHub username
contact email
code package or private repository link
commit hash or package SHA256 hash
README and reproduction instructions
input data source and license or authorization note
output files
logs or report
metrics
failure cases and known limitations
rights-to-submit statement
open-source license and third-party dependency statement
security and data-source statement
```

## Optional public PR

A public PR may be used when the contributor chooses public disclosure. Public PR submissions should include reproduction commands, data-source notes, outputs, reports, known limitations, and the linked challenge ID.

Do not include any sensitive, private, confidential, customer, account, credential, paid-data, third-party-restricted, or non-public strategy material in a public PR.

## Important Legal Statement check

Before submitting, read `docs/legal-notice-and-compliance.md` and `docs/legal-notice-and-compliance.zh-CN.md`.

Do not submit credentials, private keys, cookies, private account records, private trading logs, private market data, paid datasets, customer information, personal information, private positions, private risk rules, non-public strategy material, private profit logic, confidential business information, code you are not licensed to submit, or materials that the contributor does not have the right to submit.

Public challenges and examples are for lawful research, education, engineering experiments, reproducible evaluation, risk-control validation, and system design only. They are not investment advice, financial-product marketing, asset management, securities or futures services, virtual-asset services, or return promises.
