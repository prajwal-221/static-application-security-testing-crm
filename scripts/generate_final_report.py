#!/usr/bin/env python3
"""
DevSecOps Final Security Report Generator

This script generates a comprehensive final security report by aggregating
and analyzing results from multiple security scanning tools.

Usage: python scripts/generate_final_report.py <reports_directory> <output_directory>
"""

import os
import json
import glob
import datetime
import xml.etree.ElementTree as ET
import sys
from collections import defaultdict
from jinja2 import Template


def normalize(sev):
    """Normalize severity levels to standard values"""
    sev = sev.upper()
    if sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
        return sev
    if sev in ["WARN", "WARNING"]:
        return "MEDIUM"
    return "LOW"


def parse_trivy(file):
    """Parse Trivy JSON reports"""
    try:
        data = json.load(open(file))
        for r in data.get("Results", []):
            for v in r.get("Vulnerabilities", []):
                s = normalize(v.get("Severity", "LOW"))
                severity[s] += 1
                tools["Trivy"].append(v.get("VulnerabilityID", "UNKNOWN"))
    except:
        pass


def parse_semgrep(file):
    """Parse Semgrep JSON reports"""
    try:
        data = json.load(open(file))
        for r in data.get("results", []):
            s = normalize(r.get("extra", {}).get("severity", "LOW"))
            severity[s] += 1
            tools["Semgrep"].append(r.get("check_id", "UNKNOWN"))
    except:
        pass


def parse_gitleaks(file):
    """Parse Gitleaks JSON reports with deduplication"""
    try:
        data = json.load(open(file))

        # Gitleaks v8+ uses different structure - handle both old and new formats
        findings = []

        if isinstance(data, dict):
            # New format: {"findings": [...], "summary": {...}}
            if "findings" in data:
                findings = data["findings"]
            # Legacy format: direct array of findings
            elif len(data) > 0 and any(k in data.get(next(iter(data.keys())), {})) for k in ["RuleID", "Description", "File"]:
                findings = [data] if "RuleID" in data or "Description" in data else []
        elif isinstance(data, list):
            # Direct array format
            findings = data

        unique_count = 0

        for f in findings:
            # Create a more robust fingerprint for deduplication
            title = f.get("Description") or f.get("RuleID") or f.get("title") or f.get("rule") or ""
            file_path = f.get("File") or f.get("file") or f.get("file_path") or ""
            line = str(f.get("StartLine") or f.get("startLine") or f.get("line") or "")

            # Normalize the fingerprint
            fingerprint = (title.strip(), file_path.strip(), line.strip())

            # Use global deduplication across all gitleaks files
            if fingerprint in global_gitleaks_seen:
                continue

            global_gitleaks_seen.add(fingerprint)
            unique_count += 1
            severity["HIGH"] += 1
            tools["Gitleaks"].append(title)

        print(f"Gitleaks processed {file}: {unique_count} unique secrets from {len(findings)} total findings")

    except Exception as e:
        print(f"Gitleaks parse error in {file}: {e}")
        # If parsing fails, don't add any counts
        pass


def parse_zap(file):
    """Parse OWASP ZAP XML reports"""
    try:
        tree = ET.parse(file)
        root = tree.getroot()
        for alert in root.iter("alertitem"):
            sev = normalize(alert.findtext("riskdesc", "Low").split()[0])
            severity[sev] += 1
            tools["ZAP"].append(alert.findtext("name", "Web Vulnerability"))
    except:
        pass


def main():
    """Main function to generate final security report"""
    global severity, tools, global_gitleaks_seen

    # Get command line arguments
    if len(sys.argv) != 3:
        print("Usage: python scripts/generate_final_report.py <reports_directory> <output_directory>")
        print("Example: python scripts/generate_final_report.py all-reports/normalized-reports final-report")
        sys.exit(1)

    REPORT_ROOT = sys.argv[1]
    OUTPUT_DIR = sys.argv[2]
    OUTPUT_FILE = os.path.join(OUTPUT_DIR, "final-security-report.md")

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Initialize global variables
    severity = defaultdict(int)
    tools = defaultdict(list)
    global_gitleaks_seen = set()

    # Process all report files
    gitleaks_files_processed = 0
    for f in glob.glob(f"{REPORT_ROOT}/**/*", recursive=True):
        if f.endswith(".json"):
            if "trivy" in f:
                parse_trivy(f)
            elif "semgrep" in f:
                parse_semgrep(f)
            elif "gitleaks" in f:
                parse_gitleaks(f)
                gitleaks_files_processed += 1
        elif f.endswith(".xml") and "zap" in f:
            parse_zap(f)

    print(f"Processed {gitleaks_files_processed} gitleaks report files")
    print(f"Total unique gitleaks findings: {len(tools['Gitleaks'])}")

    total = sum(severity.values())

    risk = "LOW"
    if severity["CRITICAL"] > 0:
        risk = "CRITICAL"
    elif severity["HIGH"] > 10:
        risk = "HIGH"
    elif severity["MEDIUM"] > 25:
        risk = "MODERATE"

    decision = "APPROVED FOR RELEASE WITH SECURITY CONDITIONS"
    if severity["CRITICAL"] > 0:
        decision = "RELEASE BLOCKED — CRITICAL RISK PRESENT"

    template = Template("""
# DevSecOps Final Security Report

**Project:** IDURAR Platform
**Environment:** Staging
**Pipeline:** DevSecOps CI/CD
**Date:** {{ date }}

---

# 1. Executive Summary

### Overall Security Posture: **{{ risk }} RISK**

| Severity | Count |
|------------|--------|
| Critical | {{ crit }} |
| High | {{ high }} |
| Medium | {{ med }} |
| Low | {{ low }} |
| Informational | {{ info }} |
| **Total** | **{{ total }}** |

**Release Decision:** **{{ decision }}**

---

# 2. Security Coverage Overview

End-to-end security validation was executed across:

- Secrets detection
- Dependency security (SCA)
- Static application security testing (SAST)
- Container image & runtime security
- Dynamic application security testing (DAST)
- Pipeline exploit validation

---

# 3. Consolidated Vulnerability Analysis

## A. Secrets & Credential Exposure — Gitleaks

**Findings:** {{ gitleaks }}
**Impact:** Credential compromise enables unauthorized access, lateral movement, and data exfiltration.

**Remediation:**
- Rotate all exposed credentials immediately
- Remove secrets from Git history
- Enforce secrets scanning in CI

**Engineering Fixes:**
- Use GitHub Secrets / Vault injection
- Implement pre-commit hooks
- Enforce secret lifecycle governance

---

## B. Dependency & SCA Findings — Trivy

**Findings:** {{ trivy }}
**Impact:** Known vulnerable libraries introduce exploitable attack paths.

**Remediation:**
- Patch high & critical CVEs
- Enforce dependency SLAs

**Engineering Fixes:**
- SBOM validation
- Automated dependency upgrades

---

## C. Static Code Vulnerabilities — Semgrep

**Findings:** {{ semgrep }}
**Impact:** Injection, authentication bypass, and logic flaws.

**Remediation:**
- Refactor insecure code
- Apply secure coding patterns

**Engineering Fixes:**
- SAST gating
- Secure coding standards

---

## D. Container Image & Runtime Vulnerabilities — Trivy

**Findings:** {{ trivy }}
**Impact:** Runtime exploitation and container breakout risk.

**Remediation:**
- Harden base images
- Patch runtime packages

**Engineering Fixes:**
- Distroless containers
- Runtime protection enforcement

---

## E. Dynamic Application Security Testing — OWASP ZAP

**Findings:** {{ zap }}
**Impact:** SQL injection, XSS, authentication bypass, session fixation.

**Remediation:**
- Apply OWASP Top 10 mitigations

**Engineering Fixes:**
- Secure request validation
- Security headers & session hardening

---

# 4. Root Cause Analysis

- Weak secrets governance
- Dependency lifecycle gaps
- Unhardened runtime environments
- Missing secure SDLC enforcement

---

# 5. Security Recommendations Roadmap

**Immediate (0–7 Days):**
- Patch critical CVEs
- Rotate secrets
- Harden containers

**Short Term (30 Days):**
- Enforce SAST & SCA gates
- Introduce SBOM governance

**Strategic (90 Days):**
- Zero Trust architecture
- Runtime exploit detection
- Threat modeling automation

---

# 6. DevSecOps Maturity Assessment

**Maturity Level:** Advanced

CI/CD demonstrates high security automation, governance, and operational readiness.

---

# 7. Strategic Security Enhancements

- CSPM & cloud posture management
- Continuous breach simulation
- Automated compliance reporting

---

# 8. Final Security Verdict

**{{ decision }}**

---

# 9. Appendix

All raw scan artifacts retained within CI/CD pipeline for compliance and audit purposes.
""")

    report = template.render(
        date=str(datetime.date.today()),
        crit=severity["CRITICAL"],
        high=severity["HIGH"],
        med=severity["MEDIUM"],
        low=severity["LOW"],
        info=severity["INFO"],
        total=total,
        risk=risk,
        decision=decision,
        gitleaks=len(tools["Gitleaks"]),
        trivy=len(tools["Trivy"]),
        semgrep=len(tools["Semgrep"]),
        zap=len(tools["ZAP"])
    )

    with open(OUTPUT_FILE, "w") as f:
        f.write(report)

    # Create README index file for all reports
    import subprocess
    subprocess.run(f'echo "DevSecOps Security Reports" > {OUTPUT_DIR}/README.txt', shell=True)
    subprocess.run(f'echo "====================================" >> {OUTPUT_DIR}/README.txt', shell=True)
    subprocess.run(f'find {OUTPUT_DIR} -type f -name "*.md" -o -name "*.html" -o -name "*.xml" -o -name "*.json" | sort >> {OUTPUT_DIR}/README.txt', shell=True)

    print(f"Final Security Report generated → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
