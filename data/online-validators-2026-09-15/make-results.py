#!/usr/bin/env python3
"""Write results.json from the hand-recorded observations of the 15 Sept 2026 run.

The observations are typed out here rather than scraped, because that is what they
are: somebody read a web page and wrote down what it said. Keeping them in one
literal makes the provenance obvious and makes a correction a one-line diff.

Every `verdict` is quoted from the tool's own output, in the tool's own language.
Nothing here is a judgement about product quality — see README.md.
"""

import json
import pathlib

RUN_DATE = "2026-09-15"
RULESET = "v2026-08-31"

# Classification is about what can fairly be said, not about a score.
#   older-ruleset   reads UBL, applies the German rules, missing rules added 2026-09-02
#   no-ubl          does not process XRechnung in the UBL syntax at all
#   matches         same outcome as the reference run, on everything tested
#   different-scope validates another standard on purpose; silence on BR-DE-* is correct
#   untested        could not be tested; never to be presented as a failure

TOOLS = [
    {
        "name": "Serviceportal Baden-Württemberg",
        "url": "https://erechnungsvalidator.service-bw.de/",
        "operator": "Land Baden-Württemberg / BITBW",
        "statedVersion": "5.0.10",
        "classification": "older-ruleset",
        "results": {
            "C1-ubl-no-buyer-reference.xml": {
                "verdict": "Fehler: 1, Warnungen: 0 — „Es wird empfohlen das Dokument zurückzuweisen.“",
                "codes": [],
            },
            "B1-ubl-date-format.xml": {
                "verdict": "Fehler: –, Warnungen: – — „Es wird empfohlen das Dokument anzunehmen und weiter zu verarbeiten.“",
                "codes": [],
                "reportTimestamp": "2026-09-15T08:56:54",
                "recognisedIssueDate": "2016-04-04+02:00",
            },
        },
        "note": (
            "Reads UBL correctly — it echoes the changed date back as 2016-04-04+02:00 — and "
            "catches the missing Leitweg-ID. For B1 it reports no warnings, where the reference "
            "run reports BR-TMP-6. The same two counters read \"1\" and \"0\" for C1, so they are "
            "populated when there is something to report. B1 was re-run and re-confirmed on "
            "15 September; the timestamp above is from the tool's own report."
        ),
    },
    {
        "name": "invoice-portal.de",
        "url": "https://validator.invoice-portal.de/",
        "statedVersion": "XRechnung 3.0.2",
        "classification": "older-ruleset",
        "results": {
            "C1-ubl-no-buyer-reference.xml": {
                "verdict": "XSD 0 · CEN-EN16931-UBL 0 · XRechnung 3.0.2: 2",
                "codes": ["BR-DE-15", "BR-DE-TMP-32"],
            },
            "B1-ubl-date-format.xml": {
                "verdict": "XRechnung 3.0.2: 1",
                "codes": ["BR-DE-TMP-32"],
            },
        },
        "note": (
            "Names every check step with its artefact. C1 matches the reference run code for "
            "code. On B1, BR-TMP-6 is absent while BR-DE-TMP-32 is still shown at information "
            "level."
        ),
    },
    {
        "name": "portinvoice",
        "url": "https://www.portinvoice.com/",
        "operator": "OXSEED logistics GmbH",
        "statedVersion": "2.26.0",
        "classification": "older-ruleset",
        "results": {
            "C1-ubl-no-buyer-reference.xml": {
                "verdict": "XRechnung 3.0 STANDARD — 11 Regeln bestanden, 2 gescheitert",
                "codes": ["BR-DE-15", "BR-DE-TMP-32"],
            },
            "B1-ubl-date-format.xml": {
                "verdict": "XRechnung 3.0 STANDARD — „Format-Validierung war erfolgreich“, 1 gescheitert",
                "codes": ["BR-DE-TMP-32"],
            },
        },
        "note": (
            "Names the detected profile URN and the engine version. BR-DE-15 disappears "
            "correctly once the Leitweg-ID is restored. BR-TMP-6 is not reported for B1; "
            "BR-DE-TMP-32 is, at information level."
        ),
    },
    {
        "name": "inoxision (belegpostfach)",
        "url": "https://validator.belegpostfach.de/",
        "operator": "inoxision GmbH",
        "classification": "matches",
        "results": {
            "C1-ubl-no-buyer-reference.xml": {
                "verdict": "Ungültig — Profil: X-Rechnung 3.0",
                "codes": [],
            },
            "B1-ubl-date-format.xml": {
                "verdict": "Gültig — Profil: X-Rechnung 3.0",
                "codes": [],
            },
        },
        "note": (
            "Detects the XRechnung profile and reaches the same outcome as the reference run "
            "on both files. Quota: ten checks per day."
        ),
    },
    {
        "name": "kostenlose-erechnung.de",
        "url": "https://kostenlose-erechnung.de/auslesen/",
        "operator": "Bär Solutions",
        "classification": "matches",
        "results": {
            "C1-ubl-no-buyer-reference.xml": {
                "verdict": "Prüfung nicht bestanden — XRechnung 3.0",
                "codes": ["BR-DE-15"],
            },
            "B1-ubl-date-format.xml": {
                "verdict": "Prüfung bestanden — XRechnung 3.0",
                "codes": [],
                "inconclusive": "BR-TMP-6",
            },
        },
        "note": (
            "Reads UBL, catches the missing Leitweg-ID and names the rule code. Inconclusive on "
            "BR-TMP-6: the interface shows a pass/fail verdict rather than a list of findings, "
            "so silence is not evidence either way."
        ),
    },
    {
        "name": "erechnungs-validator.de (winball)",
        "url": "https://erechnungs-validator.de/e-rechnung-validieren/",
        "operator": "PG Consulting",
        "classification": "no-ubl",
        "results": {
            "A1-clean-ubl.xml": {
                "verdict": "„weder Fehler noch Warnungen … konform“",
                "codes": [],
            },
            "B1-ubl-date-format.xml": {
                "verdict": "„1 Fehler / 0 Warnungen … nicht konform“ — Schritt: CII-XSD",
                "codes": ["cvc-complex-type.2.4.b"],
            },
            "C1-ubl-no-buyer-reference.xml": {
                "verdict": "„weder Fehler noch Warnungen … konform“ — empfohlen anzunehmen",
                "codes": [],
            },
        },
        "note": (
            "Its own report names the detected document type as \"EN16931 (CII)\", though the "
            "file is UBL and declares the German CIUS in cbc:CustomizationID. It is checked "
            "against the CII schema accordingly; the single error on B1 concerns "
            "ram:IssueDateTime, a CII element that does not appear in the submitted file. For "
            "C1 no Schematron step appears and the word \"XRechnung\" is absent from the report "
            "— an invoice with no Leitweg-ID is recommended for acceptance."
        ),
    },
    {
        "name": "e-rechnung.tools",
        "url": "https://www.e-rechnung.tools/validieren",
        "classification": "no-ubl",
        "results": {
            "C1-ubl-no-buyer-reference.xml": {
                "verdict": "„Kein CrossIndustryInvoice-Element gefunden.“",
                "codes": [],
            },
        },
        "note": (
            "The page advertises \"XRechnung XML oder ZUGFeRD PDF\". Given an XRechnung in UBL "
            "it answers that it found no CII element, quoting the submitted file's UBL root "
            "element back."
        ),
    },
    {
        "name": "easyfirma.net",
        "url": "https://easyfirma.net/e-rechnung/validieren",
        "classification": "no-ubl",
        "results": {
            "A1-clean-ubl.xml": {
                "verdict": "„Kein E-Rechnungs-Profil erkannt · Weder ZUGFeRD/Factur-X noch XRechnung“",
                "codes": [],
            },
            "C1-ubl-no-buyer-reference.xml": {
                "verdict": "„Kein E-Rechnungs-Profil erkannt · Weder ZUGFeRD/Factur-X noch XRechnung“",
                "codes": [],
            },
        },
        "note": (
            "This applies to A1 as well — the unmodified conformance instance from the official "
            "KoSIT test suite. Nothing about that file was altered."
        ),
    },
    {
        "name": "ITB (European Commission)",
        "url": "https://www.itb.ec.europa.eu/invoice/upload",
        "operator": "DG DIGIT",
        "classification": "different-scope",
        "results": None,  # filled from reference-itb.json: the whole corpus was run
        "note": (
            "Validates EN 16931, not the German CIUS. Not reporting BR-DE-15 is correct here, "
            "not a defect. The practical consequence: \"it passed the EU validator\" says "
            "nothing about a German B2G invoice."
        ),
    },
    {
        "name": "Truugo",
        "url": "https://app.truugo.com/qualityassurance/",
        "operator": "Studyo Ltd",
        "classification": "different-scope",
        "results": {},
        "note": (
            "Within what was tested, the profile catalogue contains no XRechnung and no "
            "EN 16931 profile; the public demo profiles are EDIFACT INVOIC, SAP XML ZORDERS05, "
            "UBL 2.0 Invoice and EDIFACT DESADV. Validating against \"UBL 2.0 Invoice\" would be "
            "a schema check and not an XRechnung result, so it was not run."
        ),
    },
    {
        "name": "e-rechnungs-checker.de",
        "url": "https://www.e-rechnungs-checker.de/",
        "classification": "untested",
        "results": {},
        "note": (
            "Could not be tested: the form only processes uploads from a genuine user "
            "interaction. That is a limit of the method, not a statement about the tool."
        ),
    },
]

FILES = {
    "A1-clean-ubl.xml": "Unmodified conformance instance from the KoSIT test suite, UBL.",
    "A2-clean-cii.xml": "Unmodified conformance instance, CII.",
    "B1-ubl-date-format.xml": "A1 with a timezone offset on the issue date: 2016-04-04+02:00. Schema-valid; triggers BR-TMP-6 (warning) since v2026-08-31.",
    "B2-cii-date-format.xml": "A2 with date format 610. Triggers BR-TMP-7 (warning) and BR-03.",
    "B3-ubl-relative-uri.xml": "A1 with a relative URI in BT-124. Triggers BR-TMP-2 (error).",
    "C1-ubl-no-buyer-reference.xml": "A1 without BT-10 \"Buyer reference\", the Leitweg-ID. Violates BR-DE-15.",
    "C2-ubl-wrong-total.xml": "A1 with an inconsistent total. Triggers BR-CO-15 and BR-CO-16.",
    "C3-ubl-bad-unit-code.xml": "A1 with an invalid unit code. Triggers BR-CL-23.",
    "D1-ubl-broken-xml.xml": "A1, not well-formed. Never reaches any rule.",
}

here = pathlib.Path(__file__).parent
itb = json.loads((here / "reference-itb.json").read_text(encoding="utf-8"))

for tool in TOOLS:
    if tool["results"] is None:
        tool["results"] = {
            name: {"verdict": r["result"], "codes": r["codes"]} for name, r in itb.items()
        }

payload = {
    "runDate": RUN_DATE,
    "ruleset": RULESET,
    "referenceRun": "reference-kosit.json",
    "corpusSource": {
        "name": "itplr-kosit/xrechnung-testsuite",
        "release": "v2026-08-31",
        "licence": "Apache-2.0",
        "note": "Each file differs from the unmodified instance in exactly one respect, and was checked against the official KoSIT validator first to confirm it triggers precisely the intended rule.",
    },
    "disclosure": "Published by NormAPI (normapi.de), which operates a validator of its own. NormAPI was deliberately left out of the comparison.",
    "classifications": {
        "older-ruleset": "Reads UBL, applies the German rules, missing rules added 2026-09-02.",
        "no-ubl": "Does not process XRechnung in the UBL syntax.",
        "matches": "Same outcome as the reference run, on everything tested.",
        "different-scope": "Validates another standard on purpose; silence on BR-DE-* is correct.",
        "untested": "Could not be tested. Not a failure.",
    },
    "files": FILES,
    "tools": TOOLS,
}

out = here / "results.json"
out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"wrote {out} — {len(TOOLS)} tools, {len(FILES)} files")
