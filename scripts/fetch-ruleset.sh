#!/usr/bin/env bash
# Downloads and unpacks one official validator-configuration release.
#
# The rule set is not vendored here. It belongs to KoSIT, it is republished
# roughly twice a year, and pinning a copy in this repository would make the
# analysis quietly stale. Fetching it means the numbers you get are the numbers
# for the release you actually care about.
#
# The checksum is verified. A re-tagged or tampered release fails here rather
# than silently changing what the analysis reports.
#
# Usage:  scripts/fetch-ruleset.sh [target-dir]
set -euo pipefail

TAG="v2026-01-31"
FILE="xrechnung-3.0.2-validator-configuration-2026-01-31.zip"
SHA256="6a5a5911a421b25fbc423f62f93f894df7b236f5d73ca4f84bb222a945082704"
URL="https://github.com/itplr-kosit/validator-configuration-xrechnung/releases/download/${TAG}/${FILE}"

TARGET="${1:-ruleset}"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

echo "downloading ${FILE}"
curl -fsSL "$URL" -o "$WORK/$FILE"

echo "verifying checksum"
if command -v sha256sum >/dev/null 2>&1; then
  echo "${SHA256}  ${WORK}/${FILE}" | sha256sum -c -
else
  actual="$(shasum -a 256 "$WORK/$FILE" | cut -d' ' -f1)"
  [ "$actual" = "$SHA256" ] || { echo "checksum mismatch: $actual" >&2; exit 1; }
  echo "ok"
fi

mkdir -p "$TARGET"
unzip -q -o "$WORK/$FILE" -d "$TARGET"
echo "unpacked into ${TARGET}"
echo
echo "now run:  node scripts/analyse.mjs ${TARGET}"
