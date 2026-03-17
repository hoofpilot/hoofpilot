"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from __future__ import annotations

import pyray as rl
from types import SimpleNamespace

from openpilot.common.constants import CV
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.text_measure import measure_text_cached

# ── Dev override — always show the banner with fake data ─────────────────────
_FORCE_SHOW = True
_FAKE_MANEUVERS = [
  SimpleNamespace(distance=482.0,  type='turn', modifier='right',       instruction='Emory Street'),
  SimpleNamespace(distance=1609.0, type='turn', modifier='slight_left',  instruction='Pacific Coast Highway'),
]
_FAKE_BANNER_TEXT = 'Emory Street'

# ── Asset path ──────────────────────────────────────────────────────────────
_NAV_ASSETS = "../../hoofpilot/selfdrive/assets/navigation/"

# ── Colours ─────────────────────────────────────────────────────────────────
_BG        = rl.Color(26, 26, 26, 185)
_WHITE     = rl.Color(255, 255, 255, 255)
_GREY      = rl.Color(175, 180, 190, 200)
_THEN_GREY = rl.Color(160, 165, 175, 180)

# ── Layout ───────────────────────────────────────────────────────────────────
_BANNER_Y_OFFSET = 60    # from rect.y (matches set-speed box top + 20 px)
_BANNER_H        = 216   # same height as the white speed-limit sign
_SECTION_RADIUS  = 0.35  # same corner radius as the speed-limit signs
_CENTER_W        = 620   # width of the main maneuver section
_THEN_W          = 185   # width of the "Then" preview section
_SECTION_GAP     = 10    # gap between centre and "then"
_ICON_SIZE       = 95    # maneuver icon in center section
_ICON_THEN_SIZE  = 62    # maneuver icon in "then" section
_PAD             = 18    # inner horizontal padding


def _icon_path(type_: str, modifier: str) -> str:
  """Map maneuver type + modifier to a navigation asset filename."""
  t = type_.strip().replace(' ', '_').replace('-', '_')
  m = modifier.strip().replace(' ', '_').replace('-', '_')
  if m and m not in ('none', 'straight'):
    return f"{_NAV_ASSETS}direction_{t}_{m}.png"
  # Try type + straight, then bare type
  for name in (f"direction_{t}_straight", f"direction_{t}"):
    return f"{_NAV_ASSETS}{name}.png"
  return f"{_NAV_ASSETS}direction_continue.png"


class NavBannerRenderer:
  def __init__(self):
    self._font_bold   = gui_app.font(FontWeight.BOLD)
    self._font_medium = gui_app.font(FontWeight.MEDIUM)

    # Lazily loaded textures keyed by (type, modifier, size)
    self._icon_cache: dict[tuple, rl.Texture | None] = {}

    self._maneuvers: list = []
    self._banner_text: str = ''

  # ── Public API ──────────────────────────────────────────────────────────

  @property
  def is_active(self) -> bool:
    return len(self._maneuvers) > 0

  def update(self) -> None:
    try:
      nav = ui_state.sm['navigationd']
      self._maneuvers = list(nav.allManeuvers)
      self._banner_text = nav.bannerInstructions or ''
      # Preload icons for the next two maneuvers to avoid stutter during render
      for m in self._maneuvers[:2]:
        self._get_icon(m.type, m.modifier, _ICON_SIZE)
        self._get_icon(m.type, m.modifier, _ICON_THEN_SIZE)
    except Exception:
      self._maneuvers = []
      self._banner_text = ''

    if _FORCE_SHOW and not self._maneuvers:
      self._maneuvers = _FAKE_MANEUVERS
      self._banner_text = _FAKE_BANNER_TEXT

  def render(self, rect: rl.Rectangle) -> None:
    if not self.is_active:
      return

    m0 = self._maneuvers[0]
    m1 = self._maneuvers[1] if len(self._maneuvers) > 1 else None

    y = rect.y + _BANNER_Y_OFFSET
    total_w = _CENTER_W + _SECTION_GAP + _THEN_W
    cx = rect.x + (rect.width - total_w) / 2

    # ── Single combined box ─────────────────────────────────────────────────
    banner_rect = rl.Rectangle(cx, y, total_w, _BANNER_H)
    rl.draw_rectangle_rounded(banner_rect, _SECTION_RADIUS, 10, _BG)

    # Vertical divider between centre and "Then"
    div_x = int(cx + _CENTER_W + _SECTION_GAP / 2)
    rl.draw_line(div_x, int(y + 16), div_x, int(y + _BANNER_H - 16), rl.Color(255, 255, 255, 40))

    # ── Centre section content ──────────────────────────────────────────────
    center_rect = rl.Rectangle(cx, y, _CENTER_W, _BANNER_H)
    self._draw_center(center_rect, m0)

    # ── "Then" section content ──────────────────────────────────────────────
    if m1 is not None:
      then_rect = rl.Rectangle(cx + _CENTER_W + _SECTION_GAP, y, _THEN_W, _BANNER_H)
      self._draw_then(then_rect, m1)

  # ── Private helpers ──────────────────────────────────────────────────────

  def _get_icon(self, type_: str, modifier: str, size: int) -> rl.Texture | None:
    key = (type_, modifier, size)
    if key in self._icon_cache:
      return self._icon_cache[key]
    try:
      path = _icon_path(type_, modifier)
      tex = gui_app.texture(path, size, size)
    except Exception:
      try:
        # Fallback: type only (e.g. direction_turn.png)
        t = type_.strip().replace(' ', '_')
        tex = gui_app.texture(f"{_NAV_ASSETS}direction_{t}.png", size, size)
      except Exception:
        try:
          tex = gui_app.texture(f"{_NAV_ASSETS}direction_continue.png", size, size)
        except Exception:
          tex = None
    self._icon_cache[key] = tex
    return tex

  @staticmethod
  def _format_dist(meters: float) -> str:
    if ui_state.is_metric:
      if meters < 1000:
        return f"{int(meters)} m"
      return f"{meters / 1000:.1f} km"
    feet = meters * 3.28084
    if feet < 900:
      return f"{int(round(feet / 50) * 50)} ft"
    return f"{meters * 0.000621371:.1f} mi"

  def _draw_center(self, rect: rl.Rectangle, m) -> None:
    icon_area_w = _ICON_SIZE + _PAD * 2

    # Maneuver icon — vertically center the icon+distance group
    icon = self._get_icon(m.type, m.modifier, _ICON_SIZE)
    icon_x = int(rect.x + _PAD)
    dist_text = self._format_dist(m.distance)
    dist_sz = measure_text_cached(self._font_medium, dist_text, 38)
    group_h = _ICON_SIZE + 6 + int(dist_sz.y)
    icon_y = int(rect.y + (rect.height - group_h) / 2)
    if icon:
      rl.draw_texture_ex(icon, rl.Vector2(icon_x, icon_y), 0.0, 1.0, _WHITE)

    # Distance label below icon
    dist_x = int(icon_x + (_ICON_SIZE - dist_sz.x) / 2)
    dist_y = icon_y + _ICON_SIZE + 6
    rl.draw_text_ex(self._font_medium, dist_text, rl.Vector2(dist_x, dist_y), 38, 0, _GREY)

    # Street / instruction name
    street = self._banner_text or m.instruction or ''
    avail_w = rect.width - icon_area_w - _PAD

    street_sz = 54
    sz = measure_text_cached(self._font_bold, street, street_sz)
    # Truncate if needed
    while sz.x > avail_w and len(street) > 3:
      street = street[:-1]
      sz = measure_text_cached(self._font_bold, street + '\u2026', street_sz)
    if street != (self._banner_text or m.instruction or ''):
      street += '\u2026'

    sz = measure_text_cached(self._font_bold, street, street_sz)
    text_x = rect.x + icon_area_w
    text_y = int(rect.y + (rect.height - sz.y) / 2)
    rl.draw_text_ex(self._font_bold, street, rl.Vector2(text_x, text_y), street_sz, 0, _WHITE)

  def _draw_then(self, rect: rl.Rectangle, m) -> None:
    # "Then" label near the top, icon just below
    then_sz = measure_text_cached(self._font_medium, 'Then', 34)
    then_y  = int(rect.y + 18)
    then_x  = int(rect.x + (rect.width - then_sz.x) / 2)
    rl.draw_text_ex(self._font_medium, 'Then', rl.Vector2(then_x, then_y), 34, 0, _THEN_GREY)

    # Next maneuver icon below the label
    icon = self._get_icon(m.type, m.modifier, _ICON_THEN_SIZE)
    if icon:
      icon_x = int(rect.x + (rect.width - _ICON_THEN_SIZE) / 2)
      icon_y = then_y + int(then_sz.y) + 8
      rl.draw_texture_ex(icon, rl.Vector2(icon_x, icon_y), 0.0, 1.0, _WHITE)
