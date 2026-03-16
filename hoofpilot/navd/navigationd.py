"""
Copyright (c) 2021-, James Vecellio, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import json
import os
import requests
from math import degrees
from numpy import interp

import cereal.messaging as messaging
from cereal import custom
from openpilot.common.api import Api
from openpilot.common.params import Params
from openpilot.common.realtime import Ratekeeper
from openpilot.common.swaglog import cloudlog

from hoofpilot.navd.constants import NAV_CV
from hoofpilot.navd.helpers import Coordinate, parse_banner_instructions
from hoofpilot.navd.navigation_helpers.mapbox_integration import MapboxIntegration
from hoofpilot.navd.navigation_helpers.nav_instructions import NavigationInstructions

KONIK_API_HOST = os.getenv('API_HOST', 'https://api.konik.ai')


class Navigationd:
  def __init__(self):
    self.params = Params()
    self.mapbox = MapboxIntegration()
    self.nav_instructions = NavigationInstructions()

    self.sm = messaging.SubMaster(['carControlSP', 'liveLocationKalman'])
    self.pm = messaging.PubMaster(['navigationd'])
    self.rk = Ratekeeper(3)  # 3 Hz

    self.route = None
    self.destination: str | None = None
    self.new_destination: str = ''

    self.allow_navigation: bool = True
    self.recompute_allowed: bool = True
    self.allow_recompute: bool = False
    self.reroute_counter: int = 0
    self.cancel_route_counter: int = 0

    self.frame: int = -1
    self.last_position: Coordinate | None = None
    self.last_bearing: float | None = None
    self.valid: bool = False

    # Track last seen NavDestination to detect remote destination changes from Stable web
    self._last_nav_destination: str = ''

    # Poll Konik /next endpoint every 15 seconds; start immediately
    self._poll_frame: int = 0
    self._poll_interval: int = 45  # frames at 3 Hz = 15 seconds

  def _get_auth_headers(self) -> dict:
    try:
      dongle_id = self._safe_get('DongleId', '')
      if not dongle_id:
        return {}
      token = Api(dongle_id).get_token()
      return {'Authorization': f'JWT {token}'}
    except Exception:
      return {}

  def _poll_konik_next(self):
    """Poll /v1/navigation/:dongle_id/next and apply the destination if present."""
    try:
      dongle_id = self._safe_get('DongleId', '')
      if not dongle_id:
        return
      headers = self._get_auth_headers()
      if not headers:
        return
      resp = requests.get(
        f'{KONIK_API_HOST}/v1/navigation/{dongle_id}/next',
        headers=headers,
        timeout=5,
      )
      if resp.status_code != 200:
        return
      dest = resp.json()
      if not dest:
        return
      place_name = dest.get('place_name') or ''
      lat = dest.get('latitude', 0)
      lon = dest.get('longitude', 0)
      if not place_name:
        return

      # Build NavDestination JSON and store so the UI and other components see it
      nav_dest = json.dumps({'latitude': lat, 'longitude': lon, 'place_name': place_name, 'place_details': dest.get('place_details', '')})
      self._safe_put('NavDestination', nav_dest)
      self._safe_put('MapboxRoute', place_name)
      cloudlog.warning(f'navigationd: polled destination from Konik: {place_name}')
    except Exception as e:
      cloudlog.warning(f'navigationd: poll_konik_next failed: {e}')

  def _safe_get(self, key, default=''):
    try:
      return self.params.get(key) or default
    except Exception:
      return default

  def _safe_put(self, key, value):
    try:
      self.params.put_nonblocking(key, value)
    except Exception:
      pass

  def _safe_remove(self, key):
    try:
      self.params.remove(key)
    except Exception:
      pass

  def _update_params(self):
    # Poll Konik /next regardless of GPS — stores destination in params so UI shows it
    self._poll_frame += 1
    if self._poll_frame >= self._poll_interval:
      self._poll_frame = 0
      self._poll_konik_next()

    if self.last_position is not None:
      self.frame += 1
      if self.frame % 15 == 0:
        # Check NavDestination (set via Athena from Stable web or polled from Konik) for coordinate-based routing
        nav_dest_str = self._safe_get('NavDestination', '')
        if nav_dest_str and nav_dest_str != self._last_nav_destination:
          self._last_nav_destination = nav_dest_str
          try:
            nav_dest = json.loads(nav_dest_str)
            lat = nav_dest.get('latitude', 0)
            lon = nav_dest.get('longitude', 0)
            place_name = nav_dest.get('place_name') or ''
            if lat and lon:
              # Has coordinates — pass directly, skips geocoding
              self.new_destination = place_name or f'{lat},{lon}'
              postvars = {'latitude': lat, 'longitude': lon, 'place_name': self.new_destination}
              postvars, valid_addr = self.mapbox.set_destination(postvars, self.last_position.longitude, self.last_position.latitude, self.last_bearing)
              if valid_addr:
                self.destination = self.new_destination
                self.nav_instructions.clear_route_cache()
                self.route = self.nav_instructions.get_current_route()
                self.cancel_route_counter = 0
                self.reroute_counter = 0
            elif not lat and not lon and not place_name:
              # All empty — explicit clear-route signal
              self._safe_put('MapboxRoute', '')
              self.nav_instructions.clear_route_cache()
              self.route = None
              self.destination = None
              self.new_destination = ''
            elif place_name:
              # No coordinates but has place_name — geocode via MapboxRoute
              self.new_destination = place_name
              self._safe_put('MapboxRoute', place_name)
          except (json.JSONDecodeError, KeyError):
            pass

        # Also check MapboxRoute (text address set via device offroad UI)
        self.new_destination = self._safe_get('MapboxRoute', '') or self.new_destination

      self.allow_recompute = (self.new_destination != self.destination and self.new_destination != '') or (
        self.recompute_allowed and self.reroute_counter > 9 and self.route
      )

      if self.allow_recompute:
        postvars = {'place_name': self.new_destination}
        postvars, valid_addr = self.mapbox.set_destination(postvars, self.last_position.longitude, self.last_position.latitude, self.last_bearing)

        if valid_addr:
          self.destination = self.new_destination
          self.nav_instructions.clear_route_cache()
          self.route = self.nav_instructions.get_current_route()
          self.cancel_route_counter = 0
          self.reroute_counter = 0

      if self.cancel_route_counter == 30:
        self.cancel_route_counter = 0
        self._safe_put('MapboxRoute', '')
        self.nav_instructions.clear_route_cache()
        self.route = None

      self.valid = self.route is not None

  def _update_navigation(self) -> tuple[str, dict | None, dict]:
    banner_instructions: str = ''
    nav_data: dict = {}
    if self.allow_navigation and self.route and self.last_position is not None:
      if progress := self.nav_instructions.get_route_progress(self.last_position.latitude, self.last_position.longitude):
        v_ego = float(max(self.sm['carControlSP'].speed, 0.0))
        nav_data['upcoming_turn'] = self.nav_instructions.get_upcoming_turn_from_progress(
          progress, self.last_position.latitude, self.last_position.longitude, v_ego
        )
        speed_limit, _ = progress['current_maxspeed']
        nav_data['current_speed_limit'] = speed_limit
        arrived = self.nav_instructions.arrived_at_destination(progress, v_ego)

        if progress['current_step']:
          if parsed := parse_banner_instructions(progress['current_step']['bannerInstructions'], progress['distance_to_end_of_step']):
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
      [
        custom.Navigationd.Maneuver.new_message(
          distance=m['distance'],
          type=m['type'],
          modifier=m['modifier'],
          instruction=m['instruction'],
        )
        for m in progress['all_maneuvers']
      ]
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
