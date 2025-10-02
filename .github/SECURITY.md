# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Currently supported versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to the repository owner. You can find the contact information in the GitHub profile.

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

Please include the requested information listed below (as much as you can provide) to help us better understand the nature and scope of the possible issue:

- Type of issue (e.g. buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit the issue

This information will help us triage your report more quickly.

## Preferred Languages

We prefer all communications to be in English.

## Policy

We follow the principle of responsible disclosure:

1. Report the vulnerability privately
2. Give us reasonable time to fix the issue
3. Don't exploit the vulnerability or disclose it publicly until fixed
4. We will acknowledge receipt of your report
5. We will work with you to understand and fix the issue
6. We will credit you in the security advisory (unless you prefer to remain anonymous)

## API Credentials Security

**IMPORTANT**: Never commit API credentials (appKey, appSecret) to the repository.

- Use environment variables or `.env` files (git-ignored)
- Use Home Assistant's configuration UI for credentials
- Never log full credentials in code
- Always mask sensitive data in logs (show only first 8 characters)

If you accidentally commit credentials:

1. Immediately revoke them in your SolarGuardian account
2. Generate new credentials
3. Remove from git history using `git filter-branch` or BFG Repo-Cleaner
4. Force push the cleaned history (if safe to do so)

## Dependencies

We use Dependabot to keep dependencies up to date and secure. Security updates for dependencies are applied promptly.

## Code Scanning

We use GitHub's CodeQL analysis to automatically detect security vulnerabilities in the codebase.
