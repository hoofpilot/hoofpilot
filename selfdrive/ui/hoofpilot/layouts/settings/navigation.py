"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import json
import os
import threading
from functools import partial

import requests

from openpilot.common.api import Api
from openpilot.common.params import Params
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import DialogResult, Widget
from openpilot.system.ui.widgets.confirm_dialog import alert_dialog
from openpilot.system.ui.widgets.list_view import button_item, toggle_item
from openpilot.system.ui.widgets.option_dialog import MultiOptionDialog
from openpilot.system.ui.widgets.scroller_tici import Scroller

from openpilot.system.ui.hoofpilot.widgets.input_dialog import InputDialogSP
from openpilot.system.ui.hoofpilot.widgets.list_view import multiple_button_item_sp

KONIK_API_HOST = os.getenv('API_HOST', 'https://api.konik.ai')


class NavigationLayout(Widget):
  def __init__(self):
    super().__init__()
    self._params = Params()
    self._poll_stop = threading.Event()
    self._poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
    self._poll_thread.start()

    self._route_item = button_item(
      "Current route", "Edit", "",
      self._show_dest_input,
    )

    self._show_nav_widget_item = toggle_item(
      "Show navigation widget",
      "Replace the driving mode selector on the homescreen with the current navigation destination",
      initial_state=self._safe_get_bool("ShowNavWidget"),
      callback=self._on_show_nav_widget,
    )

    self.items = [
      self._route_item,
      button_item("Clear route", "Clear", "", self._clear_route),
      multiple_button_item_sp("Favorites", "Navigate to saved location", ["Home", "Work", "Favorites"], 0, callback=self._favorites_callback),
      button_item("Set Home", "Set", "", partial(self._open_fav_dialog, "home", "Set Home Address")),
      button_item("Set Work", "Set", "", partial(self._open_fav_dialog, "work", "Set Work Address")),
      button_item("Add Favorite", "Add", "Add a new favorite destination", self._add_fav),
      button_item("Remove Favorite", "Remove", "Remove a saved favorite", self._remove_fav),
      self._show_nav_widget_item,
    ]
    self._scroller = Scroller(self.items, line_separator=True, spacing=0)

  # --- Konik API polling (runs in background thread) ---

  def _poll_loop(self):
    # Poll immediately, then every 10 seconds
    while not self._poll_stop.wait(0):
      self._fetch_konik_next()
      if self._poll_stop.wait(10):
        break

  def _fetch_konik_next(self):
    try:
      dongle_id = self._safe_get('DongleId', '')
      if not dongle_id:
        return
      token = Api(dongle_id).get_token()
      resp = requests.get(
        f'{KONIK_API_HOST}/v1/navigation/{dongle_id}/next',
        headers={'Authorization': f'JWT {token}'},
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
      if place_name:
        nav_dest = json.dumps({'latitude': lat, 'longitude': lon, 'place_name': place_name, 'place_details': dest.get('place_details', '')})
        self._safe_put('NavDestination', nav_dest)
        self._safe_put('MapboxRoute', place_name)
    except Exception:
      pass

  # --- Safe param helpers (guard against uncompiled keys) ---

  def _safe_get(self, key, default=""):
    try:
      return self._params.get(key) or default
    except Exception:
      return default

  def _safe_get_bool(self, key, default=False):
    try:
      return self._params.get_bool(key)
    except Exception:
      return default

  def _on_show_nav_widget(self, state: bool):
    try:
      self._params.put_bool("ShowNavWidget", state)
    except Exception:
      pass

  def _safe_put(self, key, value):
    try:
      self._params.put(key, value)
    except Exception:
      pass

  def _safe_remove(self, key):
    try:
      self._params.remove(key)
    except Exception:
      pass

  # --- Favorites storage ---

  @property
  def _favs(self):
    try:
      return json.loads(self._safe_get("MapboxFavorites", "{}"))
    except Exception:
      return {}

  def _save_favs(self, favs):
    self._safe_put("MapboxFavorites", json.dumps(favs))

  # --- Destination input ---

  def _show_dest_input(self):
    current = self._safe_get("MapboxRoute", "")
    InputDialogSP("Enter destination address", current_text=current, callback=self._set_dest_cb).show()

  def _set_dest_cb(self, res, text):
    if res == DialogResult.CONFIRM and text:
      self._safe_put("MapboxRoute", text)
      # Clear any previous NavDestination so navigationd re-geocodes via MapboxRoute
      self._safe_remove("NavDestination")

  # --- Clear route ---

  def _clear_route(self):
    self._safe_remove("MapboxRoute")
    self._safe_remove("NavDestination")

  # --- Favorites management ---

  def _handle_save_fav(self, key, is_fav, res, text):
    if res == DialogResult.CONFIRM and text:
      favs = self._favs
      (favs.setdefault("favorites", {}) if is_fav else favs)[key] = text
      self._save_favs(favs)

  def _open_fav_dialog(self, key, title):
    InputDialogSP(title, current_text=self._favs.get(key, ""), callback=partial(self._handle_save_fav, key, False)).show()

  def _add_fav_name_cb(self, res, name):
    if res == DialogResult.CONFIRM and name:
      InputDialogSP(f"Set address for '{name}'", "", callback=partial(self._handle_save_fav, name, True), min_text_size=1).show()

  def _add_fav(self):
    InputDialogSP("Favorite name", "", callback=self._add_fav_name_cb, min_text_size=1).show()

  def _set_mapbox_route_cb(self, favorites, selection):
    self._safe_put("MapboxRoute", favorites[selection])
    self._safe_remove("NavDestination")

  def _favorites_callback(self, index):
    favs = self._favs
    if index < 2:
      if route := favs.get(["home", "work"][index]):
        self._safe_put("MapboxRoute", route)
        self._safe_remove("NavDestination")
    elif favorites := favs.get("favorites"):
      self._show_list_dialog(tr("Select Favorite"), list(favorites.keys()), partial(self._set_mapbox_route_cb, favorites))
    else:
      gui_app.set_modal_overlay(alert_dialog(tr("No custom favorites set")))

  def _remove_fav_cb(self, selection):
    favs = self._favs
    if favs.get("favorites", {}).pop(selection, None):
      self._save_favs(favs)

  def _remove_fav(self):
    if favorites := self._favs.get("favorites"):
      self._show_list_dialog(tr("Remove Favorite"), list(favorites.keys()), self._remove_fav_cb)
    else:
      gui_app.set_modal_overlay(alert_dialog(tr("No custom favorites to remove")))

  def _list_dialog_cb(self, callback, res):
    if res == DialogResult.CONFIRM and self._dialog.selection:
      callback(self._dialog.selection)
    gui_app.set_modal_overlay(None)

  def _show_list_dialog(self, title, items, callback):
    self._dialog = MultiOptionDialog(title, items)
    gui_app.set_modal_overlay(self._dialog, callback=partial(self._list_dialog_cb, callback))

  # --- Rendering ---

  def _update_state(self):
    try:
      dest = None
      # Prefer place_name from NavDestination JSON (set via Athena from Konik Stable)
      nav_dest_str = self._safe_get("NavDestination", "")
      if nav_dest_str:
        try:
          dest = json.loads(nav_dest_str).get("place_name") or None
        except Exception:
          pass
      # Fall back to raw MapboxRoute text (set via device UI or on-device favorites)
      if not dest:
        dest = self._safe_get("MapboxRoute", "") or None
      self._route_item.action_item.set_value(dest or "Destination not set")
    except Exception:
      pass

  def _render(self, rect):
    self._scroller.render(rect)

  def show_event(self):
    self._scroller.show_event()
