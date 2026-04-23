#!/usr/bin/env python3

import json
import pathlib
import re
from datetime import datetime, timezone

REPORT_DIR = pathlib.Path("reports")
OUTPUT_JSON = REPORT_DIR / "security-report.json"
OUTPUT_HTML = REPORT_DIR / "security-report.html"


def safe_read_json(path):
    if not path.exists() or path.stat().st_size == 0:
        return []
    try:
        return json.loads(path.read_text())
    except Exception:
        return []


def flatten(data):
    if isinstance(data, list):
        result = []
        for item in data:
            if isinstance(item, list):
                result.extend(flatten(item))
            else:
                result.append(item)
        return result
    return data


def parse_yamllint():
    yamllint_txt = REPORT_DIR / "yamllint.txt"
    results = []

    if not yamllint_txt.exists():
        return results

    pattern = re.compile(r"(.*):(\d+):(\d+): \[(\w+)\] (.*)")

    for line in yamllint_txt.read_text().splitlines():
        match = pattern.match(line.strip())
        if match:
            results.append({
                "file": match.group(1),
                "line": int(match.group(2)),
                "column": int(match.group(3)),
                "level": match.group(4),
                "message": match.group(5)
            })

    return results


def parse_kubescore(kubescore):
    critical = []
    warning = []

    for obj in kubescore:
        for check in obj.get("checks", []):
            if check.get("skipped"):
                continue
            grade = check.get("grade", 10)
            if grade <= 3:
                critical.append(check)
            elif grade <= 6:
                warning.append(check)

    return critical, warning


def parse_kubesec(kubesec):
    findings = []

    for entry in flatten(kubesec):
        if not isinstance(entry, dict):
            continue

        advise = entry.get("scoring", {}).get("advise", [])
        if advise:
            findings.append({
                "object": entry.get("object"),
                "score": entry.get("score"),
                "advise": advise
            })

    return findings


def parse_checkov(checkov):
    failed = []

    if isinstance(checkov, dict):
        for fail in checkov.get("results", {}).get("failed_checks", []):
            failed.append({
                "id": fail.get("check_id"),
                "name": fail.get("check_name"),
                "severity": fail.get("severity"),
                "file": fail.get("file_path"),
                "guideline": fail.get("guideline")
            })

    return failed


def main():
    yamllint = parse_yamllint()
    kubeconform = safe_read_json(REPORT_DIR / "kubeconform.json")
    kubescore_raw = safe_read_json(REPORT_DIR / "kube-score.json")
    kubesec_raw = safe_read_json(REPORT_DIR / "kubesec.json")
    checkov_raw = safe_read_json(REPORT_DIR / "checkov.json")
    conftest = safe_read_json(REPORT_DIR / "conftest.json")

    kubescore_critical, kubescore_warning = parse_kubescore(kubescore_raw)
    kubesec_findings = parse_kubesec(kubesec_raw)
    checkov_failed = parse_checkov(checkov_raw)

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "yamllint_warnings": len(yamllint),
        "kubeconform_invalid": kubeconform.get("summary", {}).get("invalid", 0) if isinstance(kubeconform, dict) else 0,
        "kube_score_critical": len(kubescore_critical),
        "kube_score_warning": len(kubescore_warning),
        "kubesec_findings": len(kubesec_findings),
        "checkov_failed": len(checkov_failed),
        "conftest_violations": len(conftest) if isinstance(conftest, list) else 0
    }

    report = {
        "summary": summary,
        "yamllint": yamllint,
        "kubeconform": kubeconform,
        "kube-score": kubescore_raw,
        "kubesec": kubesec_findings,
        "checkov": checkov_failed,
        "conftest": conftest
    }

    OUTPUT_JSON.write_text(json.dumps(report, indent=2))
    OUTPUT_HTML.write_text(generate_html(summary, report))

    print("Security reports generated successfully")
    print(" - reports/security-report.json")
    print(" - reports/security-report.html")


def generate_html(summary, data):
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

<h1>Kubernetes DevSecOps Security Report</h1>
<p><b>Generated:</b> {summary["generated_at"]}</p>

<h2>Summary</h2>
<div class="card summary">
  <span class="warn">yamllint warnings: {summary["yamllint_warnings"]}</span>
  <span class="good">kubeconform invalid: {summary["kubeconform_invalid"]}</span>
  <span class="bad">kube-score critical: {summary["kube_score_critical"]}</span>
  <span class="warn">kube-score warnings: {summary["kube_score_warning"]}</span>
  <span class="warn">kubesec findings: {summary["kubesec_findings"]}</span>
  <span class="bad">checkov failed: {summary["checkov_failed"]}</span>
  <span class="good">conftest violations: {summary["conftest_violations"]}</span>
</div>

<h2>Detailed Findings</h2>
"""

    for tool, content in data.items():
        html += f"""
<div class='card'>
<h3>{tool}</h3>
<pre>{json.dumps(content, indent=2)}</pre>
</div>
"""

    html += "</body></html>"
    return html


if __name__ == "__main__":
    main()
