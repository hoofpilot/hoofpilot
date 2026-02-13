import pyray as rl
import hashlib
import hmac
import os
from collections.abc import Callable

from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.widgets.scroller import Scroller
from openpilot.system.ui.widgets import NavWidget, DialogResult
from openpilot.system.ui.lib.application import gui_app, MousePos
from openpilot.system.ui.lib.multilang import tr
from openpilot.selfdrive.ui.mici.widgets.button import BigButton, BigParamControl
from openpilot.selfdrive.ui.mici.widgets.dialog import BigDialog, BigInputDialog, BigConfirmationDialogV2


class DangerBigButton(BigButton):
  def __init__(self, text: str, value: str = "", icon: str = "", icon_size: tuple[int, int] = (64, 64), scroll: bool = False):
    super().__init__(text, value, icon, icon_size=icon_size, scroll=scroll)
    self._tint = rl.Color(190, 40, 40, 255)

  def _render(self, _):
    # draw the same button assets but tinted red to indicate a destructive action
    txt_bg = self._txt_default_bg
    if not self.enabled:
      txt_bg = self._txt_disabled_bg
    elif self.is_pressed:
      txt_bg = self._txt_hover_bg

    # Mirror BigButton behavior without importing module-level constants.
    scale = self._scale_filter.update(1.07 if self.is_pressed else 1.0)
    btn_x = self._rect.x + (self._rect.width * (1 - scale)) / 2
    btn_y = self._rect.y + (self._rect.height * (1 - scale)) / 2

    # If disabled, keep the normal disabled styling. Otherwise tint red.
    tint = rl.WHITE if not self.enabled else self._tint
    rl.draw_texture_ex(txt_bg, (btn_x, btn_y), 0, scale, tint)

    self._draw_content(btn_y)


class StableLayoutMici(NavWidget):
  def __init__(self, back_callback: Callable[[], None]):
    super().__init__()
    self.set_back_callback(back_callback)

    # Enforce "PIN first": keep remote access features off until a PIN is configured.
    self._enforce_pin_first()

    self._pin_btn = BigButton("PIN", self._pin_btn_value(), "", scroll=False)
    self._pin_btn.set_click_callback(self._on_pin_pressed)
    self._pin_btn.set_enabled(lambda: ui_state.is_offroad())

    self._live_view_toggle = BigParamControl("live view", "LiveViewEnabled", toggle_callback=self._on_live_view_toggled)
    self._remote_ssh_toggle = BigParamControl("remote ssh", "RemoteSshEnabled")

    # Disable toggles until PIN is set.
    self._live_view_toggle.set_enabled(lambda: self._remote_pin_is_set())
    self._remote_ssh_toggle.set_enabled(lambda: self._remote_pin_is_set())

    self._reset_pin_btn = DangerBigButton("reset PIN", "")
    self._reset_pin_btn.set_click_callback(self._on_reset_pin_pressed)
    self._reset_pin_btn.set_enabled(lambda: ui_state.is_offroad() and self._remote_pin_is_set())

    # Horizontal layout: keep controls side-by-side instead of stacked vertically.
    self._scroller = Scroller([
      self._pin_btn,
      self._live_view_toggle,
      self._remote_ssh_toggle,
      self._reset_pin_btn,
    ], horizontal=True, snap_items=False, line_separator=False, spacing=20, pad_start=20, pad_end=20, scroll_indicator=True)

  def show_event(self):
    super().show_event()
    self._scroller.show_event()
    self._enforce_pin_first()
    self._refresh()

  def _update_state(self):
    super()._update_state()
    self._refresh()

  def _refresh(self):
    # Keep UI in sync with params that can change from elsewhere.
    self._pin_btn.set_value(self._pin_btn_value())
    self._live_view_toggle.refresh()
    self._remote_ssh_toggle.refresh()

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
    actual = StableLayoutMici._remote_pin_hash(pin, salt, int(iters))
    return hmac.compare_digest(expected, actual)

  @staticmethod
  def _remote_pin_set(pin: str) -> None:
    if not pin.isdigit() or not (4 <= len(pin) <= 12):
      raise ValueError("PIN must be 4-12 digits")
    params = ui_state.params
    iterations = 150000
    salt = os.urandom(16)
    hsh = StableLayoutMici._remote_pin_hash(pin, salt, iterations)
    params.put("RemoteAccessPinSalt", salt)
    params.put("RemoteAccessPinHash", hsh)
    params.put("RemoteAccessPinIterations", iterations)
    params.put_bool("RemoteAccessPinEnabled", True)

  def _enforce_pin_first(self):
    if not self._remote_pin_is_set():
      ui_state.params.put_bool("LiveViewEnabled", False)
      ui_state.params.put_bool("RemoteSshEnabled", False)
      ui_state.params.put_bool("LiveView", False)

  def _pin_btn_value(self) -> str:
    return tr("change") if self._remote_pin_is_set() else tr("set")

  def _show_message(self, title: str, description: str = "") -> None:
    gui_app.set_modal_overlay(BigDialog(title, description))

  def _numbers_only_alert(self) -> None:
    self._show_message(tr("Numbers only."), tr("No characters allowed."))

  def _pin_length_alert(self) -> None:
    self._show_message(tr("PIN must be 4-12 digits."), "")

  def _on_pin_pressed(self) -> None:
    # Flow:
    # - If not set: enter new pin, confirm new pin.
    # - If set: enter old pin, then enter new pin, confirm.

    def prompt_pin(hint: str, min_len: int, cb: Callable[[str], None]):
      gui_app.set_modal_overlay(BigInputDialog(hint, default_text="", minimum_length=min_len, confirm_callback=cb))

    def handle_confirm_new(new_pin: str):
      if new_pin == "":
        # Treat empty input as "clear PIN" and return to factory state.
        self._remote_pin_clear()
        self._show_message(tr("PIN cleared."), "")
        return
      if not new_pin.isdigit():
        self._numbers_only_alert()
        return
      if not (4 <= len(new_pin) <= 12):
        self._pin_length_alert()
        return

      def handle_confirm(confirm_pin: str):
        if not confirm_pin.isdigit():
          self._numbers_only_alert()
          return
        if new_pin != confirm_pin:
          self._show_message(tr("PINs do not match."), "")
          return
        try:
          self._remote_pin_set(new_pin)
          self._show_message(tr("PIN set."), "")
        except ValueError:
          self._pin_length_alert()

      prompt_pin(tr("Confirm new PIN (4-12 digits)"), 4, handle_confirm)

    def handle_old_pin(old_pin: str):
      if not old_pin.isdigit():
        self._numbers_only_alert()
        return
      if not self._remote_pin_verify(old_pin):
        self._show_message(tr("Wrong PIN."), "")
        return

      prompt_pin(tr("Enter new PIN (4-12 digits)"), 0, handle_confirm_new)

    if self._remote_pin_is_set():
      prompt_pin(tr("Enter current PIN"), 4, handle_old_pin)
    else:
      prompt_pin(tr("Enter new PIN (4-12 digits) or leave blank to clear"), 0, handle_confirm_new)

  def _on_reset_pin_pressed(self) -> None:
    if not self._remote_pin_is_set():
      return

    def do_reset():
      self._remote_pin_clear()
      self._show_message(tr("PIN reset."), "")

    dlg = BigConfirmationDialogV2(tr("slide to reset PIN"), "icons_mici/settings/network/new/trash.png", red=True, confirm_callback=do_reset)
    gui_app.set_modal_overlay(dlg)

  @staticmethod
  def _on_live_view_toggled(enabled: bool):
    if not enabled:
      ui_state.params.put_bool("LiveView", False)

  def _render(self, rect: rl.Rectangle):
    self._scroller.render(rect)
