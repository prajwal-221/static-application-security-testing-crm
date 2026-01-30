#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime, UTC

REPORT_DIR = Path("reports")
OUTPUT_JSON = REPORT_DIR / "security-report.json"
OUTPUT_HTML = REPORT_DIR / "security-report.html"

def read_json(filename):
    path = REPORT_DIR / filename
    if not path.exists() or path.stat().st_size == 0:
        return []
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return []

yamllint = read_json("yamllint.json")
kubeconform = read_json("kubeconform.json")
kubescore = read_json("kube-score.json")
kubesec = read_json("kubesec.json")
checkov = read_json("checkov.json")
conftest = read_json("conftest.json")

report = {
    "generated_at": datetime.now(UTC).isoformat(),
    "summary": {
        "yamllint": len(yamllint),
        "kubeconform_errors": kubeconform.get("invalid", 0) if isinstance(kubeconform, dict) else 0,
        "kube_score_critical": sum(1 for r in kubescore if "CRITICAL" in json.dumps(r)),
        "kubesec_findings": len(kubesec),
        "checkov_failed": len(checkov),
        "conftest_violations": len(conftest)
    },
    "details": {
        "yamllint": yamllint,
        "kubeconform": kubeconform,
        "kube_score": kubescore,
        "kubesec": kubesec,
        "checkov": checkov,
        "conftest": conftest
    }
}

OUTPUT_JSON.write_text(json.dumps(report, indent=2))

# Generate HTML report
html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>DevSecOps Kubernetes Security Report</title>
    <style>
        body {{ font-family: Arial; background: #0f172a; color: #e5e7eb; padding: 30px; }}
        h1, h2 {{ color: #38bdf8; }}
        .card {{ background: #020617; padding: 20px; margin-bottom: 15px; border-radius: 8px; }}
        .critical {{ color: #f87171; }}
        .ok {{ color: #4ade80; }}
        pre {{ background: #020617; padding: 15px; border-radius: 8px; overflow-x: auto; }}
    </style>
</head>
<body>

<h1>🔐 Kubernetes DevSecOps Security Report</h1>
<p><b>Generated:</b> {report["generated_at"]}</p>

<h2>📊 Summary</h2>
<div class="card">
    <p>yamllint warnings: <b>{report['summary']['yamllint']}</b></p>
    <p>kubeconform invalid: <b>{report['summary']['kubeconform_errors']}</b></p>
    <p>kube-score critical: <b>{report['summary']['kube_score_critical']}</b></p>
    <p>kubesec scanned: <b>{report['summary']['kubesec_findings']}</b></p>
    <p>checkov failed: <b>{report['summary']['checkov_failed']}</b></p>
    <p>conftest violations: <b>{report['summary']['conftest_violations']}</b></p>
</div>

<h2>🔎 Detailed Findings</h2>
<pre>{json.dumps(report["details"], indent=2)}</pre>

</body>
</html>
"""

OUTPUT_HTML.write_text(html)

print("Security reports generated successfully.")
print(f"- JSON: {OUTPUT_JSON}")
print(f"- HTML: {OUTPUT_HTML}")
