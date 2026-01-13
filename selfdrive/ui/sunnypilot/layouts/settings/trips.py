"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import threading
import time
from openpilot.common.api import api_get
from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog
from openpilot.selfdrive.ui.lib.api_helpers import get_token
from openpilot.selfdrive.ui.ui_state import device, ui_state
from openpilot.system.athena.registration import UNREGISTERED_DONGLE_ID
from openpilot.system.ui.widgets import Widget
from openpilot.selfdrive.ui.widgets.drive_stats import DriveStatsWidget, PARAM_KEY

UPDATE_INTERVAL = 30  # seconds


class TripsLayout(Widget):
  def __init__(self):
    super().__init__()

    self._params = Params()
    self._drive_stats = self._initialize_items()

    self._running = True
    self._update_thread = threading.Thread(target=self._update_loop, daemon=True)
    self._update_thread.start()

  def __del__(self):
    self._running = False
    try:
      if self._update_thread and self._update_thread.is_alive():
        self._update_thread.join(timeout=1.0)
    except Exception:
      pass

  def _initialize_items(self):
    self._drive_stats = DriveStatsWidget(self._params)
    return self._drive_stats

  def _fetch_drive_stats(self):
    try:
      dongle_id = self._params.get("DongleId")
      if not dongle_id or dongle_id == UNREGISTERED_DONGLE_ID:
        return
      identity_token = get_token(dongle_id)
      response = api_get(f"v1.1/devices/{dongle_id}/stats", access_token=identity_token)
      if response.status_code == 200:
        data = response.json()
        self._params.put(PARAM_KEY, data)
    except Exception as e:
      cloudlog.error(f"Failed to fetch drive stats: {e}")

  def _update_loop(self):
    while self._running:
      if not ui_state.started and device._awake:
        self._fetch_drive_stats()
      time.sleep(UPDATE_INTERVAL)

  def _render(self, rect):
    self._drive_stats.render(rect)

  def show_event(self):
    self._drive_stats.show_event()
