#!/usr/bin/env python3
"""
Force hoofpilot into onroad mode and publish fake navigationd messages.

Usage (SSH into comma):
  1. pkill -f navigationd        # stop real daemon (if running)
  2. python test_onroad_forcer.py

This publishes:
  - deviceState  (started=True, so the UI enters onroad mode)
  - pandaStates  (ignitionLine=True, required alongside deviceState.started)
  - navigationd  (fake turn-by-turn maneuvers so the nav banner appears)

Press Ctrl+C to stop. When you stop, the UI will exit onroad mode.
"""
import time
import cereal.messaging as messaging
from cereal import custom, log

# ── Fake route data ───────────────────────────────────────────────────────────
FAKE_MANEUVERS = [
  {
    'distance': 482.0,
    'type': 'turn',
    'modifier': 'right',
    'instruction': 'Emory Street',
  },
  {
    'distance': 1609.0,
    'type': 'turn',
    'modifier': 'slight left',
    'instruction': 'Pacific Coast Highway',
  },
  {
    'distance': 3200.0,
    'type': 'fork',
    'modifier': 'slight right',
    'instruction': 'I-5 North',
  },
]

BANNER_TEXT = 'Emory Street'
FAKE_SPEED_MS = 13.4  # ~30 mph / ~48 km/h
FAKE_CRUISE_SPEED_MS = 15.6  # ~35 mph / ~56 km/h
FAKE_SPEED_LIMIT = 65  # km/h


def _make_device_state(pm):
  msg = messaging.new_message('deviceState')
  msg.valid = True
  ds = msg.deviceState
  ds.started = True
  ds.freeSpacePercent = 50.0
  ds.memoryUsagePercent = 40
  ds.cpuTempC = [45.0, 45.0]
  ds.gpuTempC = [50.0]
  ds.networkType = log.DeviceState.NetworkType.wifi
  pm.send('deviceState', msg)


def _make_panda_states(pm):
  msg = messaging.new_message('pandaStates', 1)
  msg.valid = True
  ps = msg.pandaStates[0]
  ps.ignitionLine = True
  ps.ignitionCan = True
  ps.pandaType = log.PandaState.PandaType.uno
  pm.send('pandaStates', msg)


def _make_navigationd(pm, distance):
  msg = messaging.new_message('navigationd')
  msg.valid = True
  nd = msg.navigationd
  nd.upcomingTurn = 'right'
  nd.currentSpeedLimit = FAKE_SPEED_LIMIT
  nd.bannerInstructions = BANNER_TEXT
  nd.distanceFromRoute = 0.0
  nd.valid = True

  maneuvers = []
  for i, m in enumerate(FAKE_MANEUVERS):
    maneuver = custom.Navigationd.Maneuver.new_message(
      distance=distance if i == 0 else m['distance'],
      type=m['type'],
      modifier=m['modifier'],
      instruction=m['instruction'],
    )
    maneuvers.append(maneuver)

  nd.allManeuvers = maneuvers
  pm.send('navigationd', msg)


def main():
  pm = messaging.PubMaster(['deviceState', 'pandaStates', 'navigationd'])
  print('Publishing fake deviceState + pandaStates + navigationd at 3 Hz')
  print('The UI should enter onroad mode and show the nav banner.')
  print('Kill with Ctrl+C\n')

  distance = FAKE_MANEUVERS[0]['distance']
  tick = 0

  while True:
    _make_device_state(pm)
    _make_panda_states(pm)
    _make_navigationd(pm, distance)

    distance = max(10.0, distance - 5.0)
    if distance <= 10.0:
      distance = FAKE_MANEUVERS[0]['distance']
      print('  [loop] distance reset')

    tick += 1
    if tick % 9 == 0:  # every ~3 seconds
      print(f'  distance to turn: {distance:.0f} m')

    time.sleep(1 / 3)  # 3 Hz


if __name__ == '__main__':
  main()
