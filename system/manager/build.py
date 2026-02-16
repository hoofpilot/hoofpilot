#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path

# NOTE: Do NOT import anything here that needs be built (e.g. params)
from openpilot.common.basedir import BASEDIR
from openpilot.common.spinner import Spinner
from openpilot.common.text_window import TextWindow
from openpilot.common.swaglog import cloudlog, add_file_handler
from openpilot.system.hardware import HARDWARE, AGNOS
from openpilot.system.version import get_build_metadata

MAX_CACHE_SIZE = 4e9 if "CI" in os.environ else 2e9
CACHE_DIR = Path("/data/scons_cache" if AGNOS else "/tmp/scons_cache")

TOTAL_SCONS_NODES = 2705
MAX_BUILD_PROGRESS = 100

def _is_tici() -> bool:
  try:
    return HARDWARE.get_device_type() == "tici"
  except Exception:
    return False


def _agnos_manifest_file() -> str:
  # tici (comma 3) uses the c3 manifest; everything else uses the normal tici manifest.
  return "sunnypilot/system/hardware/c3/agnos.json" if _is_tici() else "system/hardware/tici/agnos.json"

def _parse_version_tuple(v: str) -> tuple[int, ...] | None:
  # Accept "16", "10.1", "12.8.3", etc.
  parts = []
  for p in v.strip().split("."):
    if p == "":
      return None
    try:
      parts.append(int(p))
    except ValueError:
      return None
  # Treat trailing ".0" segments as equivalent (e.g. "16" == "16.0").
  while len(parts) > 1 and parts[-1] == 0:
    parts.pop()
  return tuple(parts)


def _required_agnos_version() -> str | None:
  # Primary source is environment, since launch scripts source launch_env.sh before build.py.
  req = os.environ.get("AGNOS_VERSION")
  if req:
    return req.strip()

  # Fallback to repo launch_env.sh if build.py is run manually without env.
  try:
    out = subprocess.check_output(
      ["bash", "-lc", f"unset AGNOS_VERSION; source \"{BASEDIR}/launch_env.sh\"; echo -n \"$AGNOS_VERSION\""],
      stderr=subprocess.DEVNULL,
      text=True,
    )
    req = out.strip()
    return req if req else None
  except Exception:
    return None


def _ensure_agnos_matches_required() -> None:
  if not AGNOS:
    return

  # Ensure the correct manifest exists for this device type in the repo.
  # (Updater/installer will use it; this makes failures obvious during bring-up.)
  manifest = os.path.join(BASEDIR, _agnos_manifest_file())
  if not os.path.exists(manifest):
    msg = f"Missing AGNOS manifest: {manifest}"
    if not os.getenv("CI"):
      with TextWindow(msg) as t:
        t.wait_for_exit()
    raise SystemExit(msg)

  cur = (HARDWARE.get_os_version() or "").strip()
  req = (_required_agnos_version() or "").strip()
  if not cur or not req:
    return

  cur_t = _parse_version_tuple(cur)
  req_t = _parse_version_tuple(req)
  if cur_t is None or req_t is None:
    return

  # Block build unless the OS matches the required AGNOS version for this fork.
  if cur_t != req_t:
    msg = (
      f"This build requires AGNOS {req}, but this device is running AGNOS {cur}.\n\n"
      "Install the required AGNOS version and reboot, then try again."
    )
    if not os.getenv("CI"):
      with TextWindow(msg) as t:
        t.wait_for_exit()
    raise SystemExit(msg)


def build(spinner: Spinner, dirty: bool = False, minimal: bool = False) -> None:
  _ensure_agnos_matches_required()

  env = os.environ.copy()
  env['SCONS_PROGRESS'] = "1"
  nproc = os.cpu_count()
  if nproc is None:
    nproc = 2

  extra_args = ["--minimal"] if minimal else []

  if AGNOS:
    HARDWARE.set_power_save(False)
    os.sched_setaffinity(0, range(8))  # ensure we can use the isolcpus cores

  # building with all cores can result in using too
  # much memory, so retry with less parallelism
  compile_output: list[bytes] = []
  for n in (nproc, nproc/2, 1):
    compile_output.clear()
    scons: subprocess.Popen = subprocess.Popen(["scons", f"-j{int(n)}", "--cache-populate", *extra_args], cwd=BASEDIR, env=env, stderr=subprocess.PIPE)
    assert scons.stderr is not None

    # Read progress from stderr and update spinner
    while scons.poll() is None:
      try:
        line = scons.stderr.readline()
        if line is None:
          continue
        line = line.rstrip()

        prefix = b'progress: '
        if line.startswith(prefix):
          i = int(line[len(prefix):])
          spinner.update_progress(MAX_BUILD_PROGRESS * min(1., i / TOTAL_SCONS_NODES), 100.)
        elif len(line):
          compile_output.append(line)
          print(line.decode('utf8', 'replace'))
      except Exception:
        pass

    if scons.returncode == 0:
      break

  if scons.returncode != 0:
    # Read remaining output
    if scons.stderr is not None:
      compile_output += scons.stderr.read().split(b'\n')

    # Build failed log errors
    error_s = b"\n".join(compile_output).decode('utf8', 'replace')
    add_file_handler(cloudlog)
    cloudlog.error("scons build failed\n" + error_s)

    # Show TextWindow
    spinner.close()
    if not os.getenv("CI"):
      with TextWindow("openpilot failed to build\n \n" + error_s) as t:
        t.wait_for_exit()
    exit(1)

  # enforce max cache size
  cache_files = [f for f in CACHE_DIR.rglob('*') if f.is_file()]
  cache_files.sort(key=lambda f: f.stat().st_mtime)
  cache_size = sum(f.stat().st_size for f in cache_files)
  for f in cache_files:
    if cache_size < MAX_CACHE_SIZE:
      break
    cache_size -= f.stat().st_size
    f.unlink()


if __name__ == "__main__":
  spinner = Spinner()
  spinner.update_progress(0, 100)
  build_metadata = get_build_metadata()
  build(spinner, build_metadata.openpilot.is_dirty, minimal = AGNOS)
