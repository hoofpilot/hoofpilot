"""
Copyright (c) 2021-, James Vecellio, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import os
import time
import requests
from urllib.parse import quote

from openpilot.common.params import Params

CONNECT_MAPBOX_TOKEN = os.getenv("CONNECT_MAPBOX_TOKEN", "")
MAPBOX_TOKEN_GIST_API = os.getenv("MAPBOX_TOKEN_GIST_API", "https://api.github.com/gists/115caba1efdffe0b6d0d6dfcabf709ff")
MAPBOX_TOKEN_GIST_FILE = os.getenv("MAPBOX_TOKEN_GIST_FILE", "mapbox.token")
MAPBOX_TOKEN_GIST_REFRESH_SEC = max(float(os.getenv("MAPBOX_TOKEN_GIST_REFRESH_SEC", "300")), 10.0)
MAPBOX_TOKEN_FETCH_TIMEOUT_SEC = max(float(os.getenv("MAPBOX_TOKEN_FETCH_TIMEOUT_SEC", "3")), 1.0)

_GIST_TOKEN_CACHE = {
  'token': "",
  'etag': "",
  'checked_at_monotonic': 0.0,
}


def _is_mapbox_token(token: str | None) -> bool:
  return isinstance(token, str) and token.startswith('pk.') and len(token) >= 32


def _get_cached_gist_token() -> str:
  cached = _GIST_TOKEN_CACHE.get('token')
  return cached if isinstance(cached, str) else ""


def _set_cached_gist_token(token: str) -> None:
  _GIST_TOKEN_CACHE['token'] = token


def _set_cache_checked_now() -> None:
  _GIST_TOKEN_CACHE['checked_at_monotonic'] = time.monotonic()


def _should_refresh_gist_token(force_refresh: bool) -> bool:
  if force_refresh:
    return True

  if not _is_mapbox_token(_get_cached_gist_token()):
    return True

  last_checked = _GIST_TOKEN_CACHE.get('checked_at_monotonic')
  if not isinstance(last_checked, (int, float)) or last_checked <= 0:
    return True

  return (time.monotonic() - float(last_checked)) >= MAPBOX_TOKEN_GIST_REFRESH_SEC


def _extract_token_from_gist_payload(data) -> str:
  if not isinstance(data, dict):
    return ""

  files = data.get('files', {})
  if not isinstance(files, dict) or not files:
    return ""

  file_data = files.get(MAPBOX_TOKEN_GIST_FILE)
  if not isinstance(file_data, dict):
    file_data = next((f for f in files.values() if isinstance(f, dict)), {})

  content = file_data.get('content', '') if isinstance(file_data, dict) else ''
  token = content.strip() if isinstance(content, str) else ''
  return token if _is_mapbox_token(token) else ""


def _get_gist_mapbox_token(force_refresh: bool = False) -> str:
  if not MAPBOX_TOKEN_GIST_API:
    return ""

  cached_token = _get_cached_gist_token()
  if not _should_refresh_gist_token(force_refresh):
    return cached_token

  headers = {}
  cached_etag = _GIST_TOKEN_CACHE.get('etag')
  if isinstance(cached_etag, str) and cached_etag:
    headers['If-None-Match'] = cached_etag

  _set_cache_checked_now()
  try:
    response = requests.get(MAPBOX_TOKEN_GIST_API, headers=headers, timeout=MAPBOX_TOKEN_FETCH_TIMEOUT_SEC)
  except (requests.RequestException, ValueError, TypeError):
    return cached_token

  if response.status_code == 304:
    return cached_token

  if response.status_code != 200:
    return cached_token

  etag = response.headers.get('ETag') or response.headers.get('etag')
  if isinstance(etag, str) and etag:
    _GIST_TOKEN_CACHE['etag'] = etag

  try:
    data = response.json()
  except ValueError:
    return cached_token

  token = _extract_token_from_gist_payload(data)
  if not token:
    return cached_token

  if token != cached_token:
    _set_cached_gist_token(token)

  return token


class MapboxIntegration:
  def __init__(self):
    self.params = Params()

  def get_public_token(self) -> str:
    # Prefer the device param; fall back to env var for deployments that inject token at runtime.
    try:
      token = self.params.get('MapboxToken', return_default=True)
    except Exception:
      token = None

    if isinstance(token, bytes):
      token = token.decode('utf-8', errors='ignore')
    if isinstance(token, str):
      token = token.strip()

    if _is_mapbox_token(token):
      return token

    env_token = CONNECT_MAPBOX_TOKEN.strip()
    if _is_mapbox_token(env_token):
      return env_token

    gist_token = _get_gist_mapbox_token()
    if _is_mapbox_token(gist_token):
      return gist_token

    return ""

  def set_destination(self, postvars, current_lon, current_lat, bearing=None) -> tuple[dict, bool]:
    if 'latitude' in postvars and 'longitude' in postvars:
      self.nav_confirmed(postvars, current_lon, current_lat, bearing)
      return postvars, True

    addr = postvars['place_name']
    if not addr:
      return postvars, False

    token = self.get_public_token()
    if not token:
      return postvars, False

    url = f'https://api.mapbox.com/geocoding/v5/mapbox.places/{quote(addr)}.json?access_token={token}&limit=1&proximity={current_lon},{current_lat}'
    try:
      response = requests.get(url, timeout=5)
      if response.status_code == 200:
        features = response.json()['features']
        if features:
          longitude, latitude = features[0]['geometry']['coordinates']
          postvars.update({'latitude': latitude, 'longitude': longitude, 'name': addr})
          self.nav_confirmed(postvars, current_lon, current_lat, bearing)
          return postvars, True
    except requests.RequestException:
      pass  # Broad exception to handle network errors like no internet without crashing navd process.
    return postvars, False

  def nav_confirmed(self, postvars, start_lon, start_lat, bearing=None) -> None:
    if not postvars:
      return

    latitude = float(postvars['latitude'])
    longitude = float(postvars['longitude'])

    data: dict = {'navData': {'current': {'latitude': latitude, 'longitude': longitude}, 'route': {}}}

    token = self.get_public_token()
    route_data = self.generate_route(start_lon, start_lat, longitude, latitude, token, bearing)
    if route_data:
      data['navData']['route'] = route_data
    self.params.put('MapboxSettings', data)

  @staticmethod
  def generate_route(start_lon, start_lat, end_lon, end_lat, token, bearing=None) -> dict | None:
    if not token:
      return None

    params = {
      'access_token': token,
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
      response = requests.get(f'https://api.mapbox.com/directions/v5/mapbox/driving/{start_lon},{start_lat};{end_lon},{end_lat}', params=params, timeout=5)
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
