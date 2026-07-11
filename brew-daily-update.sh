#!/bin/bash
# Homebrew Daily Update Tracker
# Runs brew update, logs new formulae/casks, and regenerates the HTML tracker.
set -euo pipefail

DATA_FILE="$HOME/Documents/homebrew-updates.json"
HTML_FILE="$HOME/Documents/homebrew-updates.html"
GEN_SCRIPT="$HOME/.local/bin/generate-homebrew-html.py"
LOG_FILE="/tmp/homebrew-daily-update.log"
TODAY=$(date +%Y-%m-%d)
BREW="$(command -v brew || true)"

exec >>"$LOG_FILE" 2>&1
echo "=== Homebrew Daily Update — $TODAY $(date +%H:%M:%S) ==="
if [ -z "$BREW" ]; then echo "ERROR: Homebrew executable not found."; exit 1; fi
mkdir -p "$(dirname "$DATA_FILE")"
[ -f "$DATA_FILE" ] || echo "[]" > "$DATA_FILE"

echo "Running brew update..."
UPDATE_OUTPUT=$("$BREW" update 2>&1) || true
echo "$UPDATE_OUTPUT"
NEW_FORMULAE=$(echo "$UPDATE_OUTPUT" | awk '/^==> New Formulae$/{flag=1; next} /^==> /{flag=0} flag' | sed '/^[[:space:]]*$/d' || true)
NEW_CASKS=$(echo "$UPDATE_OUTPUT" | awk '/^==> New Casks$/{flag=1; next} /^==> /{flag=0} flag' | sed '/^[[:space:]]*$/d' || true)
ALL_NEW="${NEW_FORMULAE}${NEW_FORMULAE:+$'\n'}${NEW_CASKS}"

while IFS= read -r name; do
    name=$(echo "$name" | xargs)
    [ -z "$name" ] && continue

    # Skip garbage: lines that are warnings, errors, file paths, or dependency macros
    if echo "$name" | grep -qE '^(Warning|Error|Please report|depends_on macos|Calling string comparison)'; then
        echo "SKIP (not a package): $name"
        continue
    fi
    # Skip file paths (e.g. /opt/homebrew/...)
    if echo "$name" | grep -qE '^/'; then
        echo "SKIP (file path): $name"
        continue
    fi

    # Some taps output "name: description" - extract both parts
    if echo "$name" | grep -q ': '; then
        DESC="${name#*: }"
        name="${name%%: *}"
        echo "PARSED inline desc: $name"
    else
        DESC=$("$BREW" desc "$name" 2>/dev/null | head -1 | sed 's/^[^:]*: //' || true)
        echo "PARSED via brew desc: $name"
    fi
    DESC=${DESC:-A Homebrew package.}

    if python3 - "$DATA_FILE" "$name" <<'PY'
import json, sys
with open(sys.argv[1], encoding="utf-8") as f: data = json.load(f)
sys.exit(0 if any(item.get("name") == sys.argv[2] for item in data) else 1)
PY
    then
        echo "SKIP (already logged): $name"
        continue
    fi

    python3 - "$DATA_FILE" "$TODAY" "$name" "$DESC" <<'PY'
import json, sys
path, date, name, desc = sys.argv[1:]
with open(path, encoding="utf-8") as f: data = json.load(f)
data.append({"date": date, "name": name, "desc": desc, "use_case": f"Install and configure {name} for development workflows"})
with open(path, "w", encoding="utf-8") as f: json.dump(data, f, indent=2)
PY
    echo "ADDED: $name — $DESC"
done <<< "$ALL_NEW"

[ -f "$GEN_SCRIPT" ] && python3 "$GEN_SCRIPT" "$DATA_FILE" "$HTML_FILE"
echo "=== Done: $TODAY $(date +%H:%M:%S) ==="
