# VAL-03 — Pipeline Blueprint Documentation

This blueprint is based on the current repository structure and the GitHub Actions workflow:
- `.github/workflows/security-pipeline`

## 1) Repository Setup (Local)

### Services
- Backend: `backend/`
- Frontend: `frontend/`

### Environment
- Backend expects environment files loaded in `backend/src/server.js`:
  - `.env`
  - `.env.local`

## 2) CI Pipeline Overview

The workflow runs on:
- `pull_request` to `main` and `staging`
- `push` to `main` and `staging`
- `schedule` (nightly)
- `workflow_dispatch` (manual)

### Stage: Secrets + SCA (`secrets_and_sca`)
- Secret scanning via **Gitleaks** (docker)
- Dependency scanning via **Trivy FS** (docker)
- npm audit for backend and frontend
- License scan via ScanCode Toolkit
- Uploads reports as artifacts

### Stage: ESLint Security (`eslint_security`)
- Runs backend and frontend security lint scripts

### Stage: SAST (`sast`)
- **Semgrep** (auto + `semgrep-rules/`)
- **NodeJsScan** on backend
- Uploads SAST artifacts

### Stage: Docker + Image/Runtime + DAST (`docker_security`)
- Builds and deploys stack via docker compose
- Generates SBOMs with Syft
- Trivy image scans (backend + frontend)
- Runtime Trivy scans
- DAST scans with ZAP:
  - Baseline scan against `http://localhost:4000`
  - API scan based on `openapi.yaml` (ZAP API Scan)
  - Active scan against `http://idurar-backend:4000`
  - Authenticated scan with `Authorization: Bearer ${{ secrets.JWT_TOKEN }}`
- Uploads artifacts, then cleans up compose

### Advanced Testing: API fuzzing (`advanced_testing_api_fuzzing`)
- Runs OpenAPI-guided fuzzing using ffuf and `scripts/ffuf_openapi_fuzz.py`
- Stores results under `security-reports/ffuf` and uploads as an artifact

### Reporting + Normalization
- Final report bundling
- Normalization via `scripts/normalize_reports.py`
- DefectDojo import job uploads scan files to `https://demo.defectdojo.org/api/v2/import-scan/`

## 3) Gates

Some gates exist in the workflow as commented-out steps (for strict enforcement when enabled). Examples:
- Secret gate (Gitleaks)
- SCA gates (Trivy FS)
- SAST gate (Semgrep)
- Image/runtime gates (Trivy)
- DAST gates (ZAP)

## 4) How to Run Locally (Developer)

### Run backend
- Ensure `.env` / `.env.local` are configured.
- Start backend with node (see backend package scripts).

### Run the stack similarly to CI
- Use docker compose build + up with the `.env` file.

### Run ZAP locally
- Baseline scan:
  - Targets `http://localhost:4000`
- Active/auth scan:
  - Targets `http://idurar-backend:4000` using the compose network.

## 5) DefectDojo Usage

The pipeline imports normalized reports into DefectDojo using:
- `DOJO_API_KEY`
- `DOJO_ENGAGEMENT_ID`

Scan type mapping in the workflow includes:
- Semgrep
- Trivy
- Gitleaks
- ZAP (XML)

## 6) Remediation Guidance (High-level)

- **Access control (IDOR):** enforce object-level checks per endpoint.
- **JWT/session policy:** align expiry and refresh strategy to policy; rotate tokens.
- **Unsafe queries:** avoid user-controlled field names/operators; use allowlists.
- **Headers:** apply a standard security headers middleware (e.g., helmet) and validate with ZAP baseline.
