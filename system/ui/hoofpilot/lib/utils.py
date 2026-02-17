from openpilot.system.ui.hoofpilot.widgets.list_view import ButtonActionSP


class NoElideButtonAction(ButtonActionSP):
  def get_width_hint(self):
    return super().get_width_hint() + 1

