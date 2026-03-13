"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import json
import math
import platform

from cereal import log
from openpilot.common.params import Params
from hoofpilot.mapd_v2.live_map_data.base_map_data import BaseMapData
from hoofpilot.navd.helpers import Coordinate


class OsmMapData(BaseMapData):
  def __init__(self):
    super().__init__()
    self.mem_params = Params("/dev/shm/params") if platform.system() != "Darwin" else self.params

  def update_location(self) -> None:
    location = self.sm['liveLocationKalman']
    self.localizer_valid = (location.status == log.LiveLocationKalman.Status.valid) and location.positionGeodetic.valid

    if self.localizer_valid:
      self.last_bearing = math.degrees(location.calibratedOrientationNED.value[2])
      self.last_position = Coordinate(location.positionGeodetic.value[0], location.positionGeodetic.value[1])

    if self.last_position is None:
      return

    params = {
      "latitude": self.last_position.latitude,
      "longitude": self.last_position.longitude,
    }

    if self.last_bearing is not None:
      params['bearing'] = self.last_bearing

    self.mem_params.put("LastGPSPosition", json.dumps(params))

  def get_current_speed_limit(self) -> float:
    return float(self.sm["mapdOut"].speedLimit)

  def get_current_road_name(self) -> str:
    return str(self.sm["mapdOut"].roadName)

  def get_next_speed_limit_and_distance(self) -> tuple[float, float]:
    next_speed_limit = float(self.sm["mapdOut"].nextSpeedLimit)
    next_speed_limit_distance = float(self.sm["mapdOut"].nextSpeedLimitDistance)
    return next_speed_limit, next_speed_limit_distance

