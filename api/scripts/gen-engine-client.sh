#!/usr/bin/env bash
# Regenerate the typed engine client from the engine repo's contract.
# Default: sibling checkout. Override with ENGINE_SPEC=path/or/url (e.g. a pinned git tag raw URL).
set -euo pipefail
SPEC="${ENGINE_SPEC:-../engine/api/engine.yaml}"
npx openapi-typescript "$SPEC" -o src/engine/generated/engine.d.ts
echo "generated src/engine/generated/engine.d.ts from $SPEC"
