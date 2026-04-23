# SAST-04 — Tune False Positives

## PART 1 — Baseline Existing Issues

### Strategy

If your repository already contains many findings:

1. Run Semgrep once.
2. Save the results as a baseline snapshot.
3. Track only new findings going forward.

This prevents legacy findings from blocking development while ensuring new vulnerabilities are stopped.

---

### Create Baseline Folder

Create:

/security-baseline/

Store the baseline file:

security-baseline/semgrep-baseline.json

Generate it using:

semgrep --config=semgrep-rules/ --json > security-baseline/semgrep-baseline.json

---

### Optional Pipeline Update

Before your security gate step, add:

echo "Comparing against baseline..."

Advanced diff comparison logic can be added later.

---

## PART 2 — Inline Suppression (Controlled)

Developers may suppress findings when appropriate.

Specific rule suppression:

```js
// nosemgrep jwt-decode-without-verify
jwt.decode(token);
```

Blanket suppression:

```js
// nosemgrep
```

Blanket suppression should be discouraged and reviewed carefully.

---

## PART 3 — Expiry-Based Suppression (Enterprise Governance)

A stronger governance model requires suppressions to expire.

```js
// nosemgrep jwt-decode-without-verify
// expiry: 2026-03-01
```

### Code Review Policy Requirements

Every suppression must include:

* Ticket reference
* Expiry date
* Justification or reason

This prevents permanent silencing of security findings.

---

## PART 4 — Reduce Noise in Rule Definitions

Improve rule precision to reduce false positives.

Naive rule:

```yaml
pattern: jwt.decode($TOKEN)
```

Improved rule:

```yaml
patterns:
  - pattern: jwt.decode($TOKEN)
  - pattern-not: jwt.verify(...)
```

This ensures the rule triggers only when verification is missing.

Better rules increase trust in security tooling and reduce alert fatigue.
