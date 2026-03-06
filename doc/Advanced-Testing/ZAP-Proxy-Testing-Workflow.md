# ZAP Proxy Testing Workflow

## Goal
Use OWASP ZAP as an intercepting proxy to:
- Validate automated findings
- Reproduce issues reliably
- Discover business-logic flaws and chained attack paths

## Setup
- Start the application in the test environment.
- Start ZAP locally.
- Configure browser/system proxy to point to ZAP:
  - Proxy host: 127.0.0.1
  - Proxy port: 8080 (or your configured ZAP proxy port)

## TLS / HTTPS Interception
- In ZAP, generate and install the ZAP Root CA certificate into your browser.
- Confirm you can browse HTTPS targets without certificate warnings.

## Traffic Capture
- Enable “Break”/intercept for:
  - Authorization headers
  - Cookie headers
  - Requests that mutate state (POST/PUT/PATCH/DELETE)
- Browse core user flows:
  - Login
  - CRUD for major objects
  - Export/import flows
  - Admin flows (if applicable)

## Reproduction and Validation
- For each suspected issue:
  - Re-send the request in ZAP (History → right click → Resend)
  - Modify parameters/headers to validate exploitability
  - Record:
    - URL
    - Method
    - Role/user
    - Request body
    - Response codes and evidence

## Authorization Testing (IDOR / AuthZ bypass)
- Capture a request for a resource belonging to user A.
- Replay the same request with user B token/cookie.
- Confirm server-side enforcement (403/404 expected).

## Session/JWT Testing
- Capture JWTs from the login flow.
- Test:
  - Expired token
  - Token reuse after logout
  - Missing/empty token
  - Tampering (signature should fail)

## Injection Testing (Targeted)
- Identify user-controlled inputs:
  - Search/filter/sort
  - Pagination
  - IDs
  - File names
- Send payload variants via ZAP:
  - Quote/escape payloads
  - JSON structure manipulation
  - NoSQL operators (if backend uses Mongo)

## Discovering Chaining Paths
- Map multi-step workflows:
  - Create → Approve → Export
  - Invite user → assign role → perform action
- Look for:
  - Missing checks in intermediate steps
  - State-machine bypass via direct API calls

## Output / Evidence
- Export relevant requests from ZAP.
- Capture screenshots of proof.
- Record reproduction steps for reporting.
