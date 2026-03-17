"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.common.params import Params
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.scroller_tici import Scroller

from openpilot.system.ui.hoofpilot.widgets.list_view import toggle_item_sp


class NavigationLayout(Widget):
  def __init__(self):
    super().__init__()
    self._params = Params()

    self._show_nav_widget_item = toggle_item_sp(
      title=lambda: "Show Navigation Widget",
      description=lambda: "Replace the driving mode selector on the homescreen with a widget for navigation.",
      initial_state=self._safe_get_bool("ShowNavWidget"),
      param="ShowNavWidget",
    )

    self.items = [self._show_nav_widget_item]
    self._scroller = Scroller(self.items, line_separator=True, spacing=0)

  def _safe_get_bool(self, key, default=False):
    try:
      return self._params.get_bool(key)
    except Exception:
      return default

  def _render(self, rect):
    self._scroller.render(rect)

  def show_event(self):
    self._scroller.show_event()
