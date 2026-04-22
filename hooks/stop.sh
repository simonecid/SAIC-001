#!/bin/bash
LOG=/home/debian/SAIC/lifecycle.log
INPUT=$(cat)
echo "$(date -Iseconds) [Stop] $INPUT" >> "$LOG"

cd /home/debian/SAIC

# --- Tests ---
python3 -m pytest tests/ -v > /tmp/pytest_out.txt 2>&1
if [ $? -ne 0 ]; then
  python3 - <<'EOF'
import json
output = open('/tmp/pytest_out.txt').read()
print(json.dumps({
    "decision": "block",
    "reason": f"Tests are failing — fix them before finishing:\n\n{output}"
}))
EOF
  exit 0
fi

# --- Build ---
echo "$(date -Iseconds) [Stop] building image with buildah" >> "$LOG"
buildah build -t localhost/user-api:latest . > /tmp/build_out.txt 2>&1
if [ $? -ne 0 ]; then
  python3 - <<'EOF'
import json
output = open('/tmp/build_out.txt').read()
print(json.dumps({
    "decision": "block",
    "reason": f"Image build failed:\n\n{output}"
}))
EOF
  exit 0
fi

# --- Import image into k3s containerd ---
echo "$(date -Iseconds) [Stop] importing image into k3s" >> "$LOG"
rm -f /tmp/user-api.tar \
  && buildah push localhost/user-api:latest docker-archive:/tmp/user-api.tar:localhost/user-api:latest > /tmp/import_out.txt 2>&1 \
  && sudo k3s ctr images import /tmp/user-api.tar >> /tmp/import_out.txt 2>&1
if [ $? -ne 0 ]; then
  python3 - <<'EOF'
import json
output = open('/tmp/import_out.txt').read()
print(json.dumps({
    "decision": "block",
    "reason": f"Image import into k3s failed:\n\n{output}"
}))
EOF
  exit 0
fi

# --- Clean up and redeploy to INT ---
echo "$(date -Iseconds) [Stop] redeploying to INT" >> "$LOG"
kubectl --kubeconfig /home/debian/SAIC/int.yaml delete deployment user-api -n default --ignore-not-found \
  > /tmp/kubectl_out.txt 2>&1 \
  && kubectl --kubeconfig /home/debian/SAIC/int.yaml apply -f /home/debian/SAIC/k8s/int/ \
  >> /tmp/kubectl_out.txt 2>&1 \
  && kubectl --kubeconfig /home/debian/SAIC/int.yaml rollout status deployment/user-api -n default \
  >> /tmp/kubectl_out.txt 2>&1
if [ $? -ne 0 ]; then
  python3 - <<'EOF'
import json
output = open('/tmp/kubectl_out.txt').read()
print(json.dumps({
    "decision": "block",
    "reason": f"Deployment to INT failed:\n\n{output}"
}))
EOF
  exit 0
fi

echo "$(date -Iseconds) [Stop] deployed to INT successfully" >> "$LOG"
exit 0
