import json
from pathlib import Path
from datetime import datetime

REPORT_DIR = Path("reports")

def read_json(name):
    path = REPORT_DIR / name
    if path.exists():
        return json.loads(path.read_text())
    return {}

def severity_summary():
    return {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0
    }

summary = {
    "generated_at": datetime.utcnow().isoformat() + "Z",
    "tools": {},
    "severity": severity_summary()
}

# kube-score
kube_score = read_json("kube-score.json")
summary["tools"]["kube-score"] = kube_score

# kubeconform
kubeconform = read_json("kubeconform.json")
summary["tools"]["kubeconform"] = kubeconform

# kubesec
kubesec = read_json("kubesec.json")
summary["tools"]["kubesec"] = kubesec

# checkov
checkov = read_json("checkov.json")
summary["tools"]["checkov"] = checkov

# conftest
conftest = read_json("conftest.json")
summary["tools"]["conftest"] = conftest

Path("security-report.json").write_text(json.dumps(summary, indent=2))

html = f"""
<html>
<head>
<title>Kubernetes DevSecOps Security Report</title>
<style>
body {{ font-family: Arial; background:#f9fafc; padding:40px }}
h1 {{ color:#1f4fd8 }}
h2 {{ margin-top:40px }}
pre {{ background:#111; color:#00ff9c; padding:15px; overflow:auto }}
.card {{ background:white; padding:20px; border-radius:8px; margin-bottom:20px; box-shadow:0 2px 5px rgba(0,0,0,0.05) }}
</style>
</head>
<body>

<h1>🔐 Kubernetes DevSecOps Security Report</h1>

<div class="card">
<b>Generated:</b> {summary["generated_at"]}<br>
<b>Project:</b> Kubernetes Security Validation Pipeline
</div>
"""

for tool, data in summary["tools"].items():
    html += f"""
    <div class="card">
      <h2>{tool.upper()}</h2>
      <pre>{json.dumps(data, indent=2)}</pre>
    </div>
    """

html += "</body></html>"

Path("security-report.html").write_text(html)

print("Security report generated:")
print(" - security-report.json")
print(" - security-report.html")
