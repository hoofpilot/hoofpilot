from openpilot.selfdrive.ui.onroad.augmented_road_view import BORDER_COLORS
from openpilot.selfdrive.ui.ui_state import ui_state, UIStatus


class ConfidenceBallSP:
  @staticmethod
  def get_animate_status_probs():
    if ui_state.status == UIStatus.LAT_ONLY:
      return ui_state.sm['modelV2'].meta.disengagePredictions.steerOverrideProbs

    # UIStatus.LONG_ONLY
    return ui_state.sm['modelV2'].meta.disengagePredictions.brakeDisengageProbs

  @staticmethod
  def get_lat_long_dot_color():
    if ui_state.status == UIStatus.LAT_ONLY:
      return BORDER_COLORS[UIStatus.LAT_ONLY]

    # UIStatus.LONG_ONLY
    return BORDER_COLORS[UIStatus.LONG_ONLY]

