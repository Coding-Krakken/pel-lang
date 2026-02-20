# Security Policy

## Supported Versions
- Only the latest stable release is actively supported for security updates.

## Reporting a Vulnerability
- Please report security issues to [security@pel-lang.org](mailto:security@pel-lang.org).
- Do **not** open public issues for security vulnerabilities.
- Provide as much detail as possible (steps to reproduce, impact, affected files).
- We will acknowledge receipt within 2 business days and coordinate a fix.

## Security Best Practices
- Never commit secrets, credentials, or sensitive data.
- Use static analysis tools (`bandit`, `safety`) before submitting code.
- Validate all user input and handle errors securely.
- Review dependencies for known vulnerabilities (`pip install safety && safety check`).

## Static Analysis Tools
- Run `bandit -r .` to scan for common Python security issues.
- Run `safety check` to check for vulnerable dependencies.
- Integrate these tools into your CI pipeline (see CONTRIBUTING.md for details).

## Disclosure Policy
- We follow responsible disclosure and will credit reporters if desired.
- Fixes will be released as soon as possible and announced in release notes.

---

For urgent issues, contact the project lead directly at [security@pel-lang.org](mailto:security@pel-lang.org).
