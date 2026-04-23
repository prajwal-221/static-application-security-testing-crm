
---

# FND-02 — Severity Model & Security Gates

**Deliverable:** Gate policy (Critical / High rules)

---

## 1. Purpose

This document defines **how security scan results are converted into deterministic pipeline decisions**.

Security findings are **not advisory**.
They are **policy enforcement inputs** that directly control whether a pipeline:

* Continues
* Fails
* Requires explicit, auditable approval

This policy applies uniformly across:

* Source code
* Dependencies
* Containers
* Infrastructure as Code (IaC)
* Runtime testing (DAST)

---

## 2. Unified Severity Classification

All tools integrated into the pipeline **must normalize findings** into the following unified severity model.

| Severity          | Definition                                        |
| ----------------- | ------------------------------------------------- |
| **Critical**      | Actively exploitable, immediate compromise        |
| **High**          | Realistic exploit path with high business impact  |
| **Medium**        | Exploitable under specific conditions or chaining |
| **Low**           | Hardening, hygiene, or best-practice issues       |
| **Informational** | Contextual, non-actionable findings               |

> No tool-specific severity is allowed to bypass this model.

---

## 3. Security Gate Philosophy

The pipeline enforces **fail-fast, shift-left security** using the following principles:

* **Fail fast** to reduce blast radius and cost
* **Zero tolerance for secrets**
* **Zero tolerance for known exploitable vulnerabilities**
* **No subjective judgment inside CI**
* **Explicit, time-bound risk acceptance only**

Security gates are **mandatory controls**, not warnings.

---

## 4. Mandatory Security Gates by Control Type

This section defines **all security gates required by the task list**.
If a gate appears here, it **must be enforced** in CI.

---

### 4.1 Secrets Scanning Gate (Hard Gate)

**Applies to:** `SEC-01`, `SEC-02`

| Condition                    | Outcome         |
| ---------------------------- | --------------- |
| Any verified secret detected | ❌ Pipeline FAIL |

**Rules:**

* No overrides
* No approvals
* No expiry-based exceptions
* Applies to filesystem and Git history

**Rationale:**
Secrets represent **immediate compromise risk** and invalidate all other controls.

---

### 4.2 Dependency Scanning Gate (SCA)

**Applies to:** `SCA-01`, `SCA-02`, `SCA-04`

| Severity | Outcome           |
| -------- | ----------------- |
| Critical | ❌ FAIL            |
| High     | ❌ FAIL            |
| Medium   | Allowed (tracked) |
| Low      | Allowed           |

**Scope:**

* Direct dependencies
* Transitive dependencies
* Lockfile-driven resolution

---

### 4.3 Static Application Security Testing Gate (SAST)

**Applies to:** `SAST-01` → `SAST-05`

| Severity | Outcome           |
| -------- | ----------------- |
| Critical | ❌ FAIL            |
| High     | ❌ FAIL            |
| Medium   | Allowed (tracked) |
| Low      | Allowed           |

**Coverage includes:**

* Injection flaws (SQL / NoSQL / Command)
* Authentication bypass
* Authorization flaws
* JWT misuse
* Unsafe file handling
* Insecure cryptography
* Security misconfigurations

---

### 4.4 Container Image Security Gate

**Applies to:** `IMG-01`, `IMG-02`

| Severity | Outcome           |
| -------- | ----------------- |
| Critical | ❌ FAIL            |
| High     | ❌ FAIL            |
| Medium   | Allowed (tracked) |
| Low      | Allowed           |

**Scope:**

* OS packages
* Application dependencies
* Base image vulnerabilities

**Notes:**

* Image scanning gates are enforced **after build**
* No production image promotion if gate fails

---

### 4.5 Infrastructure as Code (IaC) & Configuration Gate

**Applies to:** `IAC-01`, `IAC-02`

This gate evaluates **Docker, Docker Compose, Terraform, and Kubernetes**.

#### Critical Misconfigurations (Hard Fail)

| Misconfiguration                    | Outcome |
| ----------------------------------- | ------- |
| Privileged containers               | ❌ FAIL  |
| HostPath mounts                     | ❌ FAIL  |
| Containers running as root          | ❌ FAIL  |
| Missing CPU / memory limits         | ❌ FAIL  |
| Publicly exposed sensitive services | ❌ FAIL  |

#### Other Findings

| Severity | Outcome           |
| -------- | ----------------- |
| Critical | ❌ FAIL            |
| High     | ❌ FAIL            |
| Medium   | Allowed (tracked) |
| Low      | Allowed           |

---

### 4.6 Dynamic Application Security Testing (DAST) Gate

**Applies to:** `DAST-01` → `DAST-05`

| Severity | Outcome           |
| -------- | ----------------- |
| Critical | ❌ FAIL            |
| High     | ❌ FAIL            |
| Medium   | Allowed (tracked) |
| Low      | Allowed           |

**Coverage includes:**

* Injection vulnerabilities
* Authentication flaws
* Authorization issues (IDOR)
* Security header misconfigurations
* Business logic abuse (where detectable)

**Notes:**

* Applies to baseline, active, authenticated, and API scans
* Enforced only after successful test deployment

---

## 5. Gate Execution Order (Fail-Fast Strategy)

To minimize cost and feedback time, gates **must execute in strict order**:

1. **Secrets scanning**
2. **Dependency scanning (SCA)**
3. **Static code analysis (SAST)**
4. **Build**
5. **Image scanning**
6. **IaC / configuration scanning**
7. **Deploy test environment**
8. **DAST**

If any gate fails:

* Downstream jobs **must not execute**
* Pipeline status **must be FAILED**

---

## 6. Approval & Exception Model (Policy Level)

| Severity | Approval Allowed        |
| -------- | ----------------------- |
| Critical | ❌ Never                 |
| High     | ❌ Never (per task list) |
| Medium   | ✅ Tracked only          |
| Low      | ✅ Tracked only          |

> **Important:**
> Although later tasks mention “optional approvals” for High, this **foundation policy intentionally disallows High-severity bypass** to keep enforcement strict and unambiguous.
> Any relaxation must be a **conscious policy change**, not an implementation detail.

---

## 7. Audit & Compliance Requirements

For every gate decision:

* Decision must be logged in CI output
* Raw scan artifacts must be preserved
* Severity mapping must be deterministic
* Gate logic must be version-controlled
* Failures must be reproducible locally

---

## 8. FND-02 Deliverable Status

**Status:** ✅ COMPLETE

This severity model and gate policy:

* Covers **all gates required by the task list**
* Aligns with SAST, SCA, Image, IaC, and DAST phases
* Is deterministic, auditable, and enforceable
* Is future-proof for DefectDojo and runtime security
* Can be implemented directly in GitHub Actions

---

