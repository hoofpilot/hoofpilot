"""
Sunnypilot mici Stable panel.

Keep this as a thin wrapper around the base mici Stable panel so behavior stays consistent
across platforms (PIN, Live View, Remote SSH, Reset PIN).
"""

from openpilot.selfdrive.ui.mici.layouts.settings.stable import StableLayoutMici as _BaseStableLayoutMici


class StableLayoutMici(_BaseStableLayoutMici):
  pass

