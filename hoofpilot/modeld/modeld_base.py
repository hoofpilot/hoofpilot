from openpilot.common.params import Params


class ModelStateBase:
  def __init__(self):
    self.lat_delay = Params().get("LagdValueCache", return_default=True)

