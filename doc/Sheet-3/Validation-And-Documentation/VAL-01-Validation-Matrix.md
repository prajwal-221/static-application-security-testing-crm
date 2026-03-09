# VAL-01 — Validation Matrix (Injected vs Detected)

This matrix is built from code verified on branch `SAST-Sheet-3`.

## Legend
- **Injected vuln**: The concrete insecure behavior present in code.
- **Location**: File and relevant logic.
- **Repro (example)**: Minimal steps/request to reproduce.
- **Detection stage(s)**: At least one stage in `.github/workflows/security-pipeline` that should detect it.
- **Notes**: Any gaps or reproducibility considerations.

---

## 1) Unsafe Query / NoSQL Injection Surface

- **Injected vuln**
  - User-controlled field name is used in a Mongo query builder.
- **Location**
  - `backend/src/controllers/middlewaresControllers/createCRUDController/filter.js`
  - Uses `.where(req.query.filter).equals(req.query.equal)`.
- **Repro (example)**
  - Call any endpoint wired to this controller with:
    - `?filter=<fieldName>&equal=<value>`
  - Then attempt using unexpected field names to validate the impact.
- **Detection stage(s)**
  - **SAST — Semgrep** (stage: `sast`)
  - **SAST — NodeJsScan** (stage: `sast`)
- **Notes**
  - This is a reproducible unsafe pattern because query structure is influenced by user input.

---

## 2) IDOR-style Read (Missing Object-Level Authorization)

- **Injected vuln**
  - Reads objects by `_id` without verifying ownership/tenant permissions.
- **Location**
  - `backend/src/controllers/middlewaresControllers/createCRUDController/read.js`
  - `Model.findOne({ _id: req.params.id, removed: false })`
- **Repro (example)**
  - Authenticate as user A.
  - Obtain a resource ID belonging to user B.
  - Request the read endpoint with that ID and confirm the response returns data instead of 403.
- **Detection stage(s)**
  - **DAST — ZAP Active Scan** (stage: `docker_security`) *if the API is reachable and ZAP coverage includes the endpoint*
  - **Advanced Testing — API Fuzzing (ffuf)** (job: `advanced_testing_api_fuzzing`) can help enumerate reachable IDs/endpoints
- **Notes**
  - IDOR is often hard for pure SAST rules to validate without context; DAST/proxy reproduction is typically required.

---

## 3) Missing Security Headers (No Helmet / CSP / etc.)

- **Injected vuln**
  - Server does not set common security headers by default.
- **Location**
  - `backend/src/app.js`
  - No `helmet()` middleware found.
- **Repro (example)**
  - After stack is running, run:
    - `curl -I http://localhost:4000/public/health`
  - Verify absence of headers like `Content-Security-Policy`, `X-Frame-Options`, `Strict-Transport-Security`.
- **Detection stage(s)**
  - **DAST — OWASP ZAP Baseline** (stage: `docker_security`)
- **Notes**
  - ZAP Baseline commonly reports missing headers.

---

## 4) Weak JWT Handling / Risky Session Policy

- **Injected vuln**
  - Long-lived token when `remember` is enabled.
- **Location**
  - `backend/src/controllers/middlewaresControllers/createAuthMiddleware/authUser.js`
  - `expiresIn: req.body.remember ? 365 * 24 + 'h' : '24h'`
- **Repro (example)**
  - Log in with `remember=true` and inspect the returned JWT.
  - Confirm token expiry is ~1 year.
- **Detection stage(s)**
  - **SAST — Semgrep** (stage: `sast`) depending on ruleset coverage
  - **Manual proxy testing (ZAP)** (ADV-03 workflow) to validate behavior end-to-end
- **Notes**
  - Whether this is considered “weak” depends on your policy; matrix records the behavior for reproducibility.

---

## 5) Download Endpoint Without `removed:false` / Object Authorization Check

- **Injected vuln**
  - Fetches a model by `_id` without `removed:false` and without object-level authorization checks.
- **Location**
  - `backend/src/handlers/downloadHandler/downloadPdf.js`
  - `Model.findOne({ _id: id }).exec();`
- **Repro (example)**
  - Call download route:
    - `GET /download/:directory/:file`
  - Use a valid `directory` and craft `file` so the derived `id` targets a record.
  - Validate whether downloads work for records that should be restricted.
- **Detection stage(s)**
  - **DAST — ZAP Active Scan** (stage: `docker_security`) (coverage dependent)
  - **Manual proxy testing (ZAP)** (ADV-03 workflow) for reliable reproduction
- **Notes**
  - This overlaps with IDOR-style behavior in download flows.

---

## 6) Reflected XSS (Intentional Injection)

- **Injected vuln**
  - User input is reflected directly into an HTML response without output encoding.
- **Location**
  - `backend/src/routes/coreRoutes/corePublicRouter.js`
  - `GET /public/xss?q=...` returns `<html><body>${q}</body></html>`
- **Repro (example)**
  - `curl "http://localhost:4000/public/xss?q=%3Cimg%20src%3Dx%20onerror%3Dalert(1)%3E"`
- **Detection stage(s)**
  - **SAST — Semgrep** (stage: `sast`) depending on ruleset coverage
  - **DAST — ZAP Baseline / Active** (stage: `docker_security`) if ZAP crawls or the OpenAPI spec includes the endpoint
- **Notes**
  - This endpoint is intentionally vulnerable for validation purposes.

---

## 7) Path Traversal-style File Read (Intentional Injection)

- **Injected vuln**
  - User-controlled path is joined to a server-side directory and read from disk without path traversal prevention.
- **Location**
  - `backend/src/routes/coreRoutes/corePublicRouter.js`
  - `GET /public/vuln-file?path=...` reads `fs.readFileSync(path.join(rootDir, path))`
- **Repro (example)**
  - Attempt to read outside the intended directory:
    - `curl "http://localhost:4000/public/vuln-file?path=../server.js"`
- **Detection stage(s)**
  - **SAST — Semgrep** (stage: `sast`) depending on ruleset coverage
  - **DAST — ZAP Active** (stage: `docker_security`) (coverage dependent)
- **Notes**
  - This endpoint is intentionally vulnerable for validation purposes.

## Gaps / Items not yet verified by code search

The following APP-06 items were not located with explicit, unambiguous markers during current code inspection:
- Reflected XSS endpoint intentionally echoing unsanitized input
- A deliberately insecure path traversal handler (current `corePublicRouter` includes an `isPathInside` guard)

If you point me to the exact endpoints/files for these, I will extend this matrix with exact locations + reproduction steps + detection stages.
