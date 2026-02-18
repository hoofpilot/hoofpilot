## Local/WSL Usage

These scripts are safe to run on a PC/WSL if you have build deps installed.

Build a release in a temporary directory (no push by default):
```bash
cd /path/to/openpilot/release
RELEASE_BRANCH=release ./build_release.sh
```

Push the generated release branch (force-push):
```bash
DO_PUSH=1 RELEASE_BRANCH=release ./build_release.sh
```

Create a stripped staging tree (does not clean your source checkout unless `CLEAN_SOURCE=1`):
```bash
cd /path/to/openpilot/release
BRANCH=devel-staging ./build_stripped.sh
```
