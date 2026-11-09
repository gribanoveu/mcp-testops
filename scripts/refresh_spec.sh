#!/bin/sh
# Re-snapshot the TestOps OpenAPI spec and show what changed against the committed one.
#
#   scripts/refresh_spec.sh [output]      # default output: openapi/api-docs.json.new
#
# Reads the stand from TESTOPS_BASE_URL (default: the internal one). It never overwrites
# openapi/api-docs.json: read the version and the diff first, because contract tests and
# docs/05 point at that file. When the change is understood:
#
#   mv openapi/api-docs.json.new openapi/api-docs.json && pytest -q
#
set -eu

cd "$(dirname "$0")/.."

BASE_URL=${TESTOPS_BASE_URL:-https://testops.moscow.alfaintra.net}
OUT=${1:-openapi/api-docs.json.new}
CURRENT=openapi/api-docs.json

curl -fsS "${BASE_URL%/}/api-docs/" -o "$OUT"
echo "saved: $OUT"

python3 - "$OUT" "$CURRENT" <<'PY'
import json
import sys

new_path, old_path = sys.argv[1], sys.argv[2]
new = json.load(open(new_path, encoding="utf-8"))
print("new spec version:", new.get("info", {}).get("version"), "| paths:", len(new.get("paths", {})))

try:
    old = json.load(open(old_path, encoding="utf-8"))
except FileNotFoundError:
    print("no committed snapshot to compare with")
    sys.exit(0)

print("old spec version:", old.get("info", {}).get("version"))

for title, new_keys, old_keys in (
    ("paths", set(new.get("paths", {})), set(old.get("paths", {}))),
    ("schemas", set(new.get("components", {}).get("schemas", {})), set(old.get("components", {}).get("schemas", {}))),
):
    added = sorted(new_keys - old_keys)
    removed = sorted(old_keys - new_keys)
    print(f"{title}: +{len(added)} -{len(removed)}")
    for name in added:
        print("  +", name)
    for name in removed:
        print("  -", name)

print()
print("next: check the endpoints and schemas the tools use (docs/03-tools-spec.md),")
print("      then move the snapshot over the committed one and run pytest -q.")
PY
