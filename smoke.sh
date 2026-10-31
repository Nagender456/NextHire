#!/usr/bin/env bash
set -euo pipefail

api_url="${API_URL:-http://127.0.0.1:8000}"
worker_url="${WORKER_URL:-http://127.0.0.1:8010}"

check() {
  local url="$1"
  curl --fail --silent --show-error --max-time 5 "$url" >/dev/null
}

check "$api_url/health"
check "$api_url/api/v1/health"
check "$worker_url/health"
printf 'NextHire smoke checks passed\n'
