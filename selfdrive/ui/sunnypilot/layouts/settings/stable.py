import hashlib
import hmac
import os

from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.input_dialog import InputDialogSP
from openpilot.system.ui.sunnypilot.widgets.list_view import dual_button_item_sp, button_item_sp, toggle_item_sp, Spacer
from openpilot.system.ui.widgets import DialogResult
from openpilot.system.ui.widgets.confirm_dialog import ConfirmDialog, alert_dialog
from openpilot.system.ui.widgets.button import ButtonStyle, Button
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.scroller_tici import Scroller


class StableLayout(Widget):
  def __init__(self):
    super().__init__()

    if not self._remote_pin_is_set():
      # Enforce "PIN first": keep remote access features off until a PIN is configured.
      ui_state.params.put_bool("LiveViewEnabled", False)
      ui_state.params.put_bool("RemoteSshEnabled", False)
      ui_state.params.put_bool("LiveView", False)

    self._reset_pin_buttons = dual_button_item_sp(
      left_text=lambda: tr("Reset PIN"),
      right_text=lambda: "",
      left_callback=self._on_reset_pin_pressed,
      right_callback=None,
      enabled=lambda: ui_state.is_offroad() and self._remote_pin_is_set(),
      border_radius=20,
    )
    self._reset_pin_btn: Button = self._reset_pin_buttons.action_item.left_button
    self._reset_pin_btn.set_button_style(ButtonStyle.DANGER)
    self._reset_pin_buttons.action_item.right_button.set_visible(False)

    self._remote_pin_button = button_item_sp(
      title=lambda: tr("PIN"),
      button_text=self._remote_pin_button_text,
      description=lambda: tr("Set or change the PIN required to use Remote SSH and Live View from Konik Stable."),
      callback=self._on_remote_pin_pressed,
      enabled=lambda: ui_state.is_offroad(),
    )

    self._live_view_toggle = toggle_item_sp(
      title=lambda: tr("Live View"),
      description=lambda: tr("Allow remote view inside your car from Konik Stable."),
      initial_state=ui_state.params.get_bool("LiveViewEnabled"),
      callback=self._on_live_view_toggled,
      param="LiveViewEnabled",
      enabled=lambda: self._remote_pin_is_set(),
    )

    self._remote_ssh_toggle = toggle_item_sp(
      title=lambda: tr("Remote SSH"),
      description=lambda: tr("Allow full remote terminal access from Konik Stable."),
      initial_state=ui_state.params.get_bool("RemoteSshEnabled"),
      param="RemoteSshEnabled",
      enabled=lambda: self._remote_pin_is_set(),
    )

    # put destructive reset at the bottom like other device controls
    self._scroller = Scroller([self._remote_pin_button, self._live_view_toggle, self._remote_ssh_toggle, Spacer(10), self._reset_pin_buttons],
                              line_separator=True, spacing=0)

  @staticmethod
  def _remote_pin_clear() -> None:
    params = ui_state.params
    params.put_bool("RemoteAccessPinEnabled", False)
    params.remove("RemoteAccessPinSalt")
    params.remove("RemoteAccessPinHash")
    params.put("RemoteAccessPinIterations", 150000)
    # Factory state for remote access features.
    params.put_bool("LiveViewEnabled", False)
    params.put_bool("RemoteSshEnabled", False)
    params.put_bool("LiveView", False)

  @staticmethod
  def _remote_pin_is_set() -> bool:
    params = ui_state.params
    if not params.get_bool("RemoteAccessPinEnabled"):
      return False
    salt = params.get("RemoteAccessPinSalt")
    hsh = params.get("RemoteAccessPinHash")
    iters = params.get("RemoteAccessPinIterations")
    return bool(salt) and bool(hsh) and (iters is not None)

  @staticmethod
  def _remote_pin_button_text() -> str:
    return tr("CHANGE") if StableLayout._remote_pin_is_set() else tr("SET")

  @staticmethod
  def _remote_pin_hash(pin: str, salt: bytes, iterations: int) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", pin.encode("utf-8"), salt, iterations, dklen=32)

  @staticmethod
  def _remote_pin_verify(pin: str) -> bool:
    params = ui_state.params
    salt = params.get("RemoteAccessPinSalt") or b""
    expected = params.get("RemoteAccessPinHash") or b""
    iters = params.get("RemoteAccessPinIterations") or 150000
    if not salt or not expected:
      return False
    actual = StableLayout._remote_pin_hash(pin, salt, int(iters))
    return hmac.compare_digest(expected, actual)

  @staticmethod
  def _remote_pin_set(pin: str) -> None:
    if not pin.isdigit() or not (4 <= len(pin) <= 12):
      raise ValueError("PIN must be 4-12 digits")
    params = ui_state.params
    iterations = 150000
    salt = os.urandom(16)
    hsh = StableLayout._remote_pin_hash(pin, salt, iterations)
    params.put("RemoteAccessPinSalt", salt)
    params.put("RemoteAccessPinHash", hsh)
    params.put("RemoteAccessPinIterations", iterations)
    params.put_bool("RemoteAccessPinEnabled", True)

  @staticmethod
  def _show_alert(msg: str) -> None:
    from openpilot.system.ui.lib.application import gui_app

    dlg = alert_dialog(msg)
    gui_app.set_modal_overlay(dlg, lambda _res: None)

  def _on_remote_pin_pressed(self) -> None:
    # Flow:
    # - If not set: enter new pin, confirm new pin.
    # - If set: enter old pin, then enter new pin, confirm.

    def _numbers_only_alert() -> None:
      self._show_alert(tr("Numbers only. No characters allowed."))

    def prompt_pin(title: str, subtitle: str, min_len: int, cb):
      dialog = InputDialogSP(title=title, sub_title=subtitle, current_text="", callback=cb, min_text_size=min_len, password_mode=True)
      dialog.show()

    def handle_new_pin(_result: DialogResult, new_pin: str):
      if _result != DialogResult.CONFIRM:
        return
      if new_pin == "":
        # Treat empty input as "clear PIN" and return to factory state.
        self._remote_pin_clear()
        self._show_alert(tr("PIN cleared."))
        return
      if not new_pin.isdigit():
        _numbers_only_alert()
        return
      if not new_pin.isdigit() or not (4 <= len(new_pin) <= 12):
        self._show_alert(tr("PIN must be 4-12 digits."))
        return

      def handle_confirm(_r2: DialogResult, confirm_pin: str):
        if _r2 != DialogResult.CONFIRM:
          return
        if not confirm_pin.isdigit():
          _numbers_only_alert()
          return
        if new_pin != confirm_pin:
          self._show_alert(tr("PINs do not match."))
          return
        try:
          self._remote_pin_set(new_pin)
        except ValueError:
          self._show_alert(tr("PIN must be 4-12 digits."))

      prompt_pin(tr("PIN"), tr("Confirm new PIN (4-12 digits)"), 4, handle_confirm)

    def handle_old_pin(_result: DialogResult, old_pin: str):
      if _result != DialogResult.CONFIRM:
        return
      if not old_pin.isdigit():
        _numbers_only_alert()
        return
      if not self._remote_pin_verify(old_pin):
        self._show_alert(tr("Wrong PIN."))
        return
      prompt_pin(tr("PIN"), tr("Enter new PIN (4-12 digits)"), 4, handle_new_pin)

    if self._remote_pin_is_set():
      prompt_pin(tr("PIN"), tr("Enter current PIN"), 4, handle_old_pin)
    else:
      # min_text_size=0 so the user can submit empty to clear and return to factory state
      prompt_pin(tr("PIN"), tr("Enter new PIN (4-12 digits) or leave blank to clear"), 0, handle_new_pin)

  def _on_reset_pin_pressed(self) -> None:
    if not self._remote_pin_is_set():
      return
    from openpilot.system.ui.lib.application import gui_app

    dlg = ConfirmDialog(tr("Reset PIN?"), tr("Reset"), tr("Cancel"))

    def cb(res: DialogResult):
      if res == DialogResult.CONFIRM:
        self._remote_pin_clear()
        self._show_alert(tr("PIN reset."))

    gui_app.set_modal_overlay(dlg, cb)

  @staticmethod
  def _on_live_view_toggled(enabled: bool):
    if not enabled:
      ui_state.params.put_bool("LiveView", False)

  def _render(self, rect):
    self._scroller.render(rect)

  def show_event(self):
    self._scroller.show_event()

