
---

# FND-01 — Define Pipeline Scope (GitHub Actions)

**Deliverable:** Scope document + repositories/services list

---

## 1. Purpose

This document defines **what is in scope and out of scope** for all security scanning performed via **GitHub Actions**.

The objective is to eliminate ambiguity so that:

* Every pipeline run is **deterministic**
* **No critical attack surface** is skipped
* **Noise and false positives** are minimized
* Security gates are **consistent, enforceable, and auditable**

This scope applies to **all pre-runtime security controls** including:

* Secrets scanning
* SAST
* SCA
* Container scanning
* Infrastructure-as-Code (IaC) scanning
* Future DAST stages

---

## 2. Application Architecture Context

The application follows a **three-tier MERN architecture**, deployed as a **monorepo**.

| Tier         | Technology        | Responsibility                           |
| ------------ | ----------------- | ---------------------------------------- |
| Presentation | React (Vite)      | UI rendering, auth token handling        |
| Application  | Node.js + Express | REST API, authentication, business logic |
| Data         | MongoDB           | Persistent data storage                  |

Infrastructure and deployment are managed using:

* **Docker & Docker Compose**
* **Terraform (cloud provisioning)**
* **Kubernetes (container orchestration)**

---

## 3. Repository Scope

### Repository Details

* **Repository:** `static-application-security-testing-crm`
* **Architecture:** Three-tier (React + Node.js + MongoDB)
* **CI Platform:** GitHub Actions

---

## 3.1 In-Scope Directories

The following directories and files **must be scanned in every pipeline run**.

### In-Scope Paths

| Path                     | Tier    | Reason                                 |
| ------------------------ | ------- | -------------------------------------- |
| `frontend/`              | UI      | Auth handling, API consumption         |
| `backend/`               | API     | JWT, RBAC, CRUD, business logic        |
| `infra/`                 | Infra   | Docker, Compose, Terraform, Kubernetes |
| `db/`                    | DB      | Seed scripts, initialization logic     |
| `Dockerfile*`            | Build   | Container image security               |
| `docker-compose*.yml`    | Runtime | Deployment security                    |
| `package.json`           | Deps    | Dependency & license scanning          |
| `package-lock.json`      | Deps    | Accurate SCA resolution                |
| `yarn.lock` (if present) | Deps    | Lockfile-based SCA                     |
| `.npmrc`                 | Build   | Registry & install behavior            |
| `.env.example`           | Config  | Secrets hygiene                        |
| `openapi.yaml`           | API     | API & DAST coverage                    |

---

## 3.2 Infrastructure as Code (IaC) — In Scope

### Terraform

All Terraform files **must be scanned** for security misconfigurations.

```
**/*.tf
**/*.tfvars
**/*.tf.json
```

Coverage includes:

* IAM misconfigurations
* Overly permissive resources
* Public exposure
* Network misconfiguration

---

### Kubernetes

All Kubernetes manifests **must be scanned**.

```
**/*.yaml
**/*.yml
```

Specifically:

* Deployments
* Services
* Ingress
* ConfigMaps
* Secrets (structure only, not values)
* Helm-rendered manifests (if committed)

Coverage includes:

* Privileged containers
* HostPath mounts
* Missing resource limits
* Unsafe capabilities
* Insecure networking defaults

---

## 3.3 Explicitly In-Scope File Types

To avoid ambiguity, the following file types are **always in scope**:

```
**/*.js
**/*.jsx
**/*.ts
**/*.tsx
**/*.json
**/*.yml
**/*.yaml
**/*.tf
```

---

## 4. Explicitly Out-of-Scope

The following **must never be scanned**, regardless of pipeline context.

| Item                | Reason                 |
| ------------------- | ---------------------- |
| `node_modules/`     | Generated dependencies |
| `dist/`, `build/`   | Generated artifacts    |
| `coverage/`         | Test output            |
| `.git/`             | SCM internals          |
| Runtime volumes     | Ephemeral data         |
| Generated artifacts | No security value      |
| Local `.env` files  | Never committed        |

### Rationale

* Generated automatically
* No actionable security value
* High false-positive rate
* Increases pipeline noise and runtime

---

## 5. Environments Covered (GitHub Model)

Security scanning is enforced consistently across the following contexts:

| Environment    | Trigger         | Purpose                          |
| -------------- | --------------- | -------------------------------- |
| `pull_request` | PR to `main`    | Fail fast, block insecure merges |
| `main`         | Merge to `main` | Enforced release gate            |
| `nightly`      | `schedule`      | Deep scans, baseline refresh     |

---

### GitHub Constructs Used

* `on: pull_request`
* `on: push (branches: main)`
* `on: schedule`
* `environments:` for approval-based controls (future)

---

## 6. Pipeline Coverage Summary

This scope guarantees coverage across all critical attack surfaces.

| Area                           | Covered |
| ------------------------------ | ------- |
| Secrets scanning               | Yes     |
| Dependency scanning (SCA)      | Yes     |
| Application source code (SAST) | Yes     |
| Docker images                  | Yes     |
| Docker Compose                 | Yes     |
| Terraform (IaC)                | Yes     |
| Kubernetes manifests           | Yes     |
| Running app (DAST – future)    | Yes     |
| Centralized reporting          | Yes     |

---

## 7. FND-01 Deliverable Status

**Status:** ✅ COMPLETE

This scope provides:

* Clear scan boundaries
* Zero ambiguity on what GitHub Actions evaluates
* Alignment with branch protection rules
* Compatibility with SAST, SCA, IaC, image scanning, and DAST
* A future-proof foundation for enterprise DevSecOps

---
