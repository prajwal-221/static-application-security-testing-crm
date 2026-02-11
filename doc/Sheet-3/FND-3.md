
# FND-03 — Triage & Exception Workflow

**Deliverable:** Triage SOP + exception workflow

---

## 1. Ownership Model

| Area                | Owner                  |
| ------------------- | ---------------------- |
| Secrets             | DevSecOps              |
| Frontend SAST       | Frontend Lead          |
| Backend SAST        | Backend Lead           |
| Dependencies (SCA)  | Application Owner      |
| Containers & Images | Platform Team          |
| IaC (Terraform/K8s) | Platform Team          |
| DAST                | Security + Application |

Each finding **must have exactly one accountable owner**.

---

## 2. SLA Commitments

| Severity | SLA             |
| -------- | --------------- |
| Critical | 24 hours        |
| High     | 3 business days |
| Medium   | Next sprint     |
| Low      | Backlog         |

SLA breaches **must be visible and auditable**.

---

## 3. Standard Triage Flow

1. Finding generated in **GitHub Actions**
2. Scan artifact preserved
3. Finding uploaded to **central vulnerability tracker** (future: DefectDojo)
4. Owner classifies finding as:

   * **True Positive**
   * **False Positive**
   * **Risk Accepted**
5. Decision recorded with:

   * Evidence
   * Owner
   * Timestamp
   * Expiry (if applicable)

---

## 4. Source of Truth

All triage decisions **must be recorded in a single authoritative system**:

* Primary: **DefectDojo,Or Snyk (or any other vulnerability tracker)**
* Interim (before Dojo): **GitHub Issues / Security tab**

Local comments, chat messages, or CI logs **are not valid sources of record**.

---

## 5. False Positive Suppression Rules

False positives are allowed **only** when:

* Clear justification is documented
* Suppression is scoped narrowly
* Expiry date is defined (max 90 days)

### Allowed Methods

* Semgrep inline suppression with reason
* Trivy ignore by CVE with expiry
* ZAP alert suppression with justification

Permanent suppressions are **not allowed**.

---

## 6. Risk Acceptance Policy

Risk acceptance is allowed **only for non-Critical findings**.

### Required Fields

* Risk description
* Business justification
* Compensating controls
* Owner
* Expiry date (maximum 90 days)

### Rules

* Critical vulnerabilities cannot be accepted
* Secrets can never be accepted
* Risk acceptance **must expire and be re-reviewed**

---

## 7. Expiry Enforcement

When a suppression or risk acceptance **expires**:

* The finding is treated as **new**
* Security gates apply again
* Pipeline failure behavior is restored automatically

No manual reminders or trust-based enforcement.

---

## 8. Escalation Rules

* Repeated Medium findings across **3 consecutive releases** escalate to High
* SLA breaches escalate to Security leadership
* Chronic suppressions trigger manual review

---

## 9. Developer Feedback Requirements

Every triaged finding must provide:

* File and line number (where applicable)
* Rule or CVE identifier
* Clear remediation guidance
* Reproduction steps when possible

The goal is **developer enablement**, not friction.

---

## 10. FND-03 Status

**Status:** ✅ COMPLETE

This workflow ensures:

* No ignored vulnerabilities
* No permanent exceptions
* Clear ownership and accountability
* Audit-ready evidence
* Alignment with FND-02 enforcement

---
