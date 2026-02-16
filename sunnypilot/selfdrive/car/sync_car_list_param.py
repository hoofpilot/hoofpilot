#!/usr/bin/env python3
import json
import os

from openpilot.common.basedir import BASEDIR
from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog

CAR_LIST_JSON_OUT = os.path.join(BASEDIR, "sunnypilot", "selfdrive", "car", "car_list.json")


def update_car_list_param():
  with open(CAR_LIST_JSON_OUT) as f:
    current_car_list = json.load(f)

  params = Params()
  if params.get("CarList") != current_car_list:
    params.put("CarList", current_car_list)
    cloudlog.warning("Updated CarList param with latest platform list")
  else:
    cloudlog.warning("CarList param is up to date, no need to update")


if __name__ == "__main__":
  update_car_list_param()

