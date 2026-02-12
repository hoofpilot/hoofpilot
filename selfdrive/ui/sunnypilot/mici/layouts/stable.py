"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from collections.abc import Callable

import pyray as rl
from openpilot.selfdrive.ui.mici.widgets.button import BigParamControl
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.widgets import NavWidget
from openpilot.system.ui.widgets.scroller import Scroller


class StableLayoutMici(NavWidget):
  def __init__(self, back_callback: Callable):
    super().__init__()
    self.set_back_callback(back_callback)

    self._live_view_toggle = BigParamControl("live view", "LiveViewEnabled", toggle_callback=self._on_live_view_toggled)
    self._scroller = Scroller([self._live_view_toggle], snap_items=False)

  @staticmethod
  def _on_live_view_toggled(enabled: bool):
    if not enabled:
      ui_state.params.put_bool("LiveView", False)

  def show_event(self):
    super().show_event()
    self._scroller.show_event()

  def _render(self, rect: rl.Rectangle):
    self._scroller.render(rect)

