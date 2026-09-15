# Eleven online validators, the same invoice, one day

Raw data for the comparison published at
<https://normapi.de/studie/online-validatoren> (English:
<https://normapi.de/en/study/online-validators>).

On 15 September 2026, files from the official KoSIT test suite were put through
eleven freely accessible e-invoice validation sites. This directory holds the
files, the reference runs, the scripts that built them, and every observation.

## Disclosure

Published by NormAPI, which operates a validator of its own. NormAPI was
deliberately left out of the comparison. Read the numbers with that in mind — and
then check them, which is what everything here is for.

## What is in here

| Path | What it is |
|---|---|
| `corpus/` | The nine test files. Each differs from the unmodified instance in exactly one respect. |
| `reference-kosit.json` | The control: the official KoSIT validator at rule set `v2026-08-31`, over the whole corpus. |
| `reference-itb.json` | The European Commission's ITB validator over the whole corpus — EN 16931, not the German CIUS. |
| `results.json` | What each of the eleven tools reported. |
| `build_corpus.py` | Builds `corpus/` from the upstream test suite. |
| `baseline.py` | Checks each file triggers precisely the rule it was built for. |
| `make-results.py` | Writes `results.json` from the recorded observations. |

## Method

Every file comes from `itplr-kosit/xrechnung-testsuite` release `v2026-08-31`
(Apache-2.0), published the same day as the rule set. No customer data is
involved and every file can be rebuilt.

Each mutation changes exactly one thing, and `baseline.py` checks against the
official KoSIT validator that it triggers precisely the intended rule and nothing
else. **Two drafts failed that check and were replaced** — both were rejected by
the XSD before Schematron ever ran, so they would have tested nothing:

- an issue date written `04.04.2016`, which fails `cvc-datatype-valid`
- an `AdditionalDocumentReference` inserted after `AccountingSupplierParty`,
  which violates the UBL element order (`cvc-complex-type.2.4.a`)

If you build your own corpus, those are the two traps.

## How to read `results.json`

Every `verdict` is quoted from the tool's own output, in the tool's own language.
Every `codes` array holds only rule codes the tool itself named. An empty array
means it named none, not that there were none.

`classification` says what can fairly be concluded, and is not a score:

- `older-ruleset` — reads UBL, applies the German rules, missing rules added on
  2 September 2026
- `no-ubl` — does not process XRechnung in the UBL syntax
- `matches` — same outcome as the reference run, on everything tested
- `different-scope` — validates another standard on purpose; silence on `BR-DE-*`
  is correct, not stale
- `untested` — could not be tested. Not a failure.

The distinction that matters most, and the one most prose on this subject misses:
**scope and staleness look identical from the outside unless you test for both.**
A tool silent on `BR-DE-*` because it validates EN 16931 is right. A tool silent
because its rule set is from August is not. `B1` and `C1` together separate them.

Where a tool shows only a pass/fail verdict with no list of findings, the absence
of a warning proves nothing, and the entry says so with `inconclusive`.

## Limits

A snapshot of one day. Tools get updated; a finding here may be out of date by the
time you read it. Three files were tested, not a feature set — a tool that misses
`BR-TMP-6` may be faultless at everything else. The Serviceportal
Baden-Württemberg validator is not reachable from outside Germany and was measured
over a German connection.

## Corrections

If something here is wrong, open an issue or write to `dmytro@normapi.de`. It will
be corrected with a date, here and on the page. Every operator named in
`results.json` was emailed a copy of their own entry on 15 September 2026, before
anyone had to find it themselves.

## Licence

The files under `corpus/` derive from the KoSIT test suite and remain under
**Apache-2.0**; see the upstream repository for the notice. Everything else in
this directory — the result data, the scripts and this README — is **CC BY 4.0**.
Attribution: NormAPI, normapi.de.
