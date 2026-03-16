"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import json
import math

import pyray as rl

from openpilot.common.params import Params
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app, FontWeight, MousePos
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets import Widget

# ── Colours ────────────────────────────────────────────────────────────────────
# Main card gradient (matches Stock ADAS Mode card in ExperimentalModeButton)
CARD_LEFT  = rl.Color(44, 52, 62, 255)
CARD_RIGHT = rl.Color(70, 82, 92, 255)
CARD_RADIUS = 0.083

# Destination pill
DEST_PILL_COLOR    = rl.Color(255, 255, 255, 255)
DEST_TEXT_COLOR    = rl.Color(15, 15, 20, 255)
NO_DEST_PILL_COLOR = rl.Color(255, 255, 255, 20)
NO_DEST_TEXT_COLOR = rl.Color(180, 190, 200, 255)

# Sub-boxes
BOX_COLOR        = rl.Color(255, 255, 255, 18)
BOX_HOVER_COLOR  = rl.Color(255, 255, 255, 40)
BOX_LABEL_COLOR  = rl.Color(160, 170, 185, 255)
BOX_VALUE_COLOR  = rl.WHITE
MANEUVER_COLOR   = rl.Color(120, 200, 255, 255)

# Title
TITLE_COLOR    = rl.Color(200, 210, 220, 255)
SUBTITLE_COLOR = rl.Color(140, 155, 170, 255)

# ── Layout ─────────────────────────────────────────────────────────────────────
PADDING_X       = 35
PADDING_Y       = 28
TITLE_FONT_SIZE    = 44
SUBTITLE_FONT_SIZE = 30
DEST_FONT_SIZE     = 52
NO_DEST_FONT_SIZE = 46
ICON_SIZE       = 72
BOX_RADIUS      = 0.12
BOX_GAP         = 14


def _format_distance(meters: float) -> str:
  if meters < 1000:
    return f"{int(meters)}m"
  return f"{meters / 1000:.1f}km"


class NavDestinationWidget(Widget):
  """Homescreen widget showing current navigation destination and shortcuts."""

  def __init__(self):
    super().__init__()
    self._params = Params()
    self._destination: str | None = None
    self._place_details: str | None = None
    self._icon = None

    # Favorites: list of (label, address) for the 3 shortcut boxes
    self._shortcut_labels: list[str] = ["Home", "Work", "Favorite"]
    self._shortcut_addrs: list[str | None] = [None, None, None]

    # Hover state for the 3 sub-boxes
    self._box_hovered: int = -1
    self._box_rects: list[rl.Rectangle] = [rl.Rectangle(0, 0, 0, 0)] * 3

  # ── Lifecycle ──────────────────────────────────────────────────────────────

  def show_event(self):
    self._refresh_destination()
    self._refresh_shortcuts()

  def _load_icon(self):
    if self._icon is None:
      try:
        self._icon = gui_app.texture(
          "../../hoofpilot/selfdrive/assets/icons/destination.png",
          ICON_SIZE, ICON_SIZE, keep_aspect_ratio=True,
        )
      except Exception:
        pass

  # ── Param helpers ──────────────────────────────────────────────────────────

  def _safe_get(self, key: str, default: str = "") -> str:
    try:
      val = self._params.get(key) or default
      return val.decode() if isinstance(val, bytes) else val
    except Exception:
      return default

  def _safe_put(self, key: str, value: str):
    try:
      self._params.put(key, value)
    except Exception:
      pass

  def _safe_remove(self, key: str):
    try:
      self._params.remove(key)
    except Exception:
      pass

  # ── State refresh ──────────────────────────────────────────────────────────

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

  def _refresh_shortcuts(self):
    try:
      favs_raw = self._safe_get("MapboxFavorites", "{}")
      favs = json.loads(favs_raw) if favs_raw else {}
    except Exception:
      favs = {}

    home_addr = favs.get("home")
    work_addr = favs.get("work")
    fav_items = list((favs.get("favorites") or {}).items())
    first_fav_label, first_fav_addr = (fav_items[0][0], fav_items[0][1]) if fav_items else ("Favorite", None)

    self._shortcut_labels = ["Home", "Work", first_fav_label]
    self._shortcut_addrs  = [home_addr, work_addr, first_fav_addr]

  def _get_maneuvers(self) -> list:
    try:
      nav_msg = ui_state.sm['navigationd']
      if nav_msg.valid and len(nav_msg.allManeuvers) > 0:
        return list(nav_msg.allManeuvers)[:3]
    except Exception:
      pass
    return []

  def _update_state(self):
    self._refresh_destination()
    self._refresh_shortcuts()
    self._load_icon()
    # Update hover from mouse position
    try:
      mouse = rl.get_mouse_position()
      self._box_hovered = -1
      for i, r in enumerate(self._box_rects):
        if rl.check_collision_point_rec(mouse, r):
          self._box_hovered = i
          break
    except Exception:
      pass

  # ── Input ──────────────────────────────────────────────────────────────────

  def _handle_mouse_release(self, mouse_pos: MousePos):
    for i, r in enumerate(self._box_rects):
      if rl.check_collision_point_rec(mouse_pos, r):
        self._on_box_tap(i)
        break

  def _on_box_tap(self, index: int):
    if self._destination:
      return  # maneuver boxes are info-only
    addr = self._shortcut_addrs[index]
    if addr:
      self._safe_put("MapboxRoute", addr)
      self._safe_remove("NavDestination")
      self._refresh_destination()

  # ── Drawing helpers ────────────────────────────────────────────────────────

  @staticmethod
  def _draw_rounded_gradient(rect: rl.Rectangle, roundness: float, left: rl.Color, right: rl.Color):
    w = max(1, int(rect.width))
    h = max(1, int(rect.height))
    r = int(max(1.0, roundness * min(w, h) * 0.5))
    x0, y0 = int(rect.x), int(rect.y)
    for i in range(w):
      t = i / max(1, w - 1)
      col = rl.Color(
        int(left.r + (right.r - left.r) * t),
        int(left.g + (right.g - left.g) * t),
        int(left.b + (right.b - left.b) * t),
        255,
      )
      cut = 0
      if i < r:
        dx = r - i
        cut = int(r - math.sqrt(max(0, r * r - dx * dx)))
      elif i >= w - r:
        dx = i - (w - r - 1)
        cut = int(r - math.sqrt(max(0, r * r - dx * dx)))
      y_start, y_end = y0 + cut, y0 + h - cut
      if y_end > y_start:
        rl.draw_line(x0 + i, y_start, x0 + i, y_end, col)

  # ── Render ─────────────────────────────────────────────────────────────────

  def _render(self, rect: rl.Rectangle):
    # Background gradient card
    self._draw_rounded_gradient(rect, CARD_RADIUS, CARD_LEFT, CARD_RIGHT)

    font        = gui_app.font(FontWeight.MEDIUM)
    bold_font   = gui_app.font(FontWeight.BOLD)

    cx = rect.x + PADDING_X
    cy = rect.y + PADDING_Y

    # ── "NAVIGATION" title ─────────────────────────────────────────────────
    title_sz = measure_text_cached(font, "NAVIGATION", TITLE_FONT_SIZE)
    rl.draw_text_ex(font, "NAVIGATION", rl.Vector2(int(cx), int(cy)), TITLE_FONT_SIZE, 0, TITLE_COLOR)
    cy += title_sz.y + 6
    subtitle_sz = measure_text_cached(font, "Manage at stable.konik.ai", SUBTITLE_FONT_SIZE)
    rl.draw_text_ex(font, "Manage at stable.konik.ai", rl.Vector2(int(cx), int(cy)), SUBTITLE_FONT_SIZE, 0, SUBTITLE_COLOR)
    cy += subtitle_sz.y + 14

    # ── Destination pill ───────────────────────────────────────────────────
    pill_w   = rect.width - 2 * PADDING_X
    pill_h   = 120
    pill_rect = rl.Rectangle(cx, cy, pill_w, pill_h)

    if self._destination:
      rl.draw_rectangle_rounded(pill_rect, 0.25, 10, DEST_PILL_COLOR)
      # Icon
      icon_x = int(cx + 20)
      icon_y = int(cy + (pill_h - ICON_SIZE) / 2)
      if self._icon is not None:
        rl.draw_texture_ex(self._icon, rl.Vector2(icon_x, icon_y), 0.0, 1.0, DEST_TEXT_COLOR)
      # Text
      text_x = icon_x + ICON_SIZE + 14
      dest_text = self._destination
      dest_sz = measure_text_cached(bold_font, dest_text, DEST_FONT_SIZE)
      text_y = int(cy + (pill_h - dest_sz.y) / 2)
      rl.draw_text_ex(bold_font, dest_text, rl.Vector2(text_x, text_y), DEST_FONT_SIZE, 0, DEST_TEXT_COLOR)
    else:
      rl.draw_rectangle_rounded(pill_rect, 0.25, 10, NO_DEST_PILL_COLOR)
      icon_x = int(cx + 20)
      icon_y = int(cy + (pill_h - ICON_SIZE) / 2)
      if self._icon is not None:
        rl.draw_texture_ex(self._icon, rl.Vector2(icon_x, icon_y), 0.0, 1.0, NO_DEST_TEXT_COLOR)
      text_x = icon_x + ICON_SIZE + 14
      nd_text = "No destination set"
      nd_sz = measure_text_cached(font, nd_text, NO_DEST_FONT_SIZE)
      text_y = int(cy + (pill_h - nd_sz.y) / 2)
      rl.draw_text_ex(font, nd_text, rl.Vector2(text_x, text_y), NO_DEST_FONT_SIZE, 0, NO_DEST_TEXT_COLOR)

    cy += pill_h + 18

    # ── 3 sub-boxes ────────────────────────────────────────────────────────
    boxes_h   = rect.y + rect.height - PADDING_Y - cy
    box_w     = (rect.width - 2 * PADDING_X - 2 * BOX_GAP) / 3
    maneuvers = self._get_maneuvers() if self._destination else []

    new_rects = []
    for i in range(3):
      bx = cx + i * (box_w + BOX_GAP)
      br = rl.Rectangle(bx, cy, box_w, boxes_h)
      new_rects.append(br)

      # Box background
      bg = BOX_HOVER_COLOR if self._box_hovered == i and not self._destination else BOX_COLOR
      rl.draw_rectangle_rounded(br, BOX_RADIUS, 10, bg)

      if self._destination:
        if i < len(maneuvers):
          self._draw_maneuver_box(br, maneuvers[i], font, bold_font)
        # else: blank box
      else:
        self._draw_shortcut_box(br, i, font, bold_font)

    self._box_rects = new_rects

  def _draw_shortcut_box(self, rect: rl.Rectangle, index: int, font, bold_font):
    label = self._shortcut_labels[index]
    addr  = self._shortcut_addrs[index]

    pad = 18
    # Icon character mapping
    icons = ["H", "W", "★"]
    icon_text = icons[index]
    icon_sz = measure_text_cached(bold_font, icon_text, 52)
    icon_x = int(rect.x + (rect.width - icon_sz.x) / 2)
    icon_y = int(rect.y + pad + 10)
    rl.draw_text_ex(bold_font, icon_text, rl.Vector2(icon_x, icon_y), 52, 0, BOX_LABEL_COLOR)

    label_sz = measure_text_cached(font, label, 38)
    lx = int(rect.x + (rect.width - label_sz.x) / 2)
    ly = icon_y + icon_sz.y + 10
    rl.draw_text_ex(font, label, rl.Vector2(lx, ly), 38, 0, BOX_VALUE_COLOR)

    if addr:
      # Truncate address to fit
      short_addr = addr if len(addr) <= 18 else addr[:16] + "…"
      addr_sz = measure_text_cached(font, short_addr, 32)
      ax = int(rect.x + (rect.width - addr_sz.x) / 2)
      ay = ly + label_sz.y + 8
      rl.draw_text_ex(font, short_addr, rl.Vector2(ax, ay), 32, 0, BOX_LABEL_COLOR)
    else:
      set_text = "Tap to set"
      set_sz = measure_text_cached(font, set_text, 30)
      sx = int(rect.x + (rect.width - set_sz.x) / 2)
      sy = ly + label_sz.y + 8
      rl.draw_text_ex(font, set_text, rl.Vector2(sx, sy), 30, 0, rl.Color(120, 130, 140, 255))

  def _draw_maneuver_box(self, rect: rl.Rectangle, maneuver, font, bold_font):
    dist_text = _format_distance(maneuver.distance)
    dist_sz   = measure_text_cached(bold_font, dist_text, 44)
    dx = int(rect.x + (rect.width - dist_sz.x) / 2)
    dy = int(rect.y + rect.height * 0.18)
    rl.draw_text_ex(bold_font, dist_text, rl.Vector2(dx, dy), 44, 0, MANEUVER_COLOR)

    instr = maneuver.instruction or f"{maneuver.type} {maneuver.modifier}".strip()
    words = instr.split()
    lines, line = [], []
    for word in words:
      test = " ".join(line + [word])
      test_sz = measure_text_cached(font, test, 32)
      if test_sz.x > rect.width - 16 and line:
        lines.append(" ".join(line))
        line = [word]
      else:
        line.append(word)
    if line:
      lines.append(" ".join(line))
    lines = lines[:3]

    total_h = len(lines) * 36
    text_y  = dy + dist_sz.y + 12
    for ln in lines:
      ln_sz = measure_text_cached(font, ln, 32)
      lx = int(rect.x + (rect.width - ln_sz.x) / 2)
      rl.draw_text_ex(font, ln, rl.Vector2(lx, int(text_y)), 32, 0, BOX_VALUE_COLOR)
      text_y += 36
