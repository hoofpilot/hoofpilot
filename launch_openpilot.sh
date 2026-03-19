#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# On any failure, run the fallback launcher
trap 'exec ./launch_chffrplus.sh' ERR

# Root launcher handles device-specific behavior (including comma 3/tici/c3).
exec ./launch_chffrplus.sh
