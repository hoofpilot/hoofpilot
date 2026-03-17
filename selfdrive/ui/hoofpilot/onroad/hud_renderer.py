"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pyray as rl

from openpilot.common.constants import CV
from openpilot.selfdrive.ui.mici.onroad.torque_bar import TorqueBar
from openpilot.selfdrive.ui.hoofpilot.onroad.developer_ui import DeveloperUiRenderer
from openpilot.selfdrive.ui.hoofpilot.onroad.road_name import RoadNameRenderer
from openpilot.selfdrive.ui.hoofpilot.onroad.rocket_fuel import RocketFuel
from openpilot.selfdrive.ui.hoofpilot.onroad.speed_limit import SpeedLimitRenderer
from openpilot.selfdrive.ui.hoofpilot.onroad.smart_cruise_control import SmartCruiseControlRenderer
from openpilot.selfdrive.ui.hoofpilot.onroad.circular_alerts import CircularAlertsRenderer
from openpilot.selfdrive.ui.hoofpilot.onroad.speed_renderer import SpeedRenderer
from openpilot.selfdrive.ui.hoofpilot.onroad.nav_banner import NavBannerRenderer
from openpilot.selfdrive.ui.ui_state import ui_state, UIStatus
from openpilot.selfdrive.ui.onroad.hud_renderer import HudRenderer, UI_CONFIG, FONT_SIZES, COLORS, CRUISE_DISABLED_CHAR
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.lib.text_measure import measure_text_cached


class HudRendererSP(HudRenderer):
  def __init__(self):
    super().__init__()
    self.developer_ui = DeveloperUiRenderer()
    self.road_name_renderer = RoadNameRenderer()
    self.rocket_fuel = RocketFuel()
    self.speed_limit_renderer = SpeedLimitRenderer()
    self.smart_cruise_control_renderer = SmartCruiseControlRenderer()
    self.circular_alerts_renderer = CircularAlertsRenderer()
    self.speed_renderer = SpeedRenderer()
    self.nav_banner = NavBannerRenderer()
    self._torque_bar = TorqueBar(scale=3.0, always=True)

    self.pcm_cruise_speed: bool = True
    self.show_icbm_status: bool = False
    self.icbm_active_counter: int = 0
    self.speed_cluster: float = 0.0
    self.speed_conv: float = CV.MS_TO_KPH if ui_state.is_metric else CV.MS_TO_MPH

  def _update_state(self) -> None:
    self.nav_banner.update()

    if ui_state.sm.recv_frame["carState"] < ui_state.started_frame:
      return

    if ui_state.CP_SP is not None:
      self.pcm_cruise_speed = ui_state.CP_SP.pcmCruiseSpeed
    self.speed_conv = CV.MS_TO_KPH if ui_state.is_metric else CV.MS_TO_MPH
    self.speed_cluster = ui_state.sm['carState'].cruiseState.speedCluster * self.speed_conv

    super()._update_state()
    self.road_name_renderer.update()
    self.speed_limit_renderer.update()
    self.smart_cruise_control_renderer.update()
    self.circular_alerts_renderer.update()
    self.speed_renderer.update()

  def _get_icbm_status(self):
    if not self.pcm_cruise_speed and ui_state.sm['carControl'].enabled:
      if round(self.set_speed) != round(self.speed_cluster):
        self.icbm_active_counter = 3 * gui_app.target_fps  # 3 seconds usually
      elif self.icbm_active_counter > 0:
        self.icbm_active_counter -= 1
    else:
      self.icbm_active_counter = 0

    self.show_icbm_status = self.icbm_active_counter > 0

  def _draw_set_speed(self, rect: rl.Rectangle) -> None:
    self._get_icbm_status()

    set_speed_width = UI_CONFIG.set_speed_width_metric if ui_state.is_metric else UI_CONFIG.set_speed_width_imperial
    x = rect.x + 60 + (UI_CONFIG.set_speed_width_imperial - set_speed_width) // 2
    y = rect.y + 45

    max_color = COLORS.GREY
    set_speed_color = COLORS.DARK_GREY
    if self.is_cruise_set:
      set_speed_color = COLORS.WHITE
      if ui_state.status == UIStatus.ENGAGED:
        max_color = COLORS.ENGAGED
      elif ui_state.status == UIStatus.DISENGAGED:
        max_color = COLORS.DISENGAGED
      elif ui_state.status == UIStatus.OVERRIDE:
        max_color = COLORS.OVERRIDE

    if self.nav_banner.is_active:
      # Combined nav box: current speed (top) + divider + MAX + cruise (bottom)
      _NAV_DIV_Y   = 118   # divider position
      _NAV_TOTAL_H = 210   # total box height
      _MAX_GREEN   = rl.Color(72, 205, 110, 255)

      set_speed_rect = rl.Rectangle(x, y, set_speed_width, _NAV_TOTAL_H)
      rl.draw_rectangle_rounded(set_speed_rect, 0.35, 10, COLORS.BLACK_TRANSLUCENT)
      rl.draw_rectangle_rounded_lines_ex(set_speed_rect, 0.35, 10, 6, COLORS.BORDER_TRANSLUCENT)

      unit_text = tr("km/h") if ui_state.is_metric else tr("mph")
      cur_str = str(round(self.speed_renderer.speed))
      cur_sz = measure_text_cached(self._font_bold, cur_str, 68)
      rl.draw_text_ex(self._font_bold, cur_str, rl.Vector2(x + (set_speed_width - cur_sz.x) / 2, y + 14), 68, 0, COLORS.WHITE)

      unit_sz = measure_text_cached(self._font_semi_bold, unit_text, 24)
      rl.draw_text_ex(self._font_semi_bold, unit_text, rl.Vector2(x + (set_speed_width - unit_sz.x) / 2, y + 88), 24, 0, COLORS.WHITE_TRANSLUCENT)

      rl.draw_line(int(x + 12), int(y + _NAV_DIV_Y), int(x + set_speed_width - 12), int(y + _NAV_DIV_Y), rl.Color(255, 255, 255, 40))

      max_text = tr("MAX")
      max_sz = measure_text_cached(self._font_semi_bold, max_text, 28)
      rl.draw_text_ex(self._font_semi_bold, max_text, rl.Vector2(x + (set_speed_width - max_sz.x) / 2, y + _NAV_DIV_Y + 8), 28, 0, _MAX_GREEN)

      set_speed_text = CRUISE_DISABLED_CHAR if not self.is_cruise_set else str(round(self.set_speed))
      ss_sz = measure_text_cached(self._font_bold, set_speed_text, 62)
      rl.draw_text_ex(self._font_bold, set_speed_text, rl.Vector2(x + (set_speed_width - ss_sz.x) / 2, y + _NAV_DIV_Y + 44), 62, 0, set_speed_color)
    else:
      set_speed_rect = rl.Rectangle(x, y, set_speed_width, UI_CONFIG.set_speed_height)
      rl.draw_rectangle_rounded(set_speed_rect, 0.35, 10, COLORS.BLACK_TRANSLUCENT)
      rl.draw_rectangle_rounded_lines_ex(set_speed_rect, 0.35, 10, 6, COLORS.BORDER_TRANSLUCENT)

      max_str_size = 60 if self.show_icbm_status else 40
      max_str_y = 15 if self.show_icbm_status else 27

      max_text = str(round(self.speed_cluster)) if self.show_icbm_status else tr("MAX")
      max_text_width = measure_text_cached(self._font_semi_bold, max_text, max_str_size).x
      rl.draw_text_ex(
        self._font_semi_bold,
        max_text,
        rl.Vector2(x + (set_speed_width - max_text_width) / 2, y + max_str_y),
        max_str_size,
        0,
        max_color,
      )

      set_speed_text = CRUISE_DISABLED_CHAR if not self.is_cruise_set else str(round(self.set_speed))
      speed_text_width = measure_text_cached(self._font_bold, set_speed_text, FONT_SIZES.set_speed).x
      rl.draw_text_ex(
        self._font_bold,
        set_speed_text,
        rl.Vector2(x + (set_speed_width - speed_text_width) / 2, y + 81),
        FONT_SIZES.set_speed,
        0,
        set_speed_color,
      )

  def _draw_current_speed(self, rect: rl.Rectangle) -> None:
    if self.nav_banner.is_active:
      return
    self.speed_renderer.render(rect)

  def _render(self, rect: rl.Rectangle) -> None:
    super()._render(rect)

    if ui_state.torque_bar and ui_state.sm['controlsState'].lateralControlState.which() != 'angleState':
      torque_rect = rect
      if ui_state.developer_ui in (DeveloperUiRenderer.DEV_UI_BOTTOM, DeveloperUiRenderer.DEV_UI_BOTH):
        torque_rect = rl.Rectangle(rect.x, rect.y, rect.width, rect.height - DeveloperUiRenderer.BOTTOM_BAR_HEIGHT)
      self._torque_bar.render(torque_rect)

    self.developer_ui.render(rect)
    self.road_name_renderer.render(rect)
    self.speed_limit_renderer.render(rect)
    self.smart_cruise_control_renderer.render(rect)
    self.nav_banner.render(rect)
    self.circular_alerts_renderer.render(rect)
    self.rocket_fuel.render(rect, ui_state.sm)

