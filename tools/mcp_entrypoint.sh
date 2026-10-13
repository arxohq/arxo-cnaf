#!/bin/sh
# Only deployment credentials and bounded-call settings reach the host.
set -eu
mode=${1:-http}
[ "$#" -le 1 ] || { echo 'Only http, stdio or healthcheck are accepted' >&2; exit 64; }
case "$mode" in
  http|stdio|healthcheck) ;;
  *) echo 'Only http, stdio or healthcheck are accepted' >&2; exit 64 ;;
esac
port=${CNAF_MCP_PORT:-8722}
case "$port" in ''|*[!0-9]*) echo 'Invalid CNAF_MCP_PORT' >&2; exit 64 ;; esac
[ "$port" -gt 0 ] && [ "$port" -le 65535 ] || exit 64
timeout=${CNAF_MCP_CALL_TIMEOUT:-30}
case "$timeout" in ''|*[!0-9]*) echo 'Invalid CNAF_MCP_CALL_TIMEOUT' >&2; exit 64 ;; esac
[ "$timeout" -gt 0 ] && [ "$timeout" -le 110 ] || exit 64
if [ "$mode" = http ] && [ -z "${CNAF_MCP_TOKEN:-}" ]; then
  echo 'CNAF_MCP_TOKEN is required for HTTP' >&2; exit 64
fi
set -- /opt/cnaf/runtime/bin/law-mcp-server --root /opt/cnaf/runtime --profile cnaf
case "$mode" in
  http) set -- "$@" --http --host 0.0.0.0 --port "$port" ;;
  healthcheck) set -- /opt/cnaf/runtime/bin/law-mcp-server --healthcheck --port "$port" ;;
esac
exec /usr/bin/env -i PATH=/usr/bin:/bin HOME=/state LANG=C.UTF-8 \
  LAW_MCP_TOKEN="${CNAF_MCP_TOKEN:-}" \
  LAW_MCP_ALLOWED_ORIGINS="${CNAF_MCP_ALLOWED_ORIGINS:-}" \
  LAW_MCP_CALL_TIMEOUT="$timeout" LAW_MCP_LOG=0 \
  LAW_MCP_ARTIFACT_DIR=/state/artifacts "$@"
