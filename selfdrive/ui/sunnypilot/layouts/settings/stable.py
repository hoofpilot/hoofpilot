"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.scroller_tici import Scroller


class StableLayout(Widget):
  def __init__(self):
    super().__init__()

    self._live_view_toggle = toggle_item_sp(
      title=lambda: tr("Live View"),
      description=lambda: tr("Allow remote view inside your car from Konik Stable."),
      initial_state=ui_state.params.get_bool("LiveViewEnabled"),
      callback=self._on_live_view_toggled,
      param="LiveViewEnabled",
    )

    self._scroller = Scroller([self._live_view_toggle], line_separator=True, spacing=0)

  @staticmethod
  def _on_live_view_toggled(enabled: bool):
    if not enabled:
      ui_state.params.put_bool("LiveView", False)

  def _render(self, rect):
    self._scroller.render(rect)

  def show_event(self):
    self._scroller.show_event()

