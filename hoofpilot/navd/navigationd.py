"""
Copyright (c) 2021-, James Vecellio, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import json
from math import degrees
from numpy import interp

import cereal.messaging as messaging
from cereal import custom
from openpilot.common.params import Params
from openpilot.common.realtime import Ratekeeper
from openpilot.common.swaglog import cloudlog

from hoofpilot.navd.constants import NAV_CV
from hoofpilot.navd.helpers import Coordinate, parse_banner_instructions
from hoofpilot.navd.navigation_helpers.mapbox_integration import MapboxIntegration
from hoofpilot.navd.navigation_helpers.nav_instructions import NavigationInstructions


class Navigationd:
  def __init__(self):
    self.params = Params()
    self.mapbox = MapboxIntegration()
    self.nav_instructions = NavigationInstructions()

    self.sm = messaging.SubMaster(['carControlSP', 'liveLocationKalman'])
    self.pm = messaging.PubMaster(['navigationd'])
    self.rk = Ratekeeper(3) # 3 Hz

    self.route = None
    self.destination: str | None = None
    self.new_destination: str = ''
    self.current_nav_destination: dict | None = None
    self.last_nav_destination: dict | None = None

    self.allow_navigation: bool = False
    self.recompute_allowed: bool = False
    self.allow_recompute: bool = False
    self.reroute_counter: int = 0
    self.cancel_route_counter: int = 0

    self.frame: int = -1
    self.last_position: Coordinate | None = None
    self.last_bearing: float | None = None
    self.valid: bool = False

  def _update_params(self):
    if self.last_position is not None:
      self.frame += 1
      if self.frame % 15 == 0:
        self.allow_navigation = self.params.get('AllowNavigation', return_default=True)
        self.new_destination = self.params.get('MapboxRoute')
        self.recompute_allowed = self.params.get('MapboxRecompute', return_default=True)
        raw_nav_destination = self.params.get('NavDestination')
        self.current_nav_destination = self._parse_nav_destination(raw_nav_destination)

      destination_changed = self.current_nav_destination and self.current_nav_destination != self.last_nav_destination
      self.allow_recompute: bool = bool(destination_changed) or (self.new_destination != self.destination and self.new_destination != '') or (
        self.recompute_allowed and self.reroute_counter > 9 and self.route)

      if self.allow_recompute:
        postvars = {'place_name': self.new_destination}
        if self.current_nav_destination:
          latitude = self.current_nav_destination.get('latitude')
          longitude = self.current_nav_destination.get('longitude')
          place_name = self.current_nav_destination.get('place_name')
          if isinstance(place_name, str) and place_name.strip():
            postvars['place_name'] = place_name.strip()
          if isinstance(latitude, (int, float)) and isinstance(longitude, (int, float)) and not (abs(latitude) < 1e-6 and abs(longitude) < 1e-6):
            postvars['latitude'] = float(latitude)
            postvars['longitude'] = float(longitude)

        postvars, valid_addr = self.mapbox.set_destination(postvars, self.last_position.longitude, self.last_position.latitude, self.last_bearing)

        if valid_addr:
          self.destination = self.new_destination
          self.last_nav_destination = dict(self.current_nav_destination) if self.current_nav_destination else None
          self.nav_instructions.clear_route_cache()
          self.route = self.nav_instructions.get_current_route()
          self.cancel_route_counter = 0
          self.reroute_counter = 0

      if self.cancel_route_counter == 30:
        self.cancel_route_counter = 0
        self.destination = None
        self.nav_instructions.clear_route_cache()
        self.route = None

      self.valid = self.route is not None

  @staticmethod
  def _parse_nav_destination(raw_nav_destination) -> dict | None:
    if raw_nav_destination is None:
      return None

    if isinstance(raw_nav_destination, bytes):
      try:
        raw_nav_destination = raw_nav_destination.decode('utf-8', errors='ignore')
      except Exception:
        return None

    if not isinstance(raw_nav_destination, str) or not raw_nav_destination.strip():
      return None

    try:
      parsed = json.loads(raw_nav_destination)
    except (ValueError, TypeError):
      return None

    if not isinstance(parsed, dict):
      return None

    return parsed

  def _update_navigation(self) -> tuple[str, dict | None, dict]:
    banner_instructions: str = ''
    nav_data: dict = {}
    if self.allow_navigation and self.route and self.last_position is not None:
      if progress := self.nav_instructions.get_route_progress(self.last_position.latitude, self.last_position.longitude):
        v_ego = float(max(self.sm['carControlSP'].speed, 0.0))
        nav_data['upcoming_turn'] = self.nav_instructions.get_upcoming_turn_from_progress(progress, self.last_position.latitude,
                                                                                          self.last_position.longitude, v_ego)
        speed_limit, _ = progress['current_maxspeed']
        nav_data['current_speed_limit'] = speed_limit
        arrived = self.nav_instructions.arrived_at_destination(progress, v_ego)

        if progress['current_step']:
          parsed = parse_banner_instructions(progress['current_step']['bannerInstructions'], progress['distance_to_end_of_step'])
          if parsed:
            banner_instructions = parsed['maneuverPrimaryText']

        nav_data['distance_from_route'] = progress['distance_from_route']
        speed_breakpoints: list = [0.0, 5.0, 10.0, 20.0, 40.0]
        distance_list: list = [100.0, 125.0, 150.0, 200.0, 250.0]
        large_distance: bool = progress['distance_from_route'] > float(interp(v_ego, speed_breakpoints, distance_list))

        route_bearing_misalign: bool = self.nav_instructions.route_bearing_misalign(self.route, self.last_bearing, v_ego)

        if large_distance and not arrived:
          self.cancel_route_counter = self.cancel_route_counter + 1 if progress['distance_from_route'] > NAV_CV.QUARTER_MILE else 0
          if self.recompute_allowed:
            self.reroute_counter += 1
        elif arrived:
          self.cancel_route_counter += 1
          self.recompute_allowed = False
        elif route_bearing_misalign:
          self.cancel_route_counter += 1
          if self.recompute_allowed:
            self.reroute_counter += 1
        else:
          self.cancel_route_counter = 0
          self.reroute_counter = 0

        # Don't recompute in last segment to prevent reroute loops
        if progress['current_step_idx'] == len(self.route['steps']) - 1:
          self.recompute_allowed = False
          self.allow_navigation = False
    else:
      banner_instructions = ''
      progress = None
      nav_data = {}

    return banner_instructions, progress, nav_data

  def _build_navigation_message(self, banner_instructions: str, progress: dict | None, nav_data: dict, valid: bool):
    msg = messaging.new_message('navigationd')
    msg.valid = valid
    msg.navigationd.upcomingTurn = nav_data.get('upcoming_turn', 'none')
    msg.navigationd.currentSpeedLimit = nav_data.get('current_speed_limit', 0)
    msg.navigationd.bannerInstructions = banner_instructions
    msg.navigationd.distanceFromRoute = nav_data.get('distance_from_route', 0.0)
    msg.navigationd.valid = self.valid

    all_maneuvers = (
      [custom.Navigationd.Maneuver.new_message(distance=m['distance'], type=m['type'], modifier=m['modifier'],
                                               instruction=m['instruction']) for m in progress['all_maneuvers']]
      if progress
      else []
    )
    msg.navigationd.allManeuvers = all_maneuvers
    return msg

  def run(self):
    cloudlog.warning('navigationd init')

    while True:
      self.sm.update(0)
      location = self.sm['liveLocationKalman']
      localizer_valid = location.positionGeodetic.valid if location else False

      if localizer_valid:
        self.last_bearing = degrees(location.calibratedOrientationNED.value[2])
        self.last_position = Coordinate(location.positionGeodetic.value[0], location.positionGeodetic.value[1])

      self._update_params()
      banner_instructions, progress, nav_data = self._update_navigation()

      msg = self._build_navigation_message(banner_instructions, progress, nav_data, valid=localizer_valid)

      self.pm.send('navigationd', msg)
      self.rk.keep_time()


def main():
  nav = Navigationd()
  nav.run()
