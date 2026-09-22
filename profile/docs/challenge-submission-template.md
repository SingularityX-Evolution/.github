# Challenge Code Submission Template

[中文版本](challenge-submission-template.zh-CN.md) | [Homepage](../README.md) | [Challenge board](../challenge-board/README.md)

For both the initial code submission and every upgraded submission, the email body must include all three of the following personal details:

| Required field | Requirement |
|---|---|
| Name | The contributor's real name; a nickname or GitHub username alone is insufficient. |
| Contact details | At least one valid, regularly checked contact method, such as an email address, phone number, or WeChat ID. Identify the contact type and ensure you can be reached promptly. |
| Personal GitHub profile URL | The full, accessible URL of the contributor's own personal GitHub profile, in the form `https://github.com/<username>`. A username alone, repository URL, organization profile, or another person's profile is insufficient. |

All three fields are mandatory. Missing information, invalid contact details, or a non-compliant profile URL makes the submission incomplete; formal review will not begin until the information is complete. Queue order follows the existing rule based on receipt of complete materials. Supplying these identity and contact details is a non-substantive supplement and must not be used to add or replace submitted code, experimental results, or other substantive review materials.

## Email template

To: `join@singularityx.tech`

Subject: `[Challenge Submission] <Challenge ID> - <Name>`

Copy the body below and replace every placeholder. Provide the code package or repository URL separately from the personal profile URL.

```text
Challenge ID: <e.g. SX-CH-003; first confirm the challenge and requested grade remain open>
Submission type: <initial submission / authorized Grade S upgrade>

Name (required): <your real name>
Contact details (required): <email / phone / WeChat: actual details; at least one>
Personal GitHub profile URL (required): https://github.com/<your-username>

Code package attachment / accessible repository URL: <filename or repository URL>
Submitted version: <commit hash or package SHA256>
Running instructions and reproduction commands: <details or attachment location>
Test results / evaluation report: <details or attachment location>
Dependencies, data sources, and authorization: <details or attachment location>
Known limitations: <list limitations, or state none>
Rights statement: I own or have the necessary rights to submit the code, data, and other materials.
Public PR URL (only when using a public PR): <PR URL>
```

Technical deliverables are governed by the selected challenge. See the [contribution guide](../CONTRIBUTING.md) for the complete workflow.

## When using a public PR

Public PR submissions must also provide the name, valid contact details, and personal GitHub profile URL privately by email to the address above. Include the challenge ID and PR URL in that email so the details can be matched to the code. Keep private contact details such as phone numbers and WeChat IDs out of public PRs, Issues, and code files. General public inquiries do not require these personal details.

These details support contributor verification, review communication, and attribution. Providing them does not authorize public disclosure of the name or contact details, or public display linking the GitHub profile to the submission. Information is handled under the [Privacy Policy](privacy-policy.md).
