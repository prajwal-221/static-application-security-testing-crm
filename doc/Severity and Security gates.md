# Severity Levels & Security Gates

---

## 1. Purpose

This document defines the **severity classification model** and **security gate enforcement rules** used in the GitLab CI/CD pipeline for a **three-tier MERN stack application**.

The goal is to ensure that **security findings are converted into deterministic pipeline decisions**, preventing insecure code from being merged or released while maintaining developer velocity.

---

## 2. Why Security Gates Matter

Security gates ensure that:

- Vulnerabilities are addressed **before runtime**
- Risk acceptance is **explicit**, not accidental
- Security enforcement is **consistent and automated**
- CI/CD pipelines act as **policy enforcement points**

Security gates are **non-negotiable controls**, not advisory warnings.

---

## 3. Unified Severity Classification Model

All security tools integrated into the pipeline **must map findings** into the following standardized severity levels.

| Severity      | Description                                             | Risk Posture            |
| ------------- | ------------------------------------------------------- | ----------------------- |
| Critical      | Actively exploitable or trivial to exploit              | Immediate business risk |
| High          | High likelihood of exploitation with significant impact | Release blocking        |
| Medium        | Exploitable under specific conditions                   | Tracked and prioritized |
| Low           | Best practice or hardening issue                        | Informational           |
| Informational | Contextual or non-actionable                            | Awareness only          |

---

## 4. Severity Normalization Strategy

Different tools report severity differently.
All tool outputs **must be normalized** into this unified model.

### Example Mapping

| Tool        | Native Severity | Unified Severity |
| ----------- | --------------- | ---------------- |
| SAST        | ERROR           | Critical         |
| SAST        | WARNING         | High             |
| SCA         | HIGH            | High             |
| SCA         | MEDIUM          | Medium           |
| Secret Scan | Verified Secret | Critical         |

---

## 5. Security Gate Philosophy

The pipeline enforces **fail-fast, shift-left security** using the following principles:

- **Zero tolerance for secrets**
- **Zero tolerance for known exploitable vulnerabilities**
- **Non-blocking visibility for medium/low risks**
- **Deterministic outcomes (no manual judgment in CI)**

---

## 6. Mandatory Pipeline Security Gates

### 6.1 Secrets Gate (Hard Block)

| Condition                  | Result                |
| -------------------------- | --------------------- |
| Any real secret detected   | ❌ Pipeline FAIL      |
| False positive allowlisted | ✅ Pipeline CONTINUES |

**Rationale:**
Secrets represent immediate compromise risk and must never be merged.

---

### 6.2 Dependency (SCA) Gate

| Severity Detected | Pipeline Action        |
| ----------------- | ---------------------- |
| Critical          | ❌ FAIL                |
| High              | ❌ FAIL                |
| Medium            | ⚠️ Allowed (tracked) |
| Low               | ℹ️ Allowed           |

**Scope:**

- `package.json`
- `package-lock.json`
- Transitive dependencies

---

### 6.3 Static Application Security Testing (SAST) Gate

| Severity Detected | Pipeline Action        |
| ----------------- | ---------------------- |
| Critical          | ❌ FAIL                |
| High              | ❌ FAIL                |
| Medium            | ⚠️ Allowed (tracked) |
| Low               | ℹ️ Allowed           |

**Coverage Areas:**

- Injection vulnerabilities
- Authentication & authorization flaws
- Insecure crypto usage
- Unsafe input handling
- Security misconfigurations

---

## 7. Branch-Level Enforcement Strategy

Security gates are enforced consistently across branches.

| Branch Type                      | Gate Enforcement                |
| -------------------------------- | ------------------------------- |
| Feature branches                 | Enabled, blocks merge           |
| Merge Requests                   | Fully enforced                  |
| Protected branches (main/master) | Strict enforcement              |
| Release tags                     | Identical to protected branches |

No branch bypass is allowed without **explicit security approval**.

---

## 8. Fail-Fast Execution Order

Security jobs must execute in the following order to minimize cost and feedback time:

1. **Secrets scanning**
2. **Dependency (SCA) scanning**
3. **Static code analysis (SAST)**

If an early gate fails, downstream jobs **must not execute**.

---

## 9. Developer Feedback Requirements

Every gate failure must:

- Clearly identify the failing rule
- Provide file, line number, and rule ID (where applicable)
- Be reproducible locally
- Include remediation guidance or references

Security gates must **educate, not just block**.

---

## 10. Exception Handling Policy

Exceptions are allowed only when:

- A vulnerability is a verified false positive
- A documented risk acceptance exists
- The exception is time-bound

All exceptions must be:

- Reviewed
- Logged
- Auditable
- Re-evaluated periodically

---

## 11. Audit & Compliance Requirements

- All gate decisions must be logged in CI logs
- All scan outputs must be preserved as artifacts
- Severity decisions must be deterministic
- Gate rules must be version-controlled

---

## 12. Deliverable Summary

| Item                                | Status |
| ----------------------------------- | ------ |
| Unified severity model defined      | ✅     |
| Secrets gate defined                | ✅     |
| SCA gate defined                    | ✅     |
| SAST gate defined                   | ✅     |
| GitLab enforcement strategy defined | ✅     |
| Audit-ready design                  | ✅     |
