# Permission-to-Defend

Deployment link: https://permission-to-defend.vercel.app/

![alt text](https://github.com/Hiithaard47/Permission-to-Defend/blob/main/Permission%20to%20Defend.png "Application Screenshot")

Permission-to-Defend is an AI-powered privacy auditing tool for Android applications. It compares an application's requested permissions against its privacy policy to determine whether those permissions are properly disclosed and justified.

The project is built around a simple idea: if an application requests access to sensitive data, its privacy policy should clearly explain why that access is required. Whenever those two don't align, it creates what this project refers to as a Privacy-Permission Mismatch.

Instead of manually reading lengthy privacy policies and comparing them against an application's permissions, users can run an automated audit that highlights inconsistencies, vague disclosures, and potentially unjustified permission requests.

### Motivation

Android applications commonly request permissions such as Camera, Microphone, Contacts, Location, and Storage. While many of these permissions are necessary for an application's functionality, developers are expected to clearly disclose why they are required and how the collected data will be used.

In reality, privacy policies are often long, difficult to read, and filled with legal language. Verifying whether every requested permission is adequately explained quickly becomes a tedious manual task.

Permission-to-Defend automates this process by using a Large Language Model to reason over both the application's privacy policy and its declared permissions, producing an audit that is easier to understand and review.

### Features
- Analyze application privacy policies using Google's Gemini models.
- Extract permissions directly from a Google Play Store URL (Apple App Store support coming soon!).
- Upload an `AndroidManifest.xml` file to parse permissions manually.
- Perform a semantic audit between requested permissions and privacy policy disclosures.
- Identify Privacy-Permission Mismatches.
- Present audit findings as individual visual cards.
- Chat with the AI after the audit to better understand the findings.
- Restrict the chatbot to answer only questions related to the generated audit.


### How It Works

#### 1. Provide the Privacy Policy

Copy and paste the application's privacy policy from the developer's website or any other official source.

#### 2. Provide the Permissions

Permissions can be supplied in either of two ways:

Paste the Google Play Store URL and let the application scrape the declared permissions.
Upload the application's `AndroidManifest.xml` file (if available) to extract permissions directly.

#### 3. Run the Audit

Once both inputs are provided, clicking Run Audit starts the analysis.

The application sends the privacy policy together with the extracted permissions to the Gemini API. Rather than performing simple keyword matching, the model semantically analyzes whether each requested permission is adequately disclosed and justified within the privacy policy.

For every permission, the audit determines whether:

- The permission is clearly disclosed.
- The intended purpose is explained.
- The disclosure is vague or incomplete.
- The permission appears to have no supporting justification.

The results are presented as individual visual cards, making it easy to identify Privacy-Permission Mismatches at a glance.

#### 4. Explore the Findings

Once the audit is complete, the chatbot becomes available.

The chatbot has access to the generated audit and allows users to ask follow-up questions about:

- Individual permissions
- Privacy policy statements
- Audit findings
- Potential privacy concerns

The chatbot operates under strict guardrails and only answers questions related to the uploaded privacy policy, extracted permissions, and generated audit. It does not respond to unrelated or general-purpose prompts.

### Project Workflow

```
Privacy Policy
       │
       ▼
Paste Policy Text
       │
       ▼
Provide Permissions
 ├── Google Play Store URL
 └── AndroidManifest.xml
       │
       ▼
Extract Permissions
       │
       ▼
Gemini Privacy Audit
       │
       ▼
Audit Report
       │
       ▼
Context-Aware Chatbot
```
