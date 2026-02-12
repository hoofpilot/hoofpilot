import pyray as rl
import math
from importlib.resources import as_file, files
from openpilot.common.params import Params
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget

ASSETS_DIR = files("openpilot.selfdrive").joinpath("assets")
MONO_FONT = ASSETS_DIR.joinpath("fonts").joinpath("JetBrainsMono-Medium.ttf")


class ExperimentalModeButton(Widget):
  def __init__(self):
    super().__init__()

    self.params = Params()
    self.experimental_mode = self.params.get_bool("ExperimentalMode")
    self.openpilot_enabled = self.params.get_bool("OpenpilotEnabledToggle")
    self._card_gap = 18
    self._card_radius = 0.083
    self._ring_radius = 22
    self._ring_thickness = 6
    self._text_size = 75
    self._font_load_size = 150
    self._text_margin_x = 28
    self._text_margin_y = 18
    self._mono_font = None

  def _ensure_mono_font(self):
    if self._mono_font is not None:
      return
    try:
      with as_file(MONO_FONT) as mono_path:
        self._mono_font = rl.load_font_ex(mono_path.as_posix(), self._font_load_size, None, 0)
        rl.set_texture_filter(self._mono_font.texture, rl.TextureFilter.TEXTURE_FILTER_BILINEAR)
    except Exception:
      self._mono_font = gui_app.font(FontWeight.BOLD)

  def show_event(self):
    self.experimental_mode = self.params.get_bool("ExperimentalMode")
    self.openpilot_enabled = self.params.get_bool("OpenpilotEnabledToggle")

  def _handle_mouse_release(self, mouse_pos):
    for i, mode_rect in enumerate(self._mode_rects(self._rect)):
      if not rl.check_collision_point_rec(mouse_pos, mode_rect):
        continue
      if i == 0:
        # Chill mode: hoofpilot enabled, experimental disabled.
        self.openpilot_enabled = True
        self.experimental_mode = False
        self.params.put_bool("OpenpilotEnabledToggle", True)
        self.params.put_bool("ExperimentalMode", False)
      elif i == 1:
        # Experimental mode: hoofpilot enabled, experimental enabled.
        self.openpilot_enabled = True
        self.experimental_mode = True
        self.params.put_bool("OpenpilotEnabledToggle", True)
        self.params.put_bool("ExperimentalMode", True)
      elif i == 2:
        # Stock ADAS mode: disable hoofpilot entirely.
        self.openpilot_enabled = False
        self.experimental_mode = False
        self.params.put_bool("OpenpilotEnabledToggle", False)
        self.params.put_bool("ExperimentalMode", False)
      break

  def _mode_rects(self, rect: rl.Rectangle) -> list[rl.Rectangle]:
    card_h = (rect.height - 2 * self._card_gap) / 3
    return [
      rl.Rectangle(rect.x, rect.y, rect.width, card_h),
      rl.Rectangle(rect.x, rect.y + card_h + self._card_gap, rect.width, card_h),
      rl.Rectangle(rect.x, rect.y + 2 * (card_h + self._card_gap), rect.width, card_h),
    ]

  def _draw_rounded_gradient(self, rect: rl.Rectangle, roundness: float, left_color: rl.Color, right_color: rl.Color):
    w = max(1, int(rect.width))
    h = max(1, int(rect.height))
    r = int(max(1.0, roundness * min(w, h) * 0.5))
    x0 = int(rect.x)
    y0 = int(rect.y)

    for i in range(w):
      t = i / max(1, w - 1)
      color = rl.Color(
        int(left_color.r + (right_color.r - left_color.r) * t),
        int(left_color.g + (right_color.g - left_color.g) * t),
        int(left_color.b + (right_color.b - left_color.b) * t),
        int(left_color.a + (right_color.a - left_color.a) * t),
      )

      cut = 0
      if i < r:
        dx = r - i
        cut = int(r - math.sqrt(max(0, r * r - dx * dx)))
      elif i >= w - r:
        dx = i - (w - r - 1)
        cut = int(r - math.sqrt(max(0, r * r - dx * dx)))

      y_start = y0 + cut
      y_end = y0 + h - cut
      if y_end > y_start:
        rl.draw_line(x0 + i, y_start, x0 + i, y_end, color)

  def _draw_card(self, rect: rl.Rectangle, label: str, selected: bool, left_color: rl.Color, right_color: rl.Color):
    self._draw_rounded_gradient(rect, self._card_radius, left_color, right_color)

    self._ensure_mono_font()
    text_x = rect.x + self._text_margin_x
    text_y = rect.y + self._text_margin_y
    text = tr(label)
    color = rl.Color(230, 236, 240, 255)
    # Faux-bold pass for JetBrains Mono Medium
    rl.draw_text_ex(self._mono_font, text, rl.Vector2(int(text_x), int(text_y)), self._text_size, 0, color)
    rl.draw_text_ex(self._mono_font, text, rl.Vector2(int(text_x + 1), int(text_y)), self._text_size, 0, color)

    cx = int(rect.x + rect.width - 44)
    cy = int(rect.y + rect.height / 2)
    ring_col = rl.Color(0, 0, 0, 255)
    inner_col = rl.Color(25, 25, 25, 255)
    rl.draw_circle(cx, cy, self._ring_radius, inner_col)
    rl.draw_circle_lines(cx, cy, self._ring_radius, ring_col)
    rl.draw_circle_lines(cx, cy, self._ring_radius - 1, ring_col)
    if selected:
      rl.draw_circle(cx, cy, self._ring_radius - self._ring_thickness, rl.Color(90, 255, 40, 255))

  def _render(self, rect):
    mode_rects = self._mode_rects(rect)
    self._draw_card(
      mode_rects[0],
      "chill mode",
      selected=self.openpilot_enabled and not self.experimental_mode,
      left_color=rl.Color(45, 222, 210, 255),
      right_color=rl.Color(6, 176, 225, 255),
    )
    self._draw_card(
      mode_rects[1],
      "Experimental Mode",
      selected=self.openpilot_enabled and self.experimental_mode,
      left_color=rl.Color(201, 92, 22, 255),
      right_color=rl.Color(183, 44, 27, 255),
    )
    self._draw_card(
      mode_rects[2],
      "Stock ADAS Mode",
      selected=not self.openpilot_enabled,
      left_color=rl.Color(44, 52, 62, 255),
      right_color=rl.Color(70, 82, 92, 255),
    )
