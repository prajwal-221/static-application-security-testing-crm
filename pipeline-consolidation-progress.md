# Pipeline Consolidation Progress

## Overview
Consolidating two GitHub Actions pipelines into one comprehensive DevSecOps pipeline:
1. **security-pipeline.yaml** - Application security scanning (SAST, SCA, DAST, etc.)
2. **IAC-K8S-Scanning** - Infrastructure-as-Code and Kubernetes security scanning

## Consolidation Plan

### Stage Order in Final Pipeline (Consolidated)

| Stage | Name | Contains |
|-------|------|----------|
| 1 | Secrets + SCA Scan | Gitleaks, Trivy FS, npm audit, License scan |
| 1.5 | ESLint Security Baseline | Backend + Frontend linting |
| 2 | SAST | Semgrep, NodeJsScan |
| 3 | **K8s Manifest Validation & Policy** | YAML Lint, Kubeconform, Kube-score, Conftest |
| 4 | **K8s & IaC Security Scanning** | Kubesec, Checkov, IaC Gate |
| 5 | Docker + DAST | Docker build, Trivy image, ZAP scans |
| 6 | API Fuzzing | ffuf |
| 7 | Final Aggregated Report | All artifacts bundle |
| 8 | Normalize Reports | Python normalization |
| 9 | DefectDojo Upload | Report upload |
| 10 | Validation | Mutillidae testing |
| 11 | Documentation | Blueprint generation |
| 12 | Final Security Report | Executive report |
| 13 | DefectDojo Enterprise | Final report upload |
| 14 | IaC Report | IaC-specific summary |

## Progress

- [x] Created progress tracking document
- [x] Created final consolidated pipeline YAML
- [x] Merged security-pipeline.yaml Stage 1, 1.5, and 2
- [x] Consolidated IAC-K8S stages into Stage 3 and Stage 4
- [x] Updated all job dependencies
- [x] Renumbered remaining stages (5-14)

## Dependencies to Update

### Job Dependencies After Consolidation
- `eslint_security` needs: `secrets_and_sca`
- `sast` needs: `secrets_and_sca`
- `yaml_lint` needs: `sast` (was parallel, now sequential after SAST)
- `kubeconform` needs: `yaml_lint`
- `kube_score` needs: `kubeconform`
- `kubesec` needs: `kubeconform`
- `checkov_scan` needs: `kubeconform`
- `iac_gate_enforcement` needs: `checkov_scan`
- `conftest` needs: `[kube_score, kubesec, iac_gate_enforcement]`
- `docker_security` needs: `sast` (keeping original, but now after IAC stages)
- `advanced_testing_api_fuzzing` needs: `docker_security`
- All report jobs need updated dependencies

## Notes
- All security gates (enforcements) are currently commented out with `#` - preserving this behavior
- The pipeline uses `continue-on-error: true` for most jobs to allow full scanning even if individual tools fail
- Reports are uploaded as artifacts at each stage
- Final consolidated report will be generated at the end
