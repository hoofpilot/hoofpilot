"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

import pyray as rl

from openpilot.selfdrive.ui.onroad.hud_renderer import COLORS, UI_CONFIG
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets import Widget

METER_TO_MILE = 0.000621371


@dataclass(frozen=True)
class NavigationWidgetConfig:
  width: int = 188
  height: int = 188
  icon_size: int = 102
  icon_top_margin: int = 10
  text_size: int = 54
  text_bottom_margin: int = 18
  x_spacing_from_speed_limit: int = 28
  y: int = 45


class NavigationRenderer(Widget):
  def __init__(self):
    super().__init__()
    self._config = NavigationWidgetConfig()
    self._font_bold: rl.Font = gui_app.font(FontWeight.BOLD)

    self._assets_dir = Path(__file__).resolve().parents[4] / "selfdrive" / "assets" / "navigation"
    self._available_assets = {path.stem for path in self._assets_dir.glob("*.png")} if self._assets_dir.exists() else set()
    self._texture_cache = {}

    self._visible: bool = False
    self._distance_m: float = 0.0
    self._icon_key: str = "direction_invalid"

  def update(self):
    sm = ui_state.sm
    if sm.recv_frame["carState"] < ui_state.started_frame:
      self._visible = False
      return

    if sm.updated["navigationd"]:
      nav_data = sm["navigationd"]
      self._visible = bool(nav_data.valid and len(nav_data.allManeuvers) > 0)
      if not self._visible:
        return

      maneuver_index = 1 if len(nav_data.allManeuvers) > 1 else 0
      maneuver = nav_data.allManeuvers[maneuver_index]
      self._distance_m = max(float(maneuver.distance), 0.0)
      self._icon_key = self._resolve_icon_key(str(maneuver.type), str(maneuver.modifier), str(maneuver.instruction))
    elif not sm.alive["navigationd"] or not sm.valid["navigationd"]:
      self._visible = False

  def _render(self, rect: rl.Rectangle):
    if not self._visible:
      return

    box_rect = self._get_widget_rect(rect)

    rl.draw_rectangle_rounded(box_rect, 0.18, 10, COLORS.BLACK_TRANSLUCENT)
    rl.draw_rectangle_rounded_lines_ex(box_rect, 0.18, 10, 4, COLORS.BORDER_TRANSLUCENT)

    icon_texture = self._get_texture(self._icon_key)
    if icon_texture is not None:
      icon_pos = rl.Vector2(
        box_rect.x + (box_rect.width - icon_texture.width) / 2,
        box_rect.y + self._config.icon_top_margin,
      )
      rl.draw_texture(icon_texture, int(icon_pos.x), int(icon_pos.y), rl.WHITE)

    distance_text = self._format_distance(self._distance_m)
    text_size = measure_text_cached(self._font_bold, distance_text, self._config.text_size)
    text_pos = rl.Vector2(
      box_rect.x + (box_rect.width - text_size.x) / 2,
      box_rect.y + box_rect.height - text_size.y - self._config.text_bottom_margin,
    )
    rl.draw_text_ex(self._font_bold, distance_text, text_pos, self._config.text_size, 0, rl.WHITE)

  def _get_widget_rect(self, rect: rl.Rectangle) -> rl.Rectangle:
    set_speed_width = UI_CONFIG.set_speed_width_metric if ui_state.is_metric else UI_CONFIG.set_speed_width_imperial
    speed_limit_x = rect.x + 60 + set_speed_width + 30 - 6
    speed_limit_right = speed_limit_x + set_speed_width
    return rl.Rectangle(
      speed_limit_right + self._config.x_spacing_from_speed_limit,
      rect.y + self._config.y,
      self._config.width,
      self._config.height,
    )

  @staticmethod
  def _format_distance(distance_m: float) -> str:
    if ui_state.is_metric:
      distance_km = distance_m / 1000.0
      if 0.0 < distance_km < 0.1:
        distance_km = 0.1
      return f"{distance_km:.1f} km"

    distance_mi = distance_m * METER_TO_MILE
    if 0.0 < distance_mi < 0.1:
      distance_mi = 0.1
    return f"{distance_mi:.1f} mi"

  def _get_texture(self, key: str):
    if key in self._texture_cache:
      return self._texture_cache[key]

    if key not in self._available_assets:
      return None

    texture_path = self._assets_dir / f"{key}.png"
    texture = gui_app.texture(texture_path.as_posix(), self._config.icon_size, self._config.icon_size, keep_aspect_ratio=True)
    self._texture_cache[key] = texture
    return texture

  def _resolve_icon_key(self, maneuver_type: str, maneuver_modifier: str, instruction: str) -> str:
    normalized_type = self._normalize_key_component(maneuver_type)
    normalized_modifier = self._normalize_key_component(maneuver_modifier)

    instruction_normalized = instruction.lower().replace(" ", "")
    if normalized_modifier == "none" and ("u-turn" in instruction.lower() or "uturn" in instruction_normalized):
      normalized_modifier = "uturn"

    type_variants = [normalized_type]
    if normalized_type == "notification":
      type_variants.append("notificaiton")
    elif normalized_type == "notificaiton":
      type_variants.append("notification")

    candidates = []
    for type_variant in type_variants:
      if normalized_modifier and normalized_modifier != "none":
        candidates.append(f"direction_{type_variant}_{normalized_modifier}")
      candidates.append(f"direction_{type_variant}")

    candidates.extend(self._modifier_fallback_candidates(normalized_modifier))
    candidates.extend(("direction_continue_straight", "direction_continue", "direction_invalid"))

    for candidate in dict.fromkeys(candidates):
      if candidate in self._available_assets:
        return candidate

    return "direction_invalid"

  @staticmethod
  def _modifier_fallback_candidates(modifier: str) -> list[str]:
    if modifier in {"left", "slight_left", "sharp_left"}:
      return [f"direction_turn_{modifier}", "direction_turn_left"]
    if modifier in {"right", "slight_right", "sharp_right"}:
      return [f"direction_turn_{modifier}", "direction_turn_right"]
    if modifier == "straight":
      return ["direction_turn_straight"]
    if modifier == "uturn":
      return ["direction_uturn", "direction_continue_uturn"]
    return []

  @staticmethod
  def _normalize_key_component(value: str) -> str:
    normalized = value.strip().replace("-", "_").replace(" ", "_")
    normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", normalized)
    normalized = re.sub(r"_+", "_", normalized)
    return normalized.lower()
