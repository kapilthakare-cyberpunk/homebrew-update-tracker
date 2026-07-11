#!/bin/bash
# Homebrew Daily Update Tracker
# Runs brew update, logs new formulae/casks, and regenerates the HTML tracker.
set -euo pipefail

DATA_FILE="$HOME/Documents/homebrew-updates.json"
HTML_FILE="$HOME/Documents/homebrew-updates.html"
GEN_SCRIPT="$HOME/.local/bin/generate-homebrew-html.py"
LOG_FILE="/tmp/homebrew-daily-update.log"
TODAY=$(date +%Y-%m-%d)
BREW="/opt/homebrew/bin/brew"

exec >>"$LOG_FILE" 2>&1
echo "=== Homebrew Daily Update — $TODAY $(date +%H:%M:%S) ==="

# Ensure data file exists
if [ ! -f "$DATA_FILE" ]; then
    echo "[]" > "$DATA_FILE"
    echo "Initialized data file: $DATA_FILE"
fi

# Run brew update
echo "Running brew update..."
UPDATE_OUTPUT=$("$BREW" update 2>&1) || true
echo "$UPDATE_OUTPUT"

# Extract "New Formulae" block (between "==> New Formulae" and next "==>" or end)
NEW_FORMULAE=$(echo "$UPDATE_OUTPUT" | awk '/^==> New Formulae$/{flag=1; next} /^==> /{flag=0} flag' | sed '/^[[:space:]]*$/d' || true)

# Extract "New Casks" block
NEW_CASKS=$(echo "$UPDATE_OUTPUT" | awk '/^==> New Casks$/{flag=1; next} /^==> /{flag=0} flag' | sed '/^[[:space:]]*$/d' || true)

ALL_NEW=""
[ -n "$NEW_FORMULAE" ] && ALL_NEW="${ALL_NEW}${NEW_FORMULAE}"$'\n'
[ -n "$NEW_CASKS" ] && ALL_NEW="${ALL_NEW}${NEW_CASKS}"

if [ -z "$(echo "$ALL_NEW" | tr -d '[:space:]')" ]; then
    echo "No new formulae or casks found today."
else
    echo "New items discovered. Processing..."
    echo "--- New Formulae ---"
    echo "$NEW_FORMULAE"
    echo "--- New Casks ---"
    echo "$NEW_CASKS"
    echo "--------------------"

    while IFS= read -r name; do
        [ -z "$name" ] && continue
        # Strip any leading/trailing whitespace
        name=$(echo "$name" | xargs)
        [ -z "$name" ] && continue

        # Skip if already in the data file
        if python3 -c "
import json
data = json.load(open('$DATA_FILE'))
if any(d.get('name','') == '$name' for d in data):
    exit(1)
" 2>/dev/null; then
            :
        else
            echo "  SKIP (already logged): $name"
            continue
        fi

        # Get description from brew
        DESC=$("$BREW" desc "$name" 2>/dev/null | head -1 | sed 's/^[^:]*: //' || echo "A Homebrew package.")
        # Escape for JSON
        DESC_JSON=$(python3 -c "import json; print(json.dumps('$DESC'));")

        # Add to JSON data
        python3 -c "
import json
data = json.load(open('$DATA_FILE'))
data.append({
    'date': '$TODAY',
    'name': '$name',
    'desc': $DESC_JSON,
    'use_case': 'Install and configure $name for enhanced development workflows'
})
json.dump(data, open('$DATA_FILE', 'w'), indent=2)
"
        echo "  ADDED: $name — $DESC"
    done <<< "$ALL_NEW"
fi

# Regenerate HTML tracker
if [ -f "$GEN_SCRIPT" ]; then
    python3 "$GEN_SCRIPT" "$DATA_FILE" "$HTML_FILE"
    echo "HTML tracker regenerated: $HTML_FILE"
else
    echo "WARNING: HTML generator script not found at $GEN_SCRIPT"
fi

echo "=== Done: $TODAY $(date +%H:%M:%S) ==="
