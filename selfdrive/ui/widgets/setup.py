import pyray as rl
from openpilot.common.time_helpers import system_time_valid
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.selfdrive.ui.widgets.pairing_dialog import PairingDialog
from openpilot.system.ui.lib.application import FontWeight, gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.lib.wrap_text import wrap_text
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.button import Button, ButtonStyle
from openpilot.system.ui.widgets.confirm_dialog import alert_dialog
from openpilot.system.ui.widgets.label import gui_label


class SetupWidget(Widget):
  def __init__(self):
    super().__init__()
    self._pairing_dialog: PairingDialog | None = None
    self._pair_device_btn = Button(lambda: tr("Pair device"), self._show_pairing, button_style=ButtonStyle.PRIMARY)

  def _render(self, rect: rl.Rectangle):
    if ui_state.prime_state.is_paired():
      return

    self._render_setup_card(rect, title=tr("Finish Setup"), description=tr("Pair your device with Konik Stable."))

  def _render_setup_card(self, rect: rl.Rectangle, title: str, description: str):
    # Match Trips card styling
    rl.draw_rectangle_rounded(rect, 0.05, 10, rl.Color(30, 30, 30, 255))

    content_w = rect.width - 64
    x = rect.x + 32
    y = rect.y + 36

    gui_label(rl.Rectangle(x, y, content_w, 88), title, 75, font_weight=FontWeight.BOLD,
              alignment=rl.GuiTextAlignment.TEXT_ALIGN_CENTER)
    y += 120

    desc_font = gui_app.font(FontWeight.NORMAL)
    wrapped = wrap_text(desc_font, description, 58, int(content_w))
    line_y = y
    for line in wrapped[:3]:
      gui_label(rl.Rectangle(x, line_y, content_w, 62), line, 58,
                alignment=rl.GuiTextAlignment.TEXT_ALIGN_CENTER)
      line_y += 62

    button_rect = rl.Rectangle(rect.x + 40, rect.y + rect.height - 170, rect.width - 80, 120)
    self._pair_device_btn.render(button_rect)

  def _show_pairing(self):
    if not system_time_valid():
      dlg = alert_dialog(tr("Please connect to Wi-Fi to complete initial pairing"))
      gui_app.set_modal_overlay(dlg)
      return

    if not self._pairing_dialog:
      self._pairing_dialog = PairingDialog()
    gui_app.set_modal_overlay(self._pairing_dialog, lambda result: setattr(self, '_pairing_dialog', None))

  def __del__(self):
    if self._pairing_dialog:
      del self._pairing_dialog
