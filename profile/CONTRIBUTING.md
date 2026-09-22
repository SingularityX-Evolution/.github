# Contributing

**Rule interpretation body:** SingularityX

Thanks for contributing to SingularityX Open Research Challenges.

## Submission requirements

**Mandatory contributor details:** The email body for both initial and upgraded submissions must include your real name, at least one valid contact method (a regularly checked email address, phone number, or WeChat ID), and the full URL of your own personal GitHub profile (`https://github.com/<username>`). A username alone, repository URL, organization profile, or another person's profile is insufficient. Missing information, invalid contact details, or a non-compliant profile URL makes the submission incomplete; formal review will not begin until the information is complete.

Use the [English submission email template](docs/challenge-submission-template.md) or [中文提交邮件模板](docs/challenge-submission-template.zh-CN.md). The personal profile URL and submitted-code repository URL are separate fields; both initial and upgraded submissions must include the three personal details.

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
[Challenge Submission] <Challenge ID> - <Name>
```

Each contributor has one initial submission opportunity per challenge. Only if that submission is certified at Grade A may the contributor submit one complete upgraded version, solely to seek Grade S certification, within five calendar days (120 hours) from the time the Grade A certification confirmation email is sent. The maximum is two submissions per contributor per challenge, and failure to submit within the window waives the upgrade opportunity. Both versions are independent and immutable after receipt. If the upgraded version meets Grade S, final certification and settlement are at Grade S; any paid Grade A bounty is credited and only the difference is paid. If it does not meet Grade S, the original Grade A certification remains effective and no duplicate Grade A bounty is awarded.

SingularityX will provide a response within five business days after submission or upload. The response may include confirmation that the work has entered review, a request for non-substantive supplementary materials, initial-screen rejection, continued reproduction review, certification at a particular grade, or no grade certification.

Each submission is placed in the review queue according to the timestamp at which its complete materials, including all three mandatory contributor details, reach the official email address or approved upload channel. Supplying missing identity or contact details is a non-substantive supplement and must not be used to add or replace submitted code, experimental results, or other substantive review materials. After a grade is certified and announced closed by SingularityX, new recognition applications for that grade will no longer be accepted. The Grade A-to-S upgrade opportunity does not reopen a closed Grade S and may be used only if Grade S remains open when the upgraded submission is received. Submissions received before the closure announcement will still receive a response; however, SingularityX does not guarantee that the grade still has an available bounty slot or will continue into bounty review for that grade.

After a grade certification succeeds, SingularityX will publicly display only a desensitized work summary, certification grade, challenge ID, and reviewed public materials for one week, without disclosing sensitive information, private code, account information, non-public strategy details, restricted data, or core confidential implementation details.

## Evidence bundle

Each submission should make review possible:

```text
challenge ID
contributor real name (required, supplied privately)
valid contact details, including contact type (required, supplied privately)
own personal GitHub profile URL: https://github.com/<username> (required)
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

A public PR may be used when the contributor chooses public disclosure. Public PR submissions should include reproduction commands, data-source notes, outputs, reports, known limitations, and the linked challenge ID. The contributor must also privately email their real name, valid contact details, and personal GitHub profile URL to `join@singularityx.tech`, including the challenge ID and PR URL so the details can be matched to the code. Formal review will not begin until all three required details are complete. Keep private contact details out of the public PR and code files.

Do not include any sensitive, private, confidential, customer, account, credential, paid-data, third-party-restricted, or non-public strategy material in a public PR.

## Rules, privacy, and legal statement check

Before submitting, read the full [User Agreement, Challenge Rules, and Legal Statement](docs/user-agreement-challenge-rules-and-legal-statement.md), the [Privacy Policy](docs/privacy-policy.md), and the [Important Legal and Compliance Statement](docs/legal-notice-and-compliance.md). Chinese versions are available in the same `docs/` directory.

Do not submit credentials, private keys, cookies, private account records, private trading logs, private market data, paid datasets, customer information, unrelated or unauthorized personal information, private positions, private risk rules, non-public strategy material, private profit logic, confidential business information, code you are not licensed to submit, or materials that the contributor does not have the right to submit.

Public challenges and examples are for lawful research, education, engineering experiments, reproducible evaluation, risk-control validation, and system design only. They are not investment advice, financial-product marketing, asset management, securities or futures services, virtual-asset services, or return promises.
