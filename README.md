# XRechnung rules, explained

Plain-language explanations of 132 EN 16931, XRechnung and Peppol validation
rules — in German and English, each with a wrong and a right XML fragment — plus
a script that reports what falls out of compiling the official rule set.

The rule set itself is not vendored here. `scripts/fetch-ruleset.sh` downloads a
release from [KoSIT](https://github.com/itplr-kosit/validator-configuration-xrechnung)
and verifies its checksum, so the analysis describes the release you care about
rather than a copy that went stale.

---

## What compiling the rule set turns up

Run it yourself: `scripts/fetch-ruleset.sh && node scripts/analyse.mjs ruleset`.
The numbers below are for `v2026-01-31` (XRechnung 3.0.2).

### Four rules can never fail

`BR-CO-05`, `BR-CO-06`, `BR-CO-07` and `BR-CO-08` compile to an assertion whose
test is literally `true()`.

They are the rules requiring an allowance or charge *reason code* to agree with
its *free text* — and whether a code and a sentence mean the same thing is not
something Schematron can decide. So the rules exist normatively, appear in every
conformance list, and no validator built on this rule set will ever emit one.

If you are writing test cases against them, you are writing test cases for
nothing.

### Thirteen groups of codes are the same check under different names

One mistake, two error codes. The pairs that matter most in practice:

| Codes | Layer | What it is |
|---|---|---|
| `BR-33` = `BR-CO-21` | UBL + CII | document allowance needs a reason |
| `BR-38` = `BR-CO-22` | UBL + CII | document charge needs a reason |
| `BR-42` = `BR-CO-23` | UBL + CII | line allowance needs a reason |
| `BR-44` = `BR-CO-24` | UBL + CII | line charge needs a reason |
| `BR-50` = `BR-61` | CII only | credit transfer needs an account |
| `BR-O-11` = `BR-O-12` | CII only | not-subject-to-VAT: other categories |
| `BR-O-13` = `BR-O-14` | CII only | not-subject-to-VAT: document allowances and charges |
| `CII-SR-184` = `CII-SR-193` | CII only | syntax binding |
| `CII-SR-333` = `CII-SR-334` | CII only | syntax binding |

`BR-50` and `BR-61` are the interesting one: in **UBL** they have different
contexts — `BR-50` only fires once a `PayeeFinancialAccount` element exists, so
omitting the group entirely reports `BR-61` alone — while in **CII** they
compile to one check and always report together. A rule whose behaviour depends
on the syntax is exactly the kind of thing that costs somebody an afternoon.

**The method matters here.** Comparing only the test expression reports about
ninety codes as duplicates, and most of them are not: `BR-02` and `BR-21` both
test `normalize-space(cbc:ID) != ''`, but one runs on the invoice and the other
on a line. The comparison has to include the context the assertion is evaluated
on. `analyse.mjs` does; a grep does not.

### The XRechnung layers are clean

| Layer | Assertion ids | Groups sharing one check |
|---|---|---|
| EN16931-UBL | 979 | 4 |
| EN16931-CII | 779 | 9 |
| XRechnung-UBL | 76 | 0 |
| XRechnung-CII | 71 | 0 |

Every duplicate and every no-op is in the European layer. The German CIUS on top
of it has neither. Note that the assertion-id counts include the `UBL-CR-*` and
`CII-SR-*` syntax-binding rules, which is why they are far larger than the ~300
business rules people usually mean by "the rule set".

---

## The reference

`data/explanations.json` — 132 rules, each with `meaning`, `cause` and `fix` in
German and English.

The rule text tells you *what* is required. It does not tell you why your
invoice broke it, which is the only thing you want to know at the moment it
does. `cause` is the mapping habit that actually produces the error — an address
kept as free text, a boolean serialised as `1`, a total computed for display and
never written out.

`data/fragments.json` — the same 132 rules, each with a `wrong` and a `right`
XML fragment. UBL where a rule applies to both syntaxes, CII where a rule exists
only there. Fragments, not documents: elements appear in the order the schema
requires them, with the surrounding context needed to place them and nothing
else.

Coverage is by family, and complete in four of them:

| Family | Explained | Can fire |
|---|---|---|
| `BR` (EN 16931 core) | 58 | 58 |
| `BR-DE` (XRechnung) | 31 | 31 |
| `PEPPOL-EN16931` | 23 | 23 |
| `BR-CO` (consistency) | 20 | 20 |
| **total** | **132** | **300** |

Not covered: the code-list family and the per-category VAT rules — roughly 160
rules of "this coded value must come from that list" and the same nine
requirements restated once per tax category. They are better served by one page
per family than by 160 near-identical entries, and that page is not written yet.

## Using it

```bash
scripts/fetch-ruleset.sh                 # downloads and checksums the rule set
node scripts/analyse.mjs ruleset         # the findings above, in full
node scripts/analyse.mjs ruleset out.json
```

The data files are plain JSON keyed by rule code:

```json
{
  "rules": {
    "BR-DE-15": {
      "de": { "meaning": "…", "cause": "…", "fix": "…" },
      "en": { "meaning": "…", "cause": "…", "fix": "…" }
    }
  }
}
```

The committed `data/findings.json` carries codes, layers and counts. It does not
carry the XPath the assertions are written in — that is KoSIT's artefact under
KoSIT's terms. Re-run the script to see it in full.

## Producing the codes in the first place

This reference explains codes; it does not produce them. To get a findings list
out of a document, any EN 16931 validator will do — the
[KoSIT validator](https://github.com/itplr-kosit/validator) with the
configuration above is the reference implementation, and
[mustangproject](https://github.com/ZUGFeRD/mustangproject),
[horstoeko/zugferd](https://github.com/horstoeko/zugferd) and
[ZUGFeRD-csharp](https://github.com/stephanstapel/ZUGFeRD-csharp) all validate
in their own ecosystems.

If you would rather not run a Java toolchain,
[`@normapi/client`](https://github.com/normapi-de/client) is a zero-dependency
TypeScript wrapper over a hosted one:

```bash
npm install @normapi/client
```

```ts
const result = await validate(await readFile('invoice.xml'))
for (const finding of result.findings) {
  console.log(finding.code) // look it up in data/explanations.json
}
```

## Eleven online validators, measured

`data/online-validators-2026-09-15/` holds the raw data behind
[a comparison of eleven free e-invoice validation sites](https://normapi.de/studie/online-validatoren),
run on 15 September 2026: the nine test files, the official KoSIT run used as the
control, the European Commission ITB run, and every observation recorded verbatim
from each tool's own report.

Three of the eleven do not process an XRechnung in the UBL syntax at all — one
fails on the unmodified conformance instance. Three more catch a missing
Leitweg-ID but report nothing for `BR-TMP-6`, added on 2 September 2026.

Published by a vendor that runs a validator of its own, and which is deliberately
absent from the comparison; the directory's README says so before it says anything
else. Every operator named was emailed their own entry on the day it went up.

## Where this comes from

These explanations are written and maintained for
[normapi.de/fehler](https://normapi.de/fehler), a commercial XRechnung
validation API. They are exported here because a reference nobody can read
offline, cite, or check into their own repository is less useful than one they
can — and because the findings above are worth more in the open than on a
marketing page.

The rendered pages carry the official rule text alongside each explanation. This
repository does not, so that the rule set stays the reader's own download.

## Licence

- `data/*.json` — [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Use
  them, translate them, build on them; credit normapi.de.
- `data/online-validators-2026-09-15/corpus/*` — derived from the KoSIT test
  suite and still **Apache-2.0**; that directory's README has the detail.
- `scripts/*` — MIT.
- The XRechnung validator configuration is **not** included and is not covered by
  either. It belongs to KoSIT; see
  [itplr-kosit/validator-configuration-xrechnung](https://github.com/itplr-kosit/validator-configuration-xrechnung)
  for its terms.

Corrections are welcome and land back on the site. If a `cause` does not match
what you actually hit, that is the most useful bug report this repository can
get.
