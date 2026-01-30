#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime, UTC

REPORT_DIR = Path("reports")
OUTPUT_JSON = REPORT_DIR / "security-report.json"
OUTPUT_HTML = REPORT_DIR / "security-report.html"


def safe_read(path):
    if not path.exists() or path.stat().st_size == 0:
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


# ----------------------------
# Load Raw Tool Outputs
# ----------------------------

yamllint_raw = safe_read(REPORT_DIR / "yamllint.json")
kubeconform_raw = safe_read(REPORT_DIR / "kubeconform.json")
kubescore_raw = safe_read(REPORT_DIR / "kube-score.json")
kubesec_raw = safe_read(REPORT_DIR / "kubesec.json")
checkov_raw = safe_read(REPORT_DIR / "checkov.json")
conftest_raw = safe_read(REPORT_DIR / "conftest.json")

# ----------------------------
# yamllint Parsing
# ----------------------------

yamllint_issues = yamllint_raw if isinstance(yamllint_raw, list) else []

# ----------------------------
# kubeconform Parsing
# ----------------------------

kubeconform_summary = {"valid": 0, "invalid": 0, "errors": 0, "skipped": 0}
if isinstance(kubeconform_raw, dict):
    kubeconform_summary = kubeconform_raw.get("summary", kubeconform_summary)

# ----------------------------
# kube-score Parsing
# ----------------------------

kubescore_critical = []
kubescore_warning = []

if isinstance(kubescore_raw, list):
    for obj in kubescore_raw:
        for check in obj.get("checks", []):
            if check.get("skipped"):
                continue
            grade = check.get("grade", 10)
            if grade <= 3:
                kubescore_critical.append(check)
            elif grade <= 6:
                kubescore_warning.append(check)

# ----------------------------
# kubesec Parsing (FIXED)
# ----------------------------

kubesec_findings = []

if isinstance(kubesec_raw, list):
    for block in kubesec_raw:
        # kubesec output may be: [ {...} ]  OR  {...}
        if isinstance(block, list):
            entries = block
        elif isinstance(block, dict):
            entries = [block]
        else:
            continue

        for entry in entries:
            if not isinstance(entry, dict):
                continue

            advise = entry.get("scoring", {}).get("advise", [])
            if advise:
                kubesec_findings.append({
                    "object": entry.get("object"),
                    "score": entry.get("score"),
                    "advise": advise
                })

# ----------------------------
# checkov Parsing
# ----------------------------

checkov_failed = []

if isinstance(checkov_raw, list):
    for block in checkov_raw:
        results = block.get("results", {})
        for fail in results.get("failed_checks", []):
            checkov_failed.append({
                "id": fail.get("check_id"),
                "name": fail.get("check_name"),
                "severity": fail.get("severity"),
                "file": fail.get("file_path"),
                "guideline": fail.get("guideline")
            })

# ----------------------------
# conftest Parsing
# ----------------------------

conftest_violations = conftest_raw if isinstance(conftest_raw, list) else []

# ----------------------------
# Final Report Object
# ----------------------------

report = {
    "generated_at": datetime.now(UTC).isoformat(),
    "summary": {
        "yamllint_warnings": len(yamllint_issues),
        "kubeconform_invalid": kubeconform_summary.get("invalid", 0),
        "kubescore_critical": len(kubescore_critical),
        "kubescore_warning": len(kubescore_warning),
        "kubesec_findings": len(kubesec_findings),
        "checkov_failed": len(checkov_failed),
        "conftest_violations": len(conftest_violations)
    },
    "details": {
        "yamllint": yamllint_issues,
        "kubeconform": kubeconform_summary,
        "kube_score_critical": kubescore_critical,
        "kube_score_warning": kubescore_warning,
        "kubesec": kubesec_findings,
        "checkov": checkov_failed,
        "conftest": conftest_violations
    }
}

OUTPUT_JSON.write_text(json.dumps(report, indent=2))

# ----------------------------
# HTML Dashboard Generation
# ----------------------------

def section(title, content):
    return f"<div class='card'><h3>{title}</h3><pre>{json.dumps(content, indent=2)}</pre></div>"

html = f"""
<!DOCTYPE html>
<html>
<head>
<title>Kubernetes DevSecOps Security Report</title>
<style>
body {{ font-family: Inter, Arial; background:#020617; color:#e5e7eb; padding:40px }}
h1 {{ color:#38bdf8 }}
h2 {{ color:#22c55e }}
h3 {{ color:#facc15 }}
.card {{ background:#020617; border:1px solid #1e293b; border-radius:10px; padding:20px; margin-bottom:20px }}
.summary span {{ display:block; margin:6px 0 }}
.bad {{ color:#f87171 }}
.warn {{ color:#facc15 }}
.good {{ color:#4ade80 }}
pre {{ white-space:pre-wrap; word-break:break-word }}
</style>
</head>
<body>

<h1>🔐 Kubernetes DevSecOps Security Report</h1>
<p><b>Generated:</b> {report["generated_at"]}</p>

<h2>📊 Summary</h2>
<div class="card summary">
  <span class="warn">yamllint warnings: {report["summary"]["yamllint_warnings"]}</span>
  <span class="good">kubeconform invalid: {report["summary"]["kubeconform_invalid"]}</span>
  <span class="bad">kube-score critical: {report["summary"]["kubescore_critical"]}</span>
  <span class="warn">kube-score warnings: {report["summary"]["kubescore_warning"]}</span>
  <span class="warn">kubesec findings: {report["summary"]["kubesec_findings"]}</span>
  <span class="bad">checkov failed: {report["summary"]["checkov_failed"]}</span>
  <span class="good">conftest violations: {report["summary"]["conftest_violations"]}</span>
</div>

<h2>🔎 Detailed Findings</h2>

{section("yamllint", report["details"]["yamllint"])}
{section("kubeconform", report["details"]["kubeconform"])}
{section("kube-score (CRITICAL)", report["details"]["kube_score_critical"])}
{section("kube-score (WARNING)", report["details"]["kube_score_warning"])}
{section("kubesec", report["details"]["kubesec"])}
{section("checkov", report["details"]["checkov"])}
{section("conftest", report["details"]["conftest"])}

</body>
</html>
"""

OUTPUT_HTML.write_text(html)

print("Security reports generated successfully.")
print(f"JSON → {OUTPUT_JSON}")
print(f"HTML → {OUTPUT_HTML}")
