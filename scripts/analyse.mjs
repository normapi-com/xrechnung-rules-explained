/**
 * What falls out of compiling the XRechnung rule set.
 *
 * Reads the four XSLT files a validator-configuration release ships and reports
 * three things the published rule lists do not:
 *
 *   1. rules whose assertion is `true()` — they cannot fail, ever
 *   2. distinct rule codes that compile to the same check on the same context —
 *      one mistake, two error codes
 *   3. how the codes are split across the EN 16931 and XRechnung layers
 *
 * The comparison in (2) has to include the context. Comparing only the test
 * expression reports around ninety codes as duplicates, and most of those are
 * the same expression evaluated somewhere else entirely: BR-02 and BR-21 both
 * test `normalize-space(cbc:ID) != ''`, one on the invoice and one on a line.
 *
 * Usage:  node scripts/analyse.mjs <path-to-unpacked-configuration> [out.json]
 */
import { readFileSync, existsSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'

const root = process.argv[2]
const out = process.argv[3]
if (root === undefined) {
  console.error('usage: node scripts/analyse.mjs <configuration-dir> [out.json]')
  process.exit(2)
}

const LAYERS = {
  'EN16931-UBL': 'EN16931-UBL-validation.xsl',
  'EN16931-CII': 'EN16931-CII-validation.xsl',
  'XRechnung-UBL': 'resources/xrechnung/3.0.2/xsl/XRechnung-UBL-validation.xsl',
  'XRechnung-CII': 'resources/xrechnung/3.0.2/xsl/XRechnung-CII-validation.xsl',
}

const squash = (s) => s.replace(/\s+/g, ' ').trim()

/** Every assertion in one stylesheet, with the context it is evaluated on. */
function assertionsIn(xsl) {
  const templates = [...xsl.matchAll(/<xsl:template match="([^"]+)"/g)].map((m) => [
    m.index,
    squash(m[1]),
  ])
  const found = []
  const assertion =
    /id="([A-Za-z0-9-]+)">\s*<xsl:attribute name="test">([\s\S]*?)<\/xsl:attribute>/g
  for (const m of xsl.matchAll(assertion)) {
    let context = null
    for (const [at, match] of templates) {
      if (at < m.index) context = match
      else break
    }
    found.push({ code: m[1], test: squash(m[2]), context })
  }
  return found
}

const report = { rulesetDirectory: root, layers: {}, neverFires: [], sameCheck: [] }
const neverFires = new Set()
const fires = new Set()

for (const [layer, relative] of Object.entries(LAYERS)) {
  const path = join(root, relative)
  if (!existsSync(path)) {
    console.error(`missing: ${path}`)
    continue
  }
  const found = assertionsIn(readFileSync(path, 'utf8'))
  const codes = new Set(found.map((a) => a.code))

  const byCheck = new Map()
  for (const a of found) {
    if (a.test === 'true()') neverFires.add(a.code)
    else fires.add(a.code)
    // `false()` is the opposite of a no-op: the context matches only the broken
    // case, so the assertion fires whenever it is reached. Not a duplicate either.
    if (a.test === 'true()' || a.test === 'false()') continue
    const key = `${a.context} ${a.test}`
    if (!byCheck.has(key)) {
      byCheck.set(key, { context: a.context, test: a.test, codes: new Set() })
    }
    byCheck.get(key).codes.add(a.code)
  }

  const shared = [...byCheck.values()]
    .filter((c) => c.codes.size > 1)
    .map((c) => ({ layer, codes: [...c.codes].sort(), context: c.context, test: c.test }))
    .sort((a, b) => b.codes.length - a.codes.length)

  report.layers[layer] = {
    assertions: found.length,
    distinctCodes: codes.size,
    sharedChecks: shared.length,
    codesInSharedChecks: shared.reduce((n, c) => n + c.codes.length, 0),
  }
  report.sameCheck.push(...shared)
}

report.neverFires = [...neverFires].filter((c) => !fires.has(c)).sort()

// The committed JSON carries codes, layers and counts — facts about the rule
// set — but not the XPath the assertions are written in. That is KoSIT's
// artefact under KoSIT's terms; re-run this script to see it in full on stdout.
const publishable = {
  ...report,
  sameCheck: report.sameCheck.map(({ layer, codes }) => ({ layer, codes })),
}
if (out !== undefined) {
  writeFileSync(out, JSON.stringify(publishable, null, 2) + '\n')
}

console.log(`rule set: ${root}`)
console.log('')
for (const [layer, s] of Object.entries(report.layers)) {
  console.log(
    `  ${layer.padEnd(15)} ${String(s.distinctCodes).padStart(3)} codes` +
      `  ${String(s.sharedChecks).padStart(2)} shared checks covering ${s.codesInSharedChecks} codes`,
  )
}
console.log('')
console.log(`  never fires (test is true()): ${report.neverFires.join(' ') || 'none'}`)
console.log(`  groups of codes sharing one check: ${report.sameCheck.length}`)
for (const g of report.sameCheck) {
  console.log(`     [${g.layer}] ${g.codes.join(' = ')}`)
}
if (out !== undefined) {
  console.log('')
  console.log(`written to ${out}`)
}
