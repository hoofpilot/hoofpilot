from openpilot.common.params import Params


def get_lat_delay(params: Params, stock_lat_delay: float) -> float:
  if params.get_bool("LagdToggle"):
    return float(params.get("LagdValueCache", return_default=True))

  return stock_lat_delay

