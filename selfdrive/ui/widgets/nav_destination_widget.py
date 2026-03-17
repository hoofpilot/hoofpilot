"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import json

import pyray as rl

from openpilot.common.params import Params
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app, FontWeight, MousePos
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets import Widget

# ── Colours ────────────────────────────────────────────────────────────────────
CARD_COLOR  = rl.Color(30, 30, 30, 255)
CARD_RADIUS = 0.05

PILL_COLOR      = rl.Color(255, 255, 255, 255)
PILL_TEXT_COLOR = rl.Color(15, 15, 20, 255)

BOX_COLOR       = rl.Color(20, 20, 20, 255)
BOX_HOVER_COLOR = rl.Color(45, 45, 45, 255)
BOX_LABEL_COLOR = rl.Color(160, 170, 185, 255)
BOX_VALUE_COLOR = rl.WHITE
MANEUVER_COLOR  = rl.Color(120, 200, 255, 255)

TITLE_COLOR    = rl.Color(200, 210, 220, 255)

# ── Layout ─────────────────────────────────────────────────────────────────────
PADDING_X          = 35
PADDING_Y          = 28
TITLE_FONT_SIZE    = 58
DEST_FONT_SIZE     = 48
ICON_SIZE          = 64
BOX_RADIUS         = 0.14
BOX_GAP            = 20
PILL_H             = 138
ROW_ICON_SIZE      = 56


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
    self._dest_icon = None
    self._shortcut_icons: dict = {}

    self._shortcut_labels: list[str] = ["Home", "Work", "Favorite"]
    self._shortcut_addrs: list[str | None] = [None, None, None]

    self._box_hovered: int = -1
    self._box_rects: list[rl.Rectangle] = [rl.Rectangle(0, 0, 0, 0)] * 3

    self._clear_btn_rect: rl.Rectangle = rl.Rectangle(0, 0, 0, 0)
    self._clear_btn_hovered: bool = False

  # ── Lifecycle ──────────────────────────────────────────────────────────────

  def show_event(self):
    self._refresh_destination()
    self._refresh_shortcuts()

  def _load_icons(self):
    if self._dest_icon is None:
      try:
        self._dest_icon = gui_app.texture(
          "../../hoofpilot/selfdrive/assets/icons/destination.png",
          ICON_SIZE, ICON_SIZE, keep_aspect_ratio=True,
        )
      except Exception:
        pass

    icon_paths = {
      'home':     "../../hoofpilot/selfdrive/assets/offroad/icon_home.png",
      'work':     "../../hoofpilot/selfdrive/assets/icons/work.png",
      'favorite': "../../hoofpilot/selfdrive/assets/icons/star-filled.png",
    }
    for key, path in icon_paths.items():
      if key not in self._shortcut_icons:
        try:
          self._shortcut_icons[key] = gui_app.texture(path, ROW_ICON_SIZE, ROW_ICON_SIZE, keep_aspect_ratio=True)
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
    self._load_icons()
    try:
      self._box_hovered = -1
      self._clear_btn_hovered = False
      if rl.is_mouse_button_down(rl.MouseButton.MOUSE_BUTTON_LEFT):
        mouse = rl.get_mouse_position()
        if self._destination and rl.check_collision_point_rec(mouse, self._clear_btn_rect):
          self._clear_btn_hovered = True
        elif not self._destination:
          for i, r in enumerate(self._box_rects):
            if rl.check_collision_point_rec(mouse, r):
              self._box_hovered = i
              break
    except Exception:
      pass

  # ── Input ──────────────────────────────────────────────────────────────────

  def _handle_mouse_release(self, mouse_pos: MousePos):
    if self._destination:
      if rl.check_collision_point_rec(mouse_pos, self._clear_btn_rect):
        self._clear_destination()
      return
    for i, r in enumerate(self._box_rects):
      if rl.check_collision_point_rec(mouse_pos, r):
        self._on_box_tap(i)
        break

  def _clear_destination(self):
    self._safe_remove("NavDestination")
    self._safe_remove("MapboxRoute")
    self._refresh_destination()

  def _on_box_tap(self, index: int):
    addr = self._shortcut_addrs[index]
    if addr:
      self._safe_put("MapboxRoute", addr)
      self._safe_remove("NavDestination")
      self._refresh_destination()

  # ── Render ─────────────────────────────────────────────────────────────────

  def _render(self, rect: rl.Rectangle):
    rl.draw_rectangle_rounded(rect, CARD_RADIUS, 10, CARD_COLOR)

    font      = gui_app.font(FontWeight.MEDIUM)
    bold_font = gui_app.font(FontWeight.BOLD)

    cx = rect.x + PADDING_X
    cy = rect.y + PADDING_Y

    # ── Title ─────────────────────────────────────────────────────────────
    title_sz = measure_text_cached(bold_font, "NAVIGATION", TITLE_FONT_SIZE)
    rl.draw_text_ex(bold_font, "NAVIGATION", rl.Vector2(int(cx), int(cy)), TITLE_FONT_SIZE, 0, TITLE_COLOR)
    cy += title_sz.y + 14

    # ── Destination pill ──────────────────────────────────────────────────
    pill_w    = rect.width - 2 * PADDING_X
    pill_rect = rl.Rectangle(cx, cy, pill_w, PILL_H)
    rl.draw_rectangle_rounded(pill_rect, 0.25, 10, PILL_COLOR)

    icon_x = int(cx + 20)
    icon_y = int(cy + (PILL_H - ICON_SIZE) / 2)
    if self._dest_icon is not None:
      rl.draw_texture_ex(self._dest_icon, rl.Vector2(icon_x, icon_y), 0.0, 1.0, rl.WHITE)

    # ── Clear (X) button — only when a destination is active ──────────────
    btn_r  = 22
    btn_cx = int(pill_rect.x + pill_rect.width - 20 - btn_r)
    btn_cy = int(pill_rect.y + PILL_H / 2)
    if self._destination:
      self._clear_btn_rect = rl.Rectangle(btn_cx - btn_r, btn_cy - btn_r, btn_r * 2, btn_r * 2)
      btn_color = rl.Color(210, 55, 55, 255) if self._clear_btn_hovered else rl.Color(160, 40, 40, 200)
      rl.draw_circle(btn_cx, btn_cy, btn_r, btn_color)
      xs = 8
      rl.draw_line_ex(rl.Vector2(btn_cx - xs, btn_cy - xs), rl.Vector2(btn_cx + xs, btn_cy + xs), 2.5, rl.WHITE)
      rl.draw_line_ex(rl.Vector2(btn_cx + xs, btn_cy - xs), rl.Vector2(btn_cx - xs, btn_cy + xs), 2.5, rl.WHITE)

    text_x = icon_x + ICON_SIZE + 14
    if self._destination:
      dest_sz = measure_text_cached(bold_font, self._destination, DEST_FONT_SIZE)
      text_y  = int(cy + (PILL_H - dest_sz.y) / 2)
      rl.draw_text_ex(bold_font, self._destination, rl.Vector2(text_x, text_y), DEST_FONT_SIZE, 0, PILL_TEXT_COLOR)
    else:
      nd_text = "No destination set"
      nd_sz   = measure_text_cached(font, nd_text, DEST_FONT_SIZE)
      text_y  = int(cy + (PILL_H - nd_sz.y) / 2)
      rl.draw_text_ex(font, nd_text, rl.Vector2(text_x, text_y), DEST_FONT_SIZE, 0, PILL_TEXT_COLOR)

    cy += PILL_H + BOX_GAP

    # ── 3 rows (fill remaining space equally) ─────────────────────────────
    row_w         = rect.width - 2 * PADDING_X
    available_h   = rect.y + rect.height - PADDING_Y - cy
    row_h         = (available_h - 2 * BOX_GAP) / 3
    maneuvers     = self._get_maneuvers() if self._destination else []

    new_rects = []
    for i in range(3):
      ry = cy + i * (row_h + BOX_GAP)
      br = rl.Rectangle(cx, ry, row_w, row_h)
      new_rects.append(br)

      bg = BOX_HOVER_COLOR if self._box_hovered == i else BOX_COLOR
      rl.draw_rectangle_rounded(br, BOX_RADIUS, 10, bg)

      if self._destination:
        if i < len(maneuvers):
          self._draw_maneuver_row(br, maneuvers[i], font, bold_font)
        elif i == 0 and not maneuvers:
          self._draw_waiting_gps_row(br, font)
      else:
        self._draw_shortcut_row(br, i, font, bold_font)

    self._box_rects = new_rects

  def _draw_shortcut_row(self, rect: rl.Rectangle, index: int, font, bold_font):
    label    = self._shortcut_labels[index]
    addr     = self._shortcut_addrs[index]
    icon_keys = ['home', 'work', 'favorite']
    icon_tex  = self._shortcut_icons.get(icon_keys[index])

    pad_x    = 18
    circle_r = ROW_ICON_SIZE // 2 + 12
    icon_cx  = int(rect.x + pad_x + circle_r)
    icon_cy  = int(rect.y + rect.height / 2)

    rl.draw_circle(icon_cx, icon_cy, circle_r, rl.Color(55, 60, 70, 255))
    if icon_tex is not None:
      draw_scale = 0.72 if index < 2 else 0.88
      draw_half  = ROW_ICON_SIZE * draw_scale / 2
      ix = int(icon_cx - draw_half)
      iy = int(icon_cy - draw_half)
      rl.draw_texture_ex(icon_tex, rl.Vector2(ix, iy), 0.0, draw_scale, rl.WHITE)

    text_x   = rect.x + pad_x + circle_r * 2 + 14
    label_sz = measure_text_cached(bold_font, label, 46)

    if addr:
      short_addr   = addr if len(addr) <= 26 else addr[:24] + "…"
      addr_sz      = measure_text_cached(font, short_addr, 36)
      total_text_h = label_sz.y + 6 + addr_sz.y
      label_y      = int(rect.y + (rect.height - total_text_h) / 2)
      addr_y       = int(label_y + label_sz.y + 6)
      rl.draw_text_ex(bold_font, label, rl.Vector2(text_x, label_y), 46, 0, BOX_VALUE_COLOR)
      rl.draw_text_ex(font, short_addr, rl.Vector2(text_x, addr_y), 36, 0, BOX_LABEL_COLOR)
    else:
      label_y = int(rect.y + (rect.height - label_sz.y) / 2)
      rl.draw_text_ex(bold_font, label, rl.Vector2(text_x, label_y), 46, 0, BOX_VALUE_COLOR)

  def _draw_waiting_gps_row(self, rect: rl.Rectangle, font):
    text = "Waiting for GPS…"
    sz = measure_text_cached(font, text, 36)
    tx = int(rect.x + 20)
    ty = int(rect.y + (rect.height - sz.y) / 2)
    rl.draw_text_ex(font, text, rl.Vector2(tx, ty), 36, 0, BOX_LABEL_COLOR)

  def _draw_maneuver_row(self, rect: rl.Rectangle, maneuver, font, bold_font):
    pad_x     = 20
    dist_text = _format_distance(maneuver.distance)
    dist_sz   = measure_text_cached(bold_font, dist_text, 40)
    dist_y    = int(rect.y + (rect.height - dist_sz.y) / 2)
    rl.draw_text_ex(bold_font, dist_text, rl.Vector2(rect.x + pad_x, dist_y), 40, 0, MANEUVER_COLOR)

    instr   = maneuver.instruction or f"{maneuver.type} {maneuver.modifier}".strip()
    text_x  = rect.x + pad_x + dist_sz.x + 20
    avail_w = rect.width - (text_x - rect.x) - pad_x

    words = instr.split()
    lines, line = [], []
    for word in words:
      test    = " ".join(line + [word])
      test_sz = measure_text_cached(font, test, 30)
      if test_sz.x > avail_w and line:
        lines.append(" ".join(line))
        line = [word]
      else:
        line.append(word)
    if line:
      lines.append(" ".join(line))
    lines = lines[:2]

    total_h = len(lines) * 34
    text_y  = int(rect.y + (rect.height - total_h) / 2)
    for ln in lines:
      rl.draw_text_ex(font, ln, rl.Vector2(text_x, text_y), 30, 0, BOX_VALUE_COLOR)
      text_y += 34
