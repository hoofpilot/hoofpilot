import pyray as rl
from openpilot.common.params import Params
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget


class ExperimentalModeButton(Widget):
  def __init__(self):
    super().__init__()

    self.params = Params()
    self.experimental_mode = self.params.get_bool("ExperimentalMode")
    self._card_gap = 18
    self._card_radius = 0.06
    self._ring_radius = 22
    self._ring_thickness = 5

  def show_event(self):
    self.experimental_mode = self.params.get_bool("ExperimentalMode")

  def _handle_mouse_release(self, mouse_pos):
    for i, mode_rect in enumerate(self._mode_rects(self._rect)):
      if not rl.check_collision_point_rec(mouse_pos, mode_rect):
        continue
      if i == 0:
        self.experimental_mode = False
        self.params.put_bool("ExperimentalMode", False)
      elif i == 1:
        self.experimental_mode = True
        self.params.put_bool("ExperimentalMode", True)
      break

  def _mode_rects(self, rect: rl.Rectangle) -> list[rl.Rectangle]:
    card_h = (rect.height - 2 * self._card_gap) / 3
    return [
      rl.Rectangle(rect.x, rect.y, rect.width, card_h),
      rl.Rectangle(rect.x, rect.y + card_h + self._card_gap, rect.width, card_h),
      rl.Rectangle(rect.x, rect.y + 2 * (card_h + self._card_gap), rect.width, card_h),
    ]

  def _draw_card(self, rect: rl.Rectangle, label: str, selected: bool, left_color: rl.Color, right_color: rl.Color):
    # Fill with horizontal gradient by clipping rounded shape.
    rl.begin_scissor_mode(int(rect.x), int(rect.y), int(rect.width), int(rect.height))
    rl.draw_rectangle_gradient_h(int(rect.x), int(rect.y), int(rect.width), int(rect.height), left_color, right_color)
    rl.end_scissor_mode()

    border_col = rl.Color(255, 255, 255, 45)
    rl.draw_rectangle_rounded_lines_ex(rect, self._card_radius, 20, 3, border_col)

    text_x = rect.x + 28
    text_y = rect.y + (rect.height - 54) / 2
    rl.draw_text_ex(gui_app.font(FontWeight.BOLD), tr(label), rl.Vector2(int(text_x), int(text_y)), 54, 0, rl.Color(230, 236, 240, 255))

    cx = int(rect.x + rect.width - 44)
    cy = int(rect.y + rect.height / 2)
    ring_col = rl.Color(20, 20, 20, 255)
    rl.draw_circle_lines(cx, cy, self._ring_radius, ring_col)
    rl.draw_circle_lines(cx, cy, self._ring_radius - 1, ring_col)
    if selected:
      rl.draw_circle(cx, cy, self._ring_radius - self._ring_thickness, rl.Color(90, 255, 40, 255))

  def _render(self, rect):
    mode_rects = self._mode_rects(rect)
    self._draw_card(
      mode_rects[0],
      "chill mode",
      selected=not self.experimental_mode,
      left_color=rl.Color(45, 222, 210, 255),
      right_color=rl.Color(6, 176, 225, 255),
    )
    self._draw_card(
      mode_rects[1],
      "Experimental Mode",
      selected=self.experimental_mode,
      left_color=rl.Color(201, 92, 22, 255),
      right_color=rl.Color(183, 44, 27, 255),
    )
    self._draw_card(
      mode_rects[2],
      "Stock ADAS Mode",
      selected=False,
      left_color=rl.Color(44, 52, 62, 255),
      right_color=rl.Color(70, 82, 92, 255),
    )
