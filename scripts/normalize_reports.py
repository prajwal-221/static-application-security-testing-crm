import json
import os
from datetime import datetime

INPUT_DIR = "raw-reports"
OUTPUT_DIR = "normalized-reports"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def normalize_gitleaks(file_path, out_path):
    with open(file_path) as f:
        data = json.load(f)

    findings = []

    for item in data:
        findings.append({
            "title": f"Secret detected: {item.get('Description', 'Hardcoded Secret')}",
            "severity": "High",
            "description": item.get("Description", "Secret detected"),
            "file_path": item.get("File", ""),
            "line": item.get("StartLine", 0),
            "date": datetime.utcnow().isoformat() + "Z"
        })

    out = {
        "findings": findings
    }

    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)

    print(f"[+] Normalized Gitleaks → {out_path}")


def passthrough(file_path, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    os.system(f"cp {file_path} {out_path}")
    print(f"[=] Passthrough → {out_path}")


for root, _, files in os.walk(INPUT_DIR):
    for file in files:
        src = os.path.join(root, file)
        rel = os.path.relpath(src, INPUT_DIR)
        dst = os.path.join(OUTPUT_DIR, rel)

        os.makedirs(os.path.dirname(dst), exist_ok=True)

        if "gitleaks" in file.lower():
            normalize_gitleaks(src, dst)
        else:
            passthrough(src, dst)

print("\nNormalization completed successfully.")
