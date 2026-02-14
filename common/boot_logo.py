import os
import subprocess
from pathlib import Path

from openpilot.common.basedir import BASEDIR
from openpilot.common.utils import run_cmd_default


def ensure_boot_background(source_relpath: str = "selfdrive/assets/images/bg.jpg",
                           dest_path: str = "/usr/comma/bg.jpg") -> None:

  # Don’t attempt on non-POSIX (e.g., local dev on Windows/macOS).
  if os.name != "posix":
    return

  dest = Path(dest_path)
  if not dest.exists():
    return

  src = Path(BASEDIR) / source_relpath
  if not src.is_file():
    print(f"boot background source missing: {src}")
    return

  try:
    if dest.is_file() and dest.read_bytes() == src.read_bytes():
      return
  except Exception:
    # If we can't compare, fall back to copying.
    pass

  mount_options = run_cmd_default(["findmnt", "-n", "-o", "OPTIONS", "/"], default="ro")
  restored = False
  try:
    subprocess.check_call(["sudo", "mount", "-o", "remount,rw", "/"])
    subprocess.check_call(["sudo", "cp", "-f", str(src), str(dest)])
  finally:
    try:
      subprocess.check_call(["sudo", "mount", "-o", f"remount,{mount_options}", "/"])
      restored = True
    except Exception:
      pass

  if not restored:
    print("warning: failed to restore original mount options for /")

