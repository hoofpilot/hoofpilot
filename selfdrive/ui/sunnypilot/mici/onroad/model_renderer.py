import pyray as rl
from openpilot.selfdrive.ui.ui_state import UIStatus

LANE_LINE_COLORS_SP = {
  UIStatus.LAT_ONLY: rl.Color(0, 255, 64, 255),
  UIStatus.LONG_ONLY: rl.Color(0, 255, 64, 255),
}

