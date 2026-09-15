#!/usr/bin/env python3
"""Build the study corpus: official conformance instances plus targeted mutations.

Every file here derives from the KoSIT test suite v2026-08-31, which is published
under Apache-2.0 and matches the rule set released on 2 September 2026. Nothing is
customer data, so anybody can re-run this and check the result.

Each mutation is designed to isolate ONE discriminator. The point of the study is
not "does validator X work" but "is validator X on the current rule set", and the
only way to see that from the outside is a file whose verdict changed between
versions.
"""

import pathlib
import re
import shutil

SRC = pathlib.Path("instances/standard")
OUT = pathlib.Path("corpus")
UBL = SRC / "01.01a-INVOICE_ubl.xml"
CII = SRC / "01.01a-INVOICE_uncefact.xml"

OUT.mkdir(exist_ok=True)
cases: list[tuple[str, str, str]] = []


def emit(name: str, text: str, expect: str) -> None:
    (OUT / name).write_text(text, encoding="utf-8")
    cases.append((name, expect, ""))


ubl = UBL.read_text(encoding="utf-8")
cii = CII.read_text(encoding="utf-8")

# A — clean baselines. Every validator should accept these. A rejection here is a
# false positive and the most damaging kind of bug, because the invoice is correct.
emit("A1-clean-ubl.xml", ubl, "accept")
emit("A2-clean-cii.xml", cii, "accept")

# B — the version discriminators. These are the six rules that arrived with
# v2026-08-31. A validator still on v2026-01-31 stays silent on all of them.

# B1: BR-TMP-6 — UBL dates must be YYYY-MM-DD.
#
# A German-format date ("04.04.2016") is the obvious mutation and it is the WRONG
# one: cbc:IssueDate is xs:date, so the file dies at the schema step and Schematron
# never runs. The rule is only reachable with a date that is schema-valid but not
# plain YYYY-MM-DD — xs:date permits a timezone offset, so that is the gap the rule
# exists to close, and it is exactly what a careless mapping emits.
emit("B1-ubl-date-format.xml",
     ubl.replace("<cbc:IssueDate>2016-04-04</cbc:IssueDate>",
                 "<cbc:IssueDate>2016-04-04+02:00</cbc:IssueDate>"),
     "BR-TMP-6")

# B2: BR-TMP-7 — CII dates need format="102". 610 is the other common code and is
# exactly what a mis-configured mapping emits.
emit("B2-cii-date-format.xml", cii.replace('format="102"', 'format="610"', 1), "BR-TMP-7")

# B3: BR-TMP-2 — BT-124 must be an absolute URL. This one was RAISED from warning
# to error on 2 September, so it separates validators three ways: silent, warning,
# or error.
#
# UBL enforces element order, so this block has to go BEFORE
# cac:AccountingSupplierParty. Appending it after gives cvc-complex-type.2.4.a and
# the file dies at the schema step, same trap as B1.
ubl_doc = re.sub(
    r"(<cac:AccountingSupplierParty>)",
    """<cac:AdditionalDocumentReference>
    <cbc:ID>DOC-1</cbc:ID>
    <cbc:DocumentDescription>Stundennachweis</cbc:DocumentDescription>
    <cac:Attachment>
      <cac:ExternalReference>
        <cbc:URI>./anhang/stundennachweis.pdf</cbc:URI>
      </cac:ExternalReference>
    </cac:Attachment>
  </cac:AdditionalDocumentReference>\\1""",
    ubl, count=1)
emit("B3-ubl-relative-uri.xml", ubl_doc, "BR-TMP-2")

# C — classic failures. Every validator, current or stale, should catch these.
# Anyone who misses one has a real gap that has nothing to do with versions.

# C1: BR-DE-15 — the Leitweg-ID. The single most common rejection in Germany.
emit("C1-ubl-no-buyer-reference.xml",
     ubl.replace("<cbc:BuyerReference>04011000-12345-03</cbc:BuyerReference>", ""),
     "BR-DE-15")

# C2: arithmetic. Schema-valid, so validation reaches Schematron and the failure is
# a business rule rather than a parse error.
m = re.search(r"<cbc:TaxInclusiveAmount currencyID=\"EUR\">([\d.]+)</cbc:TaxInclusiveAmount>", ubl)
if m:
    wrong = f"{float(m.group(1)) + 100:.2f}"
    emit("C2-ubl-wrong-total.xml",
         ubl.replace(m.group(0), m.group(0).replace(m.group(1), wrong)),
         "BR-CO-*")

# C3: BR-CL-23 — unit code outside UN/ECE Rec 20. orgaMAX documents this one, so it
# is a fair bet it is common in the wild.
emit("C3-ubl-bad-unit-code.xml", ubl.replace('unitCode="XPP"', 'unitCode="STÜCK"'), "BR-CL-23")

# D — malformed, to check the schema step is reached at all.
emit("D1-ubl-broken-xml.xml", ubl.replace("</cbc:IssueDate>", "", 1), "not well-formed")

print(f"{len(cases)} files in {OUT}/")
for name, expect, _ in cases:
    print(f"  {name:34} expect: {expect}")
