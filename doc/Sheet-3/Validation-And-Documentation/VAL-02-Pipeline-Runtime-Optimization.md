# VAL-02 — Pipeline Runtime Optimization

This document records optimizations grounded in `.github/workflows/security-pipeline`.

## Observed runtime hotspots (by inspection)

- Multiple `npm install` / `npm ci` executions across jobs.
- Python-based tooling installs (Semgrep, NodeJsScan) without pip caching.
- Docker image pulls for scanners (gitleaks, trivy, zap, scancode) happen per run.

## Implemented optimizations (safe)

### 1) Node dependency caching
- Use `actions/setup-node` built-in caching (`cache: npm`) with appropriate `cache-dependency-path`.
- Prefer `npm ci` over `npm install` for repeatability and speed.

### 2) Python dependency caching
- Use `actions/setup-python` pip caching (`cache: pip`) where Semgrep/NodeJsScan are installed.

## Optional optimizations (not yet implemented)

### Docker layer caching
- Consider enabling BuildKit cache exports/imports for docker compose builds.

### Scanner ruleset tuning
- For Semgrep: reduce configs or scope directories if needed (while preserving coverage).

## Validation
- Compare GitHub Actions job durations before vs after changes.
- Ensure security report artifacts still get generated and uploaded.
