#!/usr/bin/env bash
export API_HOST=https://api.konik.ai/
export ATHENA_HOST=wss://athena.konik.ai
set -euo pipefail
IFS=$'\n\t'

# On any failure, run the fallback launcher
trap 'exec ./launch_chffrplus.sh' ERR

# Root launcher handles device-specific behavior (including comma 3/tici/c3).
exec ./launch_chffrplus.sh
