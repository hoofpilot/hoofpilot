"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import os
from collections.abc import Callable
from dataclasses import dataclass

import pyray as rl

SHOW_MOUSE_COORDS = os.getenv("SHOW_MOUSE_COORDS") == "1"
SUNNYPILOT_UI = os.getenv("SUNNYPILOT_UI", "1") == "1"

OFFROAD_FPS = int(os.getenv("OFFROAD_FPS", "59"))
ONROAD_FPS = int(os.getenv("ONROAD_FPS", "20"))


@dataclass
class ModalOverlay:
  overlay: object = None
  callback: Callable | None = None


class GuiApplicationExt:
  def __init__(self):
    self._show_mouse_coords = SHOW_MOUSE_COORDS
    self._modal_overlay = ModalOverlay()
    self._modal_overlay_shown = False
    self._modal_overlay_tick: Callable | None = None

  @staticmethod
  def sunnypilot_ui() -> bool:
    return SUNNYPILOT_UI

  def _draw_mouse_coordinates(self, font):
    coords_text = f"X:{int(rl.get_mouse_x())}, Y:{int(rl.get_mouse_y())}"

    green_color = rl.Color(0, 159, 47, 255)  # Match the green color of FPS counter

    # Calculate text width to position it at the right edge; estimate width based on text length
    # Each character is approximately 10-12 pixels wide at font size 20
    estimated_text_width = len(coords_text) * 11

    # Position text at the top right corner, 10px from the top
    screen_width = self._scaled_width if self._scale != 1.0 else self._width
    text_pos = rl.Vector2(screen_width - estimated_text_width - 10, 6)

    # Draw the text
    rl.draw_text_ex(font, coords_text, text_pos, 20, 0, green_color)

  def set_show_mouse_coords(self, show: bool):
    self._show_mouse_coords = show

  def set_target_fps(self, fps: int):
    fps = max(1, int(fps))
    if fps == self._target_fps:
      return
    self._target_fps = fps
    if rl.is_window_ready():
      from openpilot.system.ui.lib.application import OFFSCREEN
      rl.set_target_fps(0 if OFFSCREEN else fps)

  def set_modal_overlay(self, overlay, callback: Callable | None = None):
    if self._modal_overlay.overlay is not None:
      if hasattr(self._modal_overlay.overlay, 'hide_event'):
        self._modal_overlay.overlay.hide_event()
      if self._modal_overlay.callback is not None:
        self._modal_overlay.callback(-1)
    self._modal_overlay = ModalOverlay(overlay, callback)
    self._modal_overlay_shown = False

  def set_modal_overlay_tick(self, tick_function: Callable | None):
    self._modal_overlay_tick = tick_function

  def _handle_modal_overlay(self) -> bool:
    if self._modal_overlay.overlay:
      if hasattr(self._modal_overlay.overlay, 'render'):
        result = self._modal_overlay.overlay.render(rl.Rectangle(0, 0, self.width, self.height))
      elif callable(self._modal_overlay.overlay):
        result = self._modal_overlay.overlay()
      else:
        raise Exception

      if not self._modal_overlay_shown and hasattr(self._modal_overlay.overlay, 'show_event'):
        self._modal_overlay.overlay.show_event()
        self._modal_overlay_shown = True

      if result >= 0:
        original_modal = self._modal_overlay
        self._modal_overlay = ModalOverlay()
        if hasattr(original_modal.overlay, 'hide_event'):
          original_modal.overlay.hide_event()
        if original_modal.callback is not None:
          original_modal.callback(result)
      return True
    else:
      self._modal_overlay_shown = False
      return False
