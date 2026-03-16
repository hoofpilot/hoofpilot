"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import json

import pyray as rl

from openpilot.common.params import Params
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets import Widget

CARD_BG_COLOR = rl.Color(32, 40, 50, 255)
TITLE_COLOR = rl.Color(150, 160, 170, 255)
DEST_COLOR = rl.WHITE
NO_DEST_COLOR = rl.Color(110, 120, 130, 255)

CARD_RADIUS = 0.04
TITLE_FONT_SIZE = 38
DEST_FONT_SIZE = 60
NO_DEST_FONT_SIZE = 54
ICON_SIZE = 80
ICON_MARGIN_X = 45
ICON_TEXT_GAP = 24


class NavDestinationWidget(Widget):
  """Homescreen widget showing current navigation destination."""

  def __init__(self):
    super().__init__()
    self._params = Params()
    self._destination: str | None = None
    self._place_details: str | None = None
    self._icon = None

  def show_event(self):
    self._refresh_destination()

  def _load_icon(self):
    if self._icon is None:
      try:
        self._icon = gui_app.texture(
          "../../hoofpilot/selfdrive/assets/icons/destination.png",
          ICON_SIZE, ICON_SIZE, keep_aspect_ratio=True,
        )
      except Exception:
        pass

  def _safe_get(self, key: str, default: str = "") -> str:
    try:
      val = self._params.get(key) or default
      return val.decode() if isinstance(val, bytes) else val
    except Exception:
      return default

  def _refresh_destination(self):
    dest = None
    details = None

    nav_dest_str = self._safe_get("NavDestination", "")
    if nav_dest_str:
      try:
        nav = json.loads(nav_dest_str)
        place_name = nav.get("place_name") or ""
        if place_name:
          dest = place_name
          details = nav.get("place_details") or ""
      except Exception:
        pass

    if not dest:
      route = self._safe_get("MapboxRoute", "")
      if route:
        dest = route
        details = ""

    self._destination = dest
    self._place_details = details

  def _update_state(self):
    self._refresh_destination()
    self._load_icon()

  def _render(self, rect: rl.Rectangle):
    rl.draw_rectangle_rounded(rect, CARD_RADIUS, 10, CARD_BG_COLOR)

    font = gui_app.font(FontWeight.MEDIUM)
    bold_font = gui_app.font(FontWeight.BOLD)

    icon_x = int(rect.x + ICON_MARGIN_X)
    icon_y = int(rect.y + (rect.height - ICON_SIZE) / 2)

    if self._icon is not None:
      rl.draw_texture_ex(
        self._icon,
        rl.Vector2(icon_x, icon_y),
        0.0,
        1.0,
        rl.WHITE,
      )

    text_x = icon_x + ICON_SIZE + ICON_TEXT_GAP

    title = "Current Destination"
    title_sz = measure_text_cached(font, title, TITLE_FONT_SIZE)

    if self._destination:
      dest_text = self._destination
      dest_font_size = DEST_FONT_SIZE
      dest_color = DEST_COLOR
    else:
      dest_text = "No destination set"
      dest_font_size = NO_DEST_FONT_SIZE
      dest_color = NO_DEST_COLOR

    dest_sz = measure_text_cached(bold_font, dest_text, dest_font_size)

    total_text_h = title_sz.y + 10 + dest_sz.y
    base_y = rect.y + (rect.height - total_text_h) / 2

    rl.draw_text_ex(font, title, rl.Vector2(int(text_x), int(base_y)), TITLE_FONT_SIZE, 0, TITLE_COLOR)
    rl.draw_text_ex(
      bold_font,
      dest_text,
      rl.Vector2(int(text_x), int(base_y + title_sz.y + 10)),
      dest_font_size,
      0,
      dest_color,
    )
