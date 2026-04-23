# FND-04 — Report Formats & Artifact Retention

**Deliverable:** Report format standard & artifact retention plan

---

## 1. Standard Output Formats

All security tooling **must produce machine-readable, deterministic output** suitable for automated ingestion, auditing, and long-term retention.

### Approved Formats by Tool

| Tool               | Required Output Format |
| ------------------ | ---------------------- |
| Gitleaks           | JSON                   |
| Semgrep            | SARIF + JSON           |
| Trivy (Filesystem) | JSON                   |
| Trivy (Image)      | JSON                   |
| Checkov            | JSON                   |
| OWASP ZAP          | JSON + HTML            |
| SBOM (Syft)        | JSON                   |

### Format Usage Rules

* **JSON**
  * System of record
  * Required for DefectDojo ingestion
* **SARIF**
  * Required for GitHub Code Scanning integration
* **HTML**
  * Human-readable review only
  * Allowed **exclusively for DAST (OWASP ZAP)**

---

## 2. GitHub Artifacts Strategy

All scan results **must be persisted as GitHub Actions artifacts** with automated lifecycle management.

### Retention Policy

| Artifact Type      | Retention Period |
| ------------------ | ---------------- |
| Pull Request scans | 30 days          |
| Main branch scans  | 90 days          |
| Nightly scans      | 14 days          |
| SBOMs              | 90 days          |

**Retention enforcement requirements:**

* Must be configured directly in **GitHub Actions artifact settings**
* Manual cleanup is **not permitted**

---

## 3. Artifact Contents

### Required Inclusions

Artifacts  **must include** :

* Raw tool scan outputs
* Normalized JSON reports
* CI execution logs
* SBOM files (where applicable)

### Explicit Exclusions

Artifacts  **must not include** :

* Secrets of any kind
* Tokens or credentials
* Environment variables
* Runtime payload data
* Ephemeral execution secrets

---

## 4. Artifact Scope by Pipeline Context

| Pipeline Context | Artifact Scope                          |
| ---------------- | --------------------------------------- |
| Pull Request     | Security scan reports only              |
| Main Branch      | Security reports + SBOMs                |
| Nightly          | Full reports, baselines, and trend data |

---

## 5. Artifact Integrity & Size Controls

To preserve reliability and CI stability:

* Large artifacts **must be compressed** (`.zip` or `.gz`)
* Individual artifacts must remain within practical CI size limits
* **Corrupted, partial, or incomplete artifacts invalidate the scan**
* Failed artifact uploads are treated as pipeline failures

---

## 6. Audit & Compliance Guarantees

This standard ensures:

* Deterministic, repeatable security evidence
* Long-term traceability across builds and releases
* Reproducibility of failures and findings
* Tool-agnostic ingestion pipelines
* Native compatibility with DefectDojo and GitHub Security features

---

## 7. FND-04 Status

**Status:** ✅ COMPLETE

This completes the **Foundations & Standards phase** with:

* Clear output expectations
* Controlled artifact lifecycle
* Audit-ready evidence
* Zero ambiguity for CI implementation
