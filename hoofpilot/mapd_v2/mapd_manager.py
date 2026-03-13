"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
#!/usr/bin/env python3
import json
import platform
import os
import glob
import shutil
from datetime import datetime

from cereal import messaging
from openpilot.common.params import Params
from openpilot.common.realtime import Ratekeeper, config_realtime_process
from openpilot.common.swaglog import cloudlog
from openpilot.selfdrive.selfdrived.alertmanager import set_offroad_alert
from hoofpilot.mapd_v2.live_map_data.osm_map_data import OsmMapData
from openpilot.system.hardware.hw import Paths
from hoofpilot.mapd_v2 import MAPD_PATH
from hoofpilot.mapd_v2.mapd_installer import VERSION, update_installed_version

# PFEIFER - MAPD {{
params = Params()
mem_params = Params("/dev/shm/params") if platform.system() != "Darwin" else params
# }} PFEIFER - MAPD

MAPD_INPUT_DOWNLOAD = 0


def get_files_for_cleanup() -> list[str]:
  paths = [
    f"{Paths.mapd_root()}/db",
    f"{Paths.mapd_root()}/v*"
  ]
  files_to_remove = []
  for path in paths:
    if os.path.exists(path):
      files = glob.glob(path + '/**', recursive=True)
      files_to_remove.extend(files)
  # check for version and mapd files
  if not os.path.isfile(MAPD_PATH):
    files_to_remove.append(MAPD_PATH)
  return files_to_remove


def cleanup_old_osm_data(files_to_remove: list[str]) -> None:
  for file in files_to_remove:
    # Remove trailing slash if path is file
    if file.endswith('/') and os.path.isfile(file[:-1]):
      file = file[:-1]
    # Try to remove as file or symbolic link first
    if os.path.islink(file) or os.path.isfile(file):
      os.remove(file)
    elif os.path.isdir(file):  # If it's a directory
      shutil.rmtree(file, ignore_errors=False)


def build_download_locations(nations: list[str], states: list[str] | None = None) -> str:
  locations = [f"nation.{nation}" for nation in nations if nation]
  locations.extend(f"us_state.{state}" for state in (states or []) if state and state.lower() != "all")
  locations = sorted(set(locations))
  return ",".join(locations)


def request_refresh_osm_location_data(nations: list[str], states: list[str] | None, mapd_pub_master: messaging.PubMaster) -> bool:
  params.put("OsmDownloadedDate", str(datetime.now().timestamp()))
  params.put_bool("OsmDbUpdatesCheck", False)

  osm_download_locations = {
    "nations": nations,
    "states": states or []
  }

  download_locations = build_download_locations(nations, states)
  if not download_locations:
    return False

  print(f"Downloading maps for {json.dumps(osm_download_locations)}")
  mem_params.put("OSMDownloadLocations", osm_download_locations)
  params.put("OSMDownloadProgress", {"total_files": 0, "downloaded_files": 0})

  msg = messaging.new_message("mapdIn")
  msg.mapdIn.type = MAPD_INPUT_DOWNLOAD
  msg.mapdIn.str = download_locations
  mapd_pub_master.send("mapdIn", msg)
  return True


def filter_nations_and_states(nations: list[str], states: list[str] | None = None) -> tuple[list[str], list[str]]:
  """Filters and prepares nation and state data for OSM map download.

  If the nation is 'US' and a specific state is provided, the nation 'US' is removed from the list.
  If the nation is 'US' and the state is 'All', the 'All' is removed from the list.
  The idea behind these filters is that if a specific state in the US is provided,
  there's no need to download map data for the entire US. Conversely,
  if the state is unspecified (i.e., 'All'), we intend to download map data for the whole US,
  and 'All' isn't a valid state name, so it's removed.

  Parameters:
  nations (list): A list of nations for which the map data is to be downloaded.
  states (list, optional): A list of states for which the map data is to be downloaded. Defaults to None.

  Returns:
  tuple: Two lists. The first list is filtered nations and the second list is filtered states.
  """

  if "US" in nations and states and not any(x.lower() == "all" for x in states):
    # If a specific state in the US is provided, remove 'US' from nations
    nations.remove("US")
  elif "US" in nations and states and any(x.lower() == "all" for x in states):
    # If 'All' is provided as a state (case invariant), remove those instances from states
    states = [x for x in states if x.lower() != "all"]
  elif "US" not in nations and states and any(x.lower() == "all" for x in states):
    states.remove("All")
  return nations, states or []


def update_osm_db(mapd_pub_master: messaging.PubMaster) -> bool:
  download_requested = False
  if params.get_bool("OsmDbUpdatesCheck"):
    cleanup_old_osm_data(get_files_for_cleanup())
    country = params.get("OsmLocationName", return_default=True)
    state = params.get("OsmStateName", return_default=True)
    filtered_nations, filtered_states = filter_nations_and_states([country], [state])
    download_requested = request_refresh_osm_location_data(filtered_nations, filtered_states, mapd_pub_master)

  if not mem_params.get("OSMDownloadBounds"):
    mem_params.put("OSMDownloadBounds", "")

  if not mem_params.get("LastGPSPosition"):
    mem_params.put("LastGPSPosition", "{}")

  return download_requested


def mapd_progress_to_dict(download_progress) -> dict:
  return {
    "active": bool(download_progress.active),
    "cancelled": bool(download_progress.cancelled),
    "total_files": int(download_progress.totalFiles),
    "downloaded_files": int(download_progress.downloadedFiles),
    "locations": list(download_progress.locations),
    "location_details": [
      {
        "location": str(location_detail.location),
        "total_files": int(location_detail.totalFiles),
        "downloaded_files": int(location_detail.downloadedFiles),
      }
      for location_detail in download_progress.locationDetails
    ],
  }


def mapd_path_to_target_velocities(path_points) -> str:
  target_velocities = [
    {
      "latitude": float(path_point.latitude),
      "longitude": float(path_point.longitude),
      "velocity": float(path_point.targetVelocity),
    }
    for path_point in path_points
  ]
  return json.dumps(target_velocities, separators=(",", ":"))


def update_mapd_outputs(mapd_sub_master: messaging.SubMaster, download_requested: bool, download_started: bool,
                        previous_target_velocities: str | None) -> tuple[bool, bool, str | None]:
  if not mapd_sub_master.updated["mapdExtendedOut"]:
    return download_requested, download_started, previous_target_velocities

  mapd_extended_out = mapd_sub_master["mapdExtendedOut"]
  download_progress = mapd_extended_out.downloadProgress
  params.put("OSMDownloadProgress", mapd_progress_to_dict(download_progress))

  if download_progress.active:
    download_started = True
    if not mem_params.get("OSMDownloadLocations"):
      mem_params.put("OSMDownloadLocations", {"locations": list(download_progress.locations)})
  elif download_requested and (
    download_started or
    download_progress.cancelled or
    (download_progress.totalFiles > 0 and download_progress.downloadedFiles >= download_progress.totalFiles)
  ):
    mem_params.remove("OSMDownloadLocations")
    download_requested = False
    download_started = False

  target_velocities = mapd_path_to_target_velocities(mapd_extended_out.path)
  if target_velocities != previous_target_velocities:
    mem_params.put("MapTargetVelocities", target_velocities)
    previous_target_velocities = target_velocities

  return download_requested, download_started, previous_target_velocities


def main_thread():
  update_installed_version(VERSION, params)
  config_realtime_process([0, 1, 2, 3], 5)

  rk = Ratekeeper(1, print_delay_threshold=None)
  live_map_sp = OsmMapData()
  mapd_pub_master = messaging.PubMaster(["mapdIn"])
  mapd_sub_master = messaging.SubMaster(["mapdExtendedOut"])

  download_requested = False
  download_started = False
  previous_target_velocities = None

  # Create folder needed for OSM
  try:
    os.mkdir(Paths.mapd_root())
  except FileExistsError:
    pass
  except PermissionError:
    cloudlog.exception(f"mapd: failed to make {Paths.mapd_root()}")

  while True:
    show_alert = get_files_for_cleanup() and params.get_bool("OsmLocal")
    set_offroad_alert("Offroad_OSMUpdateRequired", show_alert, "This alert will be cleared when new maps are downloaded.")

    if update_osm_db(mapd_pub_master):
      download_requested = True
      download_started = False

    mapd_sub_master.update(0)
    download_requested, download_started, previous_target_velocities = update_mapd_outputs(
      mapd_sub_master, download_requested, download_started, previous_target_velocities,
    )

    live_map_sp.tick()
    rk.keep_time()


def main():
  main_thread()


if __name__ == "__main__":
  main()

