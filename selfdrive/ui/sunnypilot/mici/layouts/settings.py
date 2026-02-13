from enum import IntEnum

from openpilot.selfdrive.ui.mici.layouts.settings import settings as OP
from openpilot.selfdrive.ui.mici.widgets.button import BigButton
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.models import ModelsLayoutMici
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.stable import StableLayoutMici
from openpilot.selfdrive.ui.ui_state import ui_state

ICON_SIZE = 70

OP.PanelType = IntEnum(
  "PanelType",
  [es.name for es in OP.PanelType] + [
    "SUNNYLINK",
    "STABLE",
    "MODELS",
  ],
  start=0,
)


class SettingsLayoutSP(OP.SettingsLayout):
  def __init__(self):
    OP.SettingsLayout.__init__(self)

    self._stable_btn = BigButton("stable", "", "../../sunnypilot/selfdrive/assets/offroad/icon_konik.png", icon_size=(72, 72))
    self._stable_btn.set_click_callback(lambda: self._set_current_panel(OP.PanelType.STABLE))
    self._stable_btn.set_visible(ui_state.prime_state.is_paired())

    models_btn = BigButton("models", "", "../../sunnypilot/selfdrive/assets/offroad/icon_models.png")
    models_btn.set_click_callback(lambda: self._set_current_panel(OP.PanelType.MODELS))

    self._panels.update({
      OP.PanelType.STABLE: OP.PanelInfo("stable", StableLayoutMici(back_callback=lambda: self._set_current_panel(None))),
      OP.PanelType.MODELS: OP.PanelInfo("models", ModelsLayoutMici(back_callback=lambda: self._set_current_panel(None))),
    })

    items = self._scroller._items.copy()

    items.insert(1, self._stable_btn)
    items.insert(2, models_btn)
    self._scroller._items.clear()
    for item in items:
      self._scroller.add_widget(item)

  def _update_state(self):
    super()._update_state()
    paired = ui_state.prime_state.is_paired()
    self._stable_btn.set_visible(paired)
    if not paired and self._current_panel == OP.PanelType.STABLE:
      self._set_current_panel(None)

