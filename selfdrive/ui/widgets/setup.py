import pyray as rl
from openpilot.common.time_helpers import system_time_valid
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.selfdrive.ui.widgets.pairing_dialog import PairingDialog
from openpilot.system.ui.lib.application import gui_app, FontWeight, FONT_SCALE
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.lib.wrap_text import wrap_text
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.confirm_dialog import alert_dialog
from openpilot.system.ui.widgets.button import Button, ButtonStyle


class SetupWidget(Widget):
  def __init__(self):
    super().__init__()
    self._pair_device_btn = Button(lambda: tr("Pair device"), self._show_pairing, button_style=ButtonStyle.PRIMARY)

  def _render(self, rect: rl.Rectangle):
    if not ui_state.prime_state.is_paired():
      self._render_registration(rect)

  def _render_registration(self, rect: rl.Rectangle):
    rl.draw_rectangle_rounded(rect, 0.05, 10, rl.Color(30, 30, 30, 255))

    content_w = rect.width - 64
    x = rect.x + 32
    w = content_w

    font = gui_app.font(FontWeight.BOLD)
    title = tr("Finish Setup")
    desc = tr("Pair your device with Konik Stable.")
    light_font = gui_app.font(FontWeight.NORMAL)
    wrapped = wrap_text(light_font, desc, 50, int(w))

    title_h = 75
    title_gap = 38
    desc_h = len(wrapped) * int(50 * FONT_SCALE)
    btn_gap = 30
    btn_h = 200
    total_h = title_h + title_gap + desc_h + btn_gap + btn_h
    y = rect.y + (rect.height - total_h) / 2

    rl.draw_text_ex(font, title, rl.Vector2(x, y), title_h, 0, rl.WHITE)
    y += title_h + title_gap

    for line in wrapped:
      rl.draw_text_ex(light_font, line, rl.Vector2(x, y), 50, 0, rl.WHITE)
      y += int(50 * FONT_SCALE)

    button_rect = rl.Rectangle(x, y + btn_gap, w, btn_h)
    self._pair_device_btn.render(button_rect)

  @staticmethod
  def _show_pairing():
    if not system_time_valid():
      dlg = alert_dialog(tr("Please connect to Wi-Fi to complete initial pairing"))
      gui_app.push_widget(dlg)
      return

    gui_app.push_widget(PairingDialog())
