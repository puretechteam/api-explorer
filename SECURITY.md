# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability within API Explorer, please report it
responsibly. We take the security of our project and its users seriously.

**Do not open a public issue for security vulnerabilities.**

Instead, please send a detailed report to the project maintainers:

- **Email:** [Insert maintainer email here]
- **GitHub:** [Open a private vulnerability report via GitHub Security Advisories](https://github.com/puretechteam/api-explorer/security/advisories/new)

### What to Include in Your Report

- A description of the vulnerability and its potential impact.
- Steps to reproduce the issue (proof of concept).
- The version(s) affected.
- Any potential mitigations you have identified.
- Your contact information (if you would like to be credited).

### What to Expect

- We will acknowledge your report within a reasonable timeframe.
- We will work with you to understand and validate the issue.
- We will develop a fix and coordinate a release timeline.
- We will credit you in our changelog (unless you wish to remain anonymous).

## Supported Versions

Security updates are applied to the latest release version. Users are encouraged
to keep their installations up to date.

## Security Best Practices

- Keep your API keys and secrets in `.env` files, never in source code.
- Do not commit `.env` files or other sensitive data to the repository.
- Review the `.gitignore` file to ensure sensitive files are excluded.
- Use the proxy endpoints responsibly and in accordance with the APIs' terms of service.