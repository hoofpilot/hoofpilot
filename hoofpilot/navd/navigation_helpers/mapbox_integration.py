"""
Copyright (c) 2021-, James Vecellio, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import os
import requests
from urllib.parse import quote

from openpilot.common.api import Api
from openpilot.common.params import Params

KONIK_API_HOST = os.getenv('API_HOST', 'https://api.konik.ai')
MAPS_BASE = f'{KONIK_API_HOST}/maps'


class MapboxIntegration:
  def __init__(self):
    self.params = Params()

  def _auth_headers(self) -> dict:
    dongle_id = self.params.get('DongleId', return_default=True) or ''
    try:
      token = Api(dongle_id).get_token()
      return {'Authorization': f'JWT {token}'}
    except Exception:
      return {}

  def set_destination(self, postvars, current_lon, current_lat, bearing=None) -> tuple[dict, bool]:
    if 'latitude' in postvars and 'longitude' in postvars:
      self.nav_confirmed(postvars, current_lon, current_lat, bearing)
      return postvars, True

    addr = postvars['place_name']
    if not addr:
      return postvars, False

    url = f'{MAPS_BASE}/geocoding/v5/mapbox.places/{quote(addr)}.json'
    try:
      response = requests.get(
        url,
        params={'limit': '1', 'proximity': f'{current_lon},{current_lat}'},
        headers=self._auth_headers(),
        timeout=5,
      )
      if response.status_code == 200:
        features = response.json()['features']
        if features:
          longitude, latitude = features[0]['geometry']['coordinates']
          postvars.update({'latitude': latitude, 'longitude': longitude, 'name': addr})
          self.nav_confirmed(postvars, current_lon, current_lat, bearing)
          return postvars, True
    except requests.RequestException:
      pass
    return postvars, False

  def nav_confirmed(self, postvars, start_lon, start_lat, bearing=None) -> None:
    if not postvars:
      return

    latitude = float(postvars['latitude'])
    longitude = float(postvars['longitude'])

    data: dict = {'navData': {'current': {'latitude': latitude, 'longitude': longitude}, 'route': {}}}

    route_data = self.generate_route(start_lon, start_lat, longitude, latitude, self._auth_headers(), bearing)
    if route_data:
      data['navData']['route'] = route_data
    self.params.put('MapboxSettings', data)

  @staticmethod
  def generate_route(start_lon, start_lat, end_lon, end_lat, auth_headers, bearing=None) -> dict | None:
    params = {
      'geometries': 'geojson',
      'steps': 'true',
      'overview': 'full',
      'annotations': 'maxspeed',
      'alternatives': 'false',
      'banner_instructions': 'true',
    }
    if bearing is not None:
      params['bearings'] = f'{int((bearing + 360) % 360):.0f},90;'

    try:
      response = requests.get(
        f'{MAPS_BASE}/directions/v5/mapbox/driving/{start_lon},{start_lat};{end_lon},{end_lat}',
        params=params,
        headers=auth_headers,
        timeout=5,
      )
      data = response.json() if response.status_code == 200 else {}
    except requests.RequestException:
      return None

    routes = data['routes'] if data else None
    legs = routes[0]['legs'] if routes else None

    if data.get('code') != 'Ok' or not routes or not legs:
      return None

    route = routes[0]
    leg = legs[0]

    steps = [
      {
        'maneuver': step['maneuver']['type'],
        'instruction': step['maneuver']['instruction'],
        'distance': step['distance'],
        'duration': step['duration'],
        'location': {'longitude': step['maneuver']['location'][0], 'latitude': step['maneuver']['location'][1]},
        'modifier': step['maneuver'].get('modifier', 'none'),
        'bannerInstructions': step['bannerInstructions'],
      }
      for step in leg['steps']
    ]

    maxspeed = [{'speed': item['speed'], 'unit': item['unit']} for item in leg['annotation']['maxspeed'] if 'speed' in item]

    return {
      'steps': steps,
      'totalDistance': route['distance'],
      'totalDuration': route['duration'],
      'geometry': [{'longitude': coord[0], 'latitude': coord[1]} for coord in route['geometry']['coordinates']],
      'maxspeed': maxspeed,
    }
