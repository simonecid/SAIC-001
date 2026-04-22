#!/bin/bash
LOG=/home/debian/SAIC/lifecycle.log
INPUT=$(cat)
echo "$(date -Iseconds) [PostToolUse] $INPUT" >> "$LOG"
exit 0
