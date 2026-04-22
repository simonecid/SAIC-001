#!/bin/bash
INPUT=$(cat)

FILE=$(python3 -c "
import sys, json
d = json.load(sys.stdin)
print(d.get('tool_input', {}).get('file_path', ''))
" <<< "$INPUT" 2>/dev/null)

[[ "$FILE" == *.py ]] || exit 0

OUTPUT=$(python3 -m py_compile "$FILE" 2>&1)

if [ $? -ne 0 ]; then
  python3 - "$FILE" "$OUTPUT" <<'EOF'
import json, sys
print(json.dumps({
    "decision": "block",
    "reason": f"Syntax error in {sys.argv[1]}:\n\n{sys.argv[2]}"
}))
EOF
fi

exit 0
