#!/bin/bash
LOG=/home/debian/SAIC/lifecycle.log
INPUT=$(cat)
echo "$(date -Iseconds) [PreToolUse]  $INPUT" >> "$LOG"
exit 0
