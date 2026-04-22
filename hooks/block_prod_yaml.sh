#!/bin/bash
INPUT=$(cat)
FILE=$(echo "$INPUT" | grep -o '"file_path":"[^"]*"' | cut -d'"' -f4)
if [[ "$FILE" == *"prod.yaml"* || "$FILE" == *"int.yaml"* ]]; then
  echo "BLOCKED: Reading kubeconfig files (prod.yaml, int.yaml) is not permitted." > blocked_reads.log
  echo "BLOCKED: Reading kubeconfig files (prod.yaml, int.yaml) is not permitted."
  exit 2
fi
exit 0
