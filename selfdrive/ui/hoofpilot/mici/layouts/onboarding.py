"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pyray as rl
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.mici_setup import GreyBigButton
from openpilot.system.ui.widgets.scroller import Scroller
from openpilot.system.ui.widgets.slider import SmallSlider
from openpilot.system.version import sunnylink_consent_version, sunnylink_consent_declined
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.selfdrive.ui.mici.widgets.dialog import BigConfirmationCircleButton


class SunnylinkConsentPage(Scroller):
  def __init__(self, on_accept=None, on_decline=None, left_text: str = "disable", right_text: str = "enable"):
    super().__init__()

    logo = gui_app.texture("../../hoofpilot/selfdrive/assets/logo.png", 66, 60)
    self._header_card = GreyBigButton("sunnylink", "secured remote access", logo)
    self._terms_card = GreyBigButton(
      "",
      "sunnylink enables secured remote access to your comma device from anywhere, "
      "including settings management, remote monitoring, real-time dashboard, etc.",
    )
    self._accept_button = BigConfirmationCircleButton(
      right_text,
      gui_app.texture("icons_mici/setup/driver_monitoring/dm_check.png", 64, 64),
      on_accept,
    )
    self._decline_button = BigConfirmationCircleButton(
      left_text,
      gui_app.texture("icons_mici/setup/cancel.png", 64, 64),
      on_decline,
      red=True, exit_on_confirm=False,
    )

    self._scroller.add_widgets([
      self._header_card,
      self._terms_card,
      self._accept_button,
      self._decline_button,
    ])

  def _render(self, _):
    rl.draw_rectangle_rec(self._rect, rl.BLACK)
    super()._render(_)


class SunnylinkConsentDisableConfirmPage(SunnylinkConsentPage):
  def __init__(self, on_accept=None, on_decline=None):
    super().__init__(on_accept=on_decline, on_decline=on_accept, left_text="enable", right_text="disable")

    self._accept_button.set_visible(False)

    self._continue_button = SmallSlider("disable", confirm_callback=on_decline)
    self._scroll_panel.set_enabled(lambda: not self._continue_button.is_pressed)

    warning_icon = gui_app.texture("icons_mici/setup/red_warning.png", 66, 60)
    self._header_card.set_icon(warning_icon)
    self._header_card.set_text("disable sunnylink?")
    self._header_card.set_value("")

    self._terms_card.set_value(
      "sunnylink is designed to be enabled as part of hoofpilot's core functionality. "
      "If sunnylink is disabled, features such as settings management, "
      "remote monitoring, real-time dashboards will be unavailable.",
    )

    self._scroller.add_widgets([self._continue_button])


class SunnylinkOnboarding:
  def __init__(self):
    self.consent_done: bool = ui_state.params.get("CompletedSunnylinkConsentVersion") in {sunnylink_consent_version, sunnylink_consent_declined}
    self.disable_confirm = False

    self.consent_page = SunnylinkConsentPage(on_decline=self._on_decline, on_accept=self._on_accept)
    self.confirm_page = SunnylinkConsentDisableConfirmPage(on_decline=self._on_confirm_decline, on_accept=self._on_accept)

  @property
  def completed(self) -> bool:
    return self.consent_done

  def _on_accept(self):
    ui_state.params.put("CompletedSunnylinkConsentVersion", sunnylink_consent_version)
    ui_state.params.put_bool("SunnylinkEnabled", True)
    self.consent_done = True

  def _on_decline(self):
    self.disable_confirm = True

  def _on_confirm_decline(self):
    ui_state.params.put_bool("SunnylinkEnabled", False)
    ui_state.params.put("CompletedSunnylinkConsentVersion", sunnylink_consent_declined)
    self.consent_done = True

  def render(self, rect):
    if self.consent_done:
      return

    if self.disable_confirm:
      self.confirm_page.render(rect)
    else:
      self.consent_page.render(rect)
