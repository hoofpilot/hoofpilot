from openpilot.common.params import Params
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr, tr_noop
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.list_view import toggle_item
from openpilot.system.ui.widgets.scroller_tici import Scroller

if gui_app.sunnypilot_ui():
  from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp as toggle_item


DESCRIPTIONS = {
  "LiveViewEnabled": tr_noop(
    "Allow Konik Stable to connect to Live View so you can stream the road and driver cameras."
  ),
  "RemoteSshEnabled": tr_noop(
    "Allow Konik Stable to open a remote shell session over Live View."
  ),
}


class StableLayout(Widget):
  def __init__(self):
    super().__init__()
    self._params = Params()

    self._live_view_toggle = toggle_item(
      lambda: tr("Live View"),
      description=lambda: tr(DESCRIPTIONS["LiveViewEnabled"]),
      initial_state=self._params.get_bool("LiveViewEnabled"),
      callback=self._on_live_view_toggle,
    )

    self._remote_ssh_toggle = toggle_item(
      lambda: tr("Remote SSH"),
      description=lambda: tr(DESCRIPTIONS["RemoteSshEnabled"]),
      initial_state=self._params.get_bool("RemoteSshEnabled"),
      callback=self._on_remote_ssh_toggle,
    )

    self._scroller = Scroller([
      self._live_view_toggle,
      self._remote_ssh_toggle,
    ], line_separator=True, spacing=0)

    ui_state.add_offroad_transition_callback(self._update_toggles)

  def _render(self, rect):
    self._scroller.render(rect)

  def show_event(self):
    self._scroller.show_event()
    self._update_toggles()

  def _update_toggles(self):
    ui_state.update_params()
    self._live_view_toggle.action_item.set_state(self._params.get_bool("LiveViewEnabled"))
    self._remote_ssh_toggle.action_item.set_state(self._params.get_bool("RemoteSshEnabled"))

  def _on_live_view_toggle(self, state: bool):
    self._params.put_bool("LiveViewEnabled", state)

  def _on_remote_ssh_toggle(self, state: bool):
    self._params.put_bool("RemoteSshEnabled", state)
