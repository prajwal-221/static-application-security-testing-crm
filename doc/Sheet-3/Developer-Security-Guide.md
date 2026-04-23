
---

# IDURAR CRM — Developer Security Guide

**Enterprise DevSecOps Secure Development Standard**

---

# 1. Purpose

This document explains:

* How to run security tools locally
* How to interpret findings
* When and how suppression is allowed
* What blocks a commit or pipeline
* Developer responsibilities in secure coding

This ensures security is enforced **before code reaches CI/CD**.

---

# 2. Security Tools Used in This Project

| Category                  | Tool                  | Purpose                            |
| ------------------------- | --------------------- | ---------------------------------- |
| Secrets Detection         | Gitleaks              | Detect hardcoded credentials       |
| SAST                      | Semgrep               | Detect insecure code patterns      |
| Dependency Scanning (SCA) | Trivy (fs)            | Detect vulnerable libraries        |
| Container Security        | Trivy (image/runtime) | Detect image CVEs                  |
| DAST                      | OWASP ZAP             | Detect runtime web vulnerabilities |
| IaC Security              | Trivy     | Scan Terraform & configs           |

---

# 3. Running Security Checks Locally

## 3.1 Secret Scanning — Gitleaks

### Run manually:

```bash
gitleaks protect --staged --config=.gitleaks.toml --verbose
```

### What it scans:

* Staged files
* Hardcoded keys
* API tokens
* Private keys
* `.env` files
* DB connection strings

### If a secret is detected:

* The commit will be blocked
* Review output
* Remove the secret
* Use environment variables instead

---

## 3.2 Static Code Scan — Semgrep

### Run locally:

```bash
semgrep scan --config=auto .
```

### Common findings:

* Injection risks
* Path traversal
* Insecure eval
* Weak crypto
* Unsafe deserialization

### If findings appear:

* Fix code securely
* Refactor unsafe logic
* Apply validation or sanitization

---

## 3.3 Dependency Vulnerability Scan — Trivy

### Scan project:

```bash
trivy fs .
```

### What it detects:

* Known CVEs in npm dependencies
* High/Critical vulnerabilities
* Misconfigurations

### Fix:

```bash
npm update
npm audit fix
```

---

## 3.4 Docker Image Scan

After building:

```bash
trivy image idurar-backend:latest
```

Fix by:

* Updating base images
* Removing unnecessary packages
* Using minimal/distroless images

---

# 4. Understanding Security Findings

## Severity Levels

| Severity | Meaning                 | Action                |
| -------- | ----------------------- | --------------------- |
| CRITICAL | Exploitable immediately | Must fix before merge |
| HIGH     | Serious risk            | Fix before release    |
| MEDIUM   | Security weakness       | Plan fix              |
| LOW      | Best practice issue     | Improve gradually     |
| INFO     | Informational           | No action required    |

---

# 5. Approved Suppression Guidelines

Security suppression is allowed **only when justified**.

## 5.1 When Suppression is Allowed

* False positive
* Test credentials
* Development-only code
* Non-exploitable scenario
* Compensating control exists

---

## 5.2 How to Suppress (Semgrep)

Add inline comment:

```javascript
// nosemgrep
const safe = path.join(BASE_DIR, userInput);
```

Must include reason:

```javascript
// nosemgrep: validated via allowlist middleware
```

---

## 5.3 How to Suppress (Gitleaks)

Add to `.gitleaks.toml` allowlist:

```toml
[allowlist]
paths = ['test-data/', 'docs/examples']
```

Never suppress real secrets.

---

## 5.4 Pipeline-Level Suppression

Only security team can modify:

* Gate rules
* Severity thresholds
* Blocking policies

---

# 6. What Will Block You

The following automatically fail pipeline:

* Hardcoded secrets
* Critical SAST findings
* Critical container CVEs
* High-risk DAST vulnerabilities
* Committed `.env` files
* Private keys

---

# 7. Secure Coding Expectations

Developers must:

* Never commit secrets
* Validate all user input
* Sanitize file paths
* Use parameterized queries
* Avoid eval()
* Enforce authentication checks
* Implement CSRF protection
* Follow OWASP Top 10 guidelines

---

# 8. Common Security Mistakes in This Project

Examples previously detected:

* Containers running as root
* Path traversal vulnerability
* Missing CSRF protection
* Weak TLS configuration
* Public IP exposure in Terraform
* Mutable Docker image tags

All must be avoided in future code.

---

# 9. DevSecOps Flow Overview

Developer →
Pre-Commit Hook →
Pull Request →
CI Security Gates →
DefectDojo Aggregation →
Release Decision

Security is enforced at every stage.

---

# 10. Security Escalation Process

If unsure:

1. Do not suppress blindly
2. Raise PR comment
3. Tag security reviewer
4. Provide justification
5. Document risk acceptance if approved

---

# 11. Secure Development Philosophy

We follow:

* Shift Left Security
* Zero Trust mindset
* Defense in Depth
* Automated Enforcement
* Measurable Security Gates

---
