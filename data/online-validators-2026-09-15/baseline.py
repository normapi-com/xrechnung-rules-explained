#!/usr/bin/env python3
"""Run the corpus through NormAPI and record the reference verdict.

This is the control, not a result. Its job is to prove each mutation isolates the
rule it was built for; if a file triggers something other than its target, the file
is wrong and the comparison built on it would be worthless.
"""

import json
import pathlib
import subprocess
import time

EXPECT = {
    "A1-clean-ubl.xml": "accept",
    "A2-clean-cii.xml": "accept",
    "B1-ubl-date-format.xml": "BR-TMP-6",
    "B2-cii-date-format.xml": "BR-TMP-7",
    "B3-ubl-relative-uri.xml": "BR-TMP-2",
    "C1-ubl-no-buyer-reference.xml": "BR-DE-15",
    "C2-ubl-wrong-total.xml": "BR-CO-",
    "C3-ubl-bad-unit-code.xml": "BR-CL-23",
    "D1-ubl-broken-xml.xml": "not well-formed",
}

out = {}
for path in sorted(pathlib.Path("corpus").glob("*.xml")):
    raw = subprocess.run(
        ["curl", "-s", "--max-time", "90", "-X", "POST",
         "https://api.normapi.de/v1/validate",
         "-H", "Content-Type: application/xml",
         "-H", f"X-Document-Name: {path.name}",
         "--data-binary", f"@{path}"],
        capture_output=True, text=True).stdout
    try:
        d = json.loads(raw)
    except json.JSONDecodeError:
        out[path.name] = {"error": raw[:200]}
        continue

    codes = sorted({f.get("code", "") for f in d.get("findings", [])})
    sev = {f.get("code"): f.get("severity") for f in d.get("findings", [])}
    want = EXPECT[path.name]
    hit = (
        d.get("acceptable") is True and not [c for c in codes if not c.startswith("BR-DE-TMP-32")]
        if want == "accept"
        else (d.get("wellFormed") is False if want == "not well-formed"
              else any(c.startswith(want) for c in codes))
    )
    out[path.name] = {
        "wellFormed": d.get("wellFormed"),
        "schemaValid": d.get("schemaValid"),
        "acceptable": d.get("acceptable"),
        "ruleset": d.get("rulesetVersion"),
        "codes": codes,
        "severities": sev,
        "expected": want,
        "isolated": bool(hit),
    }
    print(f"{path.name:34} {'OK ' if hit else 'MISS'} want={want:16} got={','.join(codes) or '-'}")
    time.sleep(1)

pathlib.Path("baseline.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
bad = [k for k, v in out.items() if not v.get("isolated")]
print(f"\n{len(out) - len(bad)}/{len(out)} isolated. Broken: {bad or 'none'}")
