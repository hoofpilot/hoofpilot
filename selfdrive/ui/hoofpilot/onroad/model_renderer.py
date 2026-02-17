from openpilot.selfdrive.ui.hoofpilot.onroad.chevron_metrics import ChevronMetrics
from openpilot.selfdrive.ui.hoofpilot.onroad.rainbow_path import RainbowPath


class ModelRendererSP:
  def __init__(self):
    self.rainbow_path = RainbowPath()
    self.chevron_metrics = ChevronMetrics()

