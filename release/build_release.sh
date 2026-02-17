#!/usr/bin/env bash
set -euo pipefail
set -x

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null && pwd)"
SOURCE_DIR="$(git -C "$DIR" rev-parse --show-toplevel)"

# Optional inputs
REMOTE_URL="${REMOTE_URL:-git@github.com:hoofpilot/openpilot.git}"
DO_PUSH="${DO_PUSH:-0}"           # set to 1 to push to REMOTE_URL (force-push)
RUN_TESTS="${RUN_TESTS:-0}"       # set to 1 to run pytest
BUILD_PANDA="${BUILD_PANDA:-0}"   # set to 1 to build panda firmware

# Build directory (on a PC/WSL, never default to /data/openpilot)
BUILD_DIR="${BUILD_DIR:-"$(mktemp -d -t hoofpilot_release_build_XXXXXX)"}"

# Branch name to create/push
if [ -z "${RELEASE_BRANCH:-}" ]; then
  # Best-effort version extraction for unique branch naming.
  VERSION="$(awk -F'[\"-]' '{print $2}' "$SOURCE_DIR/hoofpilot/common/version.h" 2>/dev/null || true)"
  TS="$(date +%Y%m%d_%H%M%S)"
  RELEASE_BRANCH="release-${VERSION:-unknown}-$TS"
fi

if [ -z "$BUILD_DIR" ] || [ "$BUILD_DIR" = "/" ]; then
  echo "Refusing to run with unsafe BUILD_DIR=$BUILD_DIR"
  exit 1
fi
if [ "$BUILD_DIR" = "$SOURCE_DIR" ]; then
  echo "Refusing to run: BUILD_DIR ($BUILD_DIR) equals SOURCE_DIR ($SOURCE_DIR)"
  exit 1
fi

# set git identity (used for commits created in BUILD_DIR)
source "$DIR/identity.sh"

echo "[-] Setting up repo T=$SECONDS"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"
git init
git remote add origin "$REMOTE_URL"
git checkout --orphan "$RELEASE_BRANCH"

echo "[-] copying files T=$SECONDS"
cd "$SOURCE_DIR"
# Avoid "Argument list too long" by streaming the file list to tar.
FILES_LIST="$(mktemp -t hoofpilot_release_files_XXXXXX)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
"$PYTHON_BIN" ./release/release_files.py > "$FILES_LIST"
tar -C "$SOURCE_DIR" -cf - -T "$FILES_LIST" | tar -C "$BUILD_DIR" -xpf -
rm -f "$FILES_LIST"

cd "$BUILD_DIR"

rm -f panda/board/obj/panda.bin.signed
rm -f panda/board/obj/panda_h7.bin.signed

VERSION="$(awk -F'[\"-]' '{print $2}' hoofpilot/common/version.h)"
echo "[-] committing version $VERSION T=$SECONDS"
git add -f .
git commit -a -m "hoofpilot $VERSION release"

export PYTHONPATH="$BUILD_DIR"

# Build openpilot (requires build deps installed on your PC/WSL).
scons -j"$(nproc)" --minimal

if [ "$BUILD_PANDA" = "1" ]; then
  if [ -z "${PANDA_DEBUG_BUILD:-}" ]; then
    # Signed panda build requires the release certs. On a PC this usually won't exist.
    if [ -z "${PANDA_CERT_DIR:-}" ]; then
      echo "PANDA_CERT_DIR not set. Either set PANDA_DEBUG_BUILD=1 or provide PANDA_CERT_DIR."
      exit 1
    fi
    CERT="$PANDA_CERT_DIR" RELEASE=1 scons -j"$(nproc)" panda/
  else
    scons -j"$(nproc)" panda/
  fi
fi

# Ensure no submodules in release
if test "$(git submodule--helper list | wc -l)" -gt "0"; then
  echo "submodules found:"
  git submodule--helper list
  exit 1
fi
git submodule status

# Cleanup (build artifacts + non-target host binaries)
find . -name '*.a' -delete
find . -name '*.o' -delete
find . -name '*.os' -delete
find . -name '*.pyc' -delete
find . -name 'moc_*' -delete
find . -name '__pycache__' -delete
rm -rf .sconsign.dblite Jenkinsfile release/ || true
rm -f selfdrive/modeld/models/driving_vision.onnx || true
rm -f selfdrive/modeld/models/driving_policy.onnx || true
rm -f hoofpilot/modeld*/models/supercombo.onnx || true

find third_party/ -name '*x86*' -exec rm -rf {} +
find third_party/ -name '*Darwin*' -exec rm -rf {} +

# Restore third_party (we removed some host binaries above, keep repo content intact)
git checkout third_party/

# Mark as prebuilt release
touch prebuilt

git add -f .
git commit --amend -m "hoofpilot $VERSION"

if [ "$RUN_TESTS" = "1" ]; then
  RELEASE=1 pytest -n0 -s selfdrive/test/test_onroad.py
fi

if [ "$DO_PUSH" = "1" ]; then
  echo "[-] pushing release to $REMOTE_URL ($RELEASE_BRANCH) T=$SECONDS"
  git push -f origin "$RELEASE_BRANCH:$RELEASE_BRANCH"
else
  echo "[-] skipping push (set DO_PUSH=1 to push) T=$SECONDS"
fi

echo "[-] done T=$SECONDS"
echo "release repo at: $BUILD_DIR"
