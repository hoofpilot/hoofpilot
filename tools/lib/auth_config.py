import json
import os
from pathlib import Path

try:
  # Preferred on-device / in-repo path resolution.
  from openpilot.system.hardware.hw import Paths  # type: ignore
except Exception:
  Paths = None  # type: ignore


class MissingAuthConfigError(Exception):
  pass


def _auth_paths() -> list[str]:
  paths: list[str] = []

  # Primary location used by openpilot.
  if Paths is not None:
    try:
      paths.append(os.path.join(Paths.config_root(), 'auth.json'))
    except Exception:
      pass

  # Cabana (C++) reads this path directly (without OPENPILOT_PREFIX).
  paths.append(str(Path.home() / ".comma" / "auth.json"))

  # De-dupe while preserving order.
  out: list[str] = []
  seen: set[str] = set()
  for p in paths:
    if p not in seen:
      out.append(p)
      seen.add(p)
  return out


def get_token():
  for auth_path in _auth_paths():
    try:
      with open(auth_path) as f:
        auth = json.load(f)
        token = auth.get('access_token')
        if token:
          return token
    except Exception:
      continue
  return None


def set_token(token):
  payload = {'access_token': token}
  for auth_path in _auth_paths():
    os.makedirs(os.path.dirname(auth_path), exist_ok=True)
    with open(auth_path, 'w') as f:
      json.dump(payload, f)


def clear_token():
  for auth_path in _auth_paths():
    try:
      os.unlink(auth_path)
    except FileNotFoundError:
      pass
