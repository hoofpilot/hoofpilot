#!/usr/bin/env python3
"""
Usage::

  usage: auth.py [-h] [{github,jwt}] [jwt]

  Login to your comma account

  positional arguments:
    {github,jwt}
    jwt

  optional arguments:
    -h, --help            show this help message and exit


Examples::

  ./auth.py  # Log in with GitHub account
  ./auth.py github  # Log in with GitHub account
  ./auth.py jwt ey......hw  # Log in with a JWT from https://jwt.comma.ai, for use in CI
"""

import argparse
import os
import sys
import pprint
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from urllib.parse import parse_qs, urlencode, urljoin

from openpilot.tools.lib.api import APIError, CommaApi, UnauthorizedError
from openpilot.tools.lib.auth_config import set_token, get_token

PREFERRED_PORT = 3000
DEFAULT_API_HOST = 'https://api.konik.ai/'


def _api_base() -> str:
  base = os.getenv('API_HOST', DEFAULT_API_HOST)
  if not base.endswith('/'):
    base += '/'
  return base


class ClientRedirectServer(HTTPServer):
  query_params: dict[str, Any] = {}
  allow_reuse_address = True


class ClientRedirectHandler(BaseHTTPRequestHandler):
  def do_GET(self):
    if not self.path.startswith('/auth'):
      self.send_response(204)
      self.end_headers()
      return

    query = self.path.split('?', 1)[-1]
    query_parsed = parse_qs(query, keep_blank_values=True)
    self.server.query_params = query_parsed

    self.send_response(200)
    self.send_header('Content-type', 'text/plain')
    self.end_headers()
    self.wfile.write(b'Return to the CLI to continue')

  def log_message(self, *args):
    pass  # this prevent http server from dumping messages to stdout


def auth_redirect_link(method: str, port: int) -> str:
  if method != 'github':
    raise NotImplementedError(f"only github auth is supported (got {method})")
  provider_id = 'h'

  redirect_uri = urljoin(_api_base(), f"v2/auth/{provider_id}/redirect/")
  params = {
    'redirect_uri': redirect_uri,
    'state': f'service,localhost:{port}',
  }

  params.update({
    'client_id': 'Ov23liy0AI1YCd15pypf',
    'scope': 'read:user',
  })
  return 'https://github.com/login/oauth/authorize?' + urlencode(params)


def _first_param(params: dict[str, list[str]], name: str) -> str | None:
  v = params.get(name)
  if not v:
    return None
  return v[0]


def _create_redirect_server(preferred_port: int) -> ClientRedirectServer:
  for port in (preferred_port, 0):
    try:
      return ClientRedirectServer(('localhost', port), ClientRedirectHandler)
    except OSError as e:
      # EADDRINUSE; retry with an ephemeral port.
      if port != 0:
        continue
      raise e
  raise OSError("Failed to create redirect server")


def login(method):
  web_server = _create_redirect_server(PREFERRED_PORT)
  port = web_server.server_address[1]
  oauth_uri = auth_redirect_link(method, port)

  print(f'To sign in, use your browser and navigate to {oauth_uri}')
  webbrowser.open(oauth_uri, new=2)

  try:
    while True:
      web_server.handle_request()
      if 'code' in web_server.query_params:
        break
      elif 'error' in web_server.query_params:
        print('Authentication Error: "{}". Description: "{}" '.format(
          _first_param(web_server.query_params, 'error'),
          _first_param(web_server.query_params, 'error_description')), file=sys.stderr)
        return
  finally:
    web_server.server_close()

  try:
    code = _first_param(web_server.query_params, 'code')
    provider = _first_param(web_server.query_params, 'provider')
    if code is None or provider is None:
      raise APIError("missing required query params from redirect (expected code and provider)")
    auth_resp = CommaApi().post('v2/auth/', data={'code': code, 'provider': provider})
    set_token(auth_resp['access_token'])
  except APIError as e:
    print(f'Authentication Error: {e}', file=sys.stderr)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Login to your Konik account')
  parser.add_argument('method', default='github', const='github', nargs='?', choices=['github', 'jwt'])
  parser.add_argument('jwt', nargs='?')

  args = parser.parse_args()
  if args.method == 'jwt':
    if args.jwt is None:
      print("method JWT selected, but no JWT was provided")
      exit(1)

    set_token(args.jwt)
  else:
    login(args.method)

  try:
    me = CommaApi(token=get_token()).get('/v1/me')
    print("Authenticated!")
    pprint.pprint(me)
  except UnauthorizedError:
    print("Got invalid JWT")
    exit(1)
