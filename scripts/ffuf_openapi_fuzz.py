import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml


def _safe_name(s: str) -> str:
    s = s.strip()
    s = re.sub(r"[^a-zA-Z0-9_.-]+", "_", s)
    return s[:180] if len(s) > 180 else s


def _collect_paths(openapi: dict) -> list[str]:
    paths = openapi.get("paths") or {}
    out: list[str] = []
    for p in paths.keys():
        if not isinstance(p, str):
            continue
        # replace templated params with a placeholder
        p2 = re.sub(r"\{[^}]+\}", "FUZZ", p)
        out.append(p2)
    return sorted(set(out))


def _collect_params(openapi: dict) -> list[str]:
    out: set[str] = set()
    paths = openapi.get("paths") or {}
    for _, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue
        # parameters at path level
        for p in path_item.get("parameters") or []:
            if isinstance(p, dict) and isinstance(p.get("name"), str):
                out.add(p["name"])
        # parameters at operation level
        for _, op in path_item.items():
            if not isinstance(op, dict):
                continue
            for p in op.get("parameters") or []:
                if isinstance(p, dict) and isinstance(p.get("name"), str):
                    out.add(p["name"])
    return sorted(out)


def _write_wordlist(items: list[str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for x in items:
            f.write(x)
            f.write("\n")


def _run(cmd: list[str]) -> int:
    p = subprocess.run(cmd, stdout=sys.stdout, stderr=sys.stderr)
    return int(p.returncode)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--openapi", default="openapi.yaml")
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--out-dir", default="security-reports/ffuf")
    ap.add_argument("--auth-token", default=os.environ.get("JWT_TOKEN", ""))
    ap.add_argument("--header-wordlist", default="")
    args = ap.parse_args()

    openapi_path = Path(args.openapi)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    spec = yaml.safe_load(openapi_path.read_text(encoding="utf-8"))

    paths = _collect_paths(spec)
    params = _collect_params(spec)

    paths_wl = out_dir / "paths.txt"
    params_wl = out_dir / "params.txt"
    payloads_wl = out_dir / "payloads.txt"

    # Minimal payload set: safe defaults; user can extend later.
    payloads = [
        "'",
        '"',
        "<script>alert(1)</script>",
        "../../../../etc/passwd",
        "..%2f..%2f..%2fetc%2fpasswd",
        "${{7*7}}",
        "\\u0000",
        "%0d%0aX-Test: injected",
    ]

    _write_wordlist(paths, paths_wl)
    _write_wordlist(params, params_wl)
    _write_wordlist(payloads, payloads_wl)

    base_url = args.base_url.rstrip("/")

    common_args = [
        "ffuf",
        "-ac",
        "-t",
        "20",
        "-timeout",
        "10",
        "-s",
    ]

    headers: list[str] = []
    if args.auth_token:
        headers += ["-H", f"Authorization: Bearer {args.auth_token}"]

    # 1) Path fuzzing (uses openapi-derived paths)
    path_out = out_dir / "ffuf-paths.json"
    cmd1 = (
        common_args
        + ["-w", str(paths_wl), "-u", f"{base_url}/FUZZ", "-of", "json", "-o", str(path_out)]
        + headers
    )
    rc1 = _run(cmd1)

    # 2) Query parameter name fuzzing (try adding FUZZ param name with benign value)
    # e.g. /api/resource?FUZZ=1
    qpname_out = out_dir / "ffuf-query-param-names.json"
    cmd2 = (
        common_args
        + ["-w", str(params_wl), "-u", f"{base_url}/?FUZZ=1", "-of", "json", "-o", str(qpname_out)]
        + headers
    )
    rc2 = _run(cmd2)

    # 3) Query parameter value fuzzing for a small subset of parameters
    # Runs once per param to keep it simple.
    qpv_out_dir = out_dir / "qp-values"
    qpv_out_dir.mkdir(parents=True, exist_ok=True)

    # only run on first N params to keep runtime bounded in CI
    max_params = 25
    rc3 = 0
    for name in params[:max_params]:
        out_file = qpv_out_dir / f"ffuf-qpv-{_safe_name(name)}.json"
        cmd = (
            common_args
            + [
                "-w",
                str(payloads_wl),
                "-u",
                f"{base_url}/?{name}=FUZZ",
                "-of",
                "json",
                "-o",
                str(out_file),
            ]
            + headers
        )
        rci = _run(cmd)
        if rci != 0 and rc3 == 0:
            rc3 = rci

    # Write summary metadata
    meta = {
        "base_url": base_url,
        "openapi": str(openapi_path),
        "paths": len(paths),
        "params": len(params),
        "max_params_qpv": max_params,
        "returncodes": {"paths": rc1, "query_param_names": rc2, "query_param_values": rc3},
    }
    (out_dir / "run-meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    # Do not fail pipeline by default; analysis/gating can be added later.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
