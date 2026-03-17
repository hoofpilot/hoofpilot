#!/usr/bin/env python3
"""
Fake navigationd publisher for UI testing on device without GPS.

Usage (SSH into comma):
  1. pkill -f navigationd        # stop real daemon
  2. python test_nav_publisher.py

The UI will render the nav banner as if a real route is active.
Press Ctrl+C to stop.
"""
import time
import cereal.messaging as messaging
from cereal import custom

# ── Fake route data ───────────────────────────────────────────────────────────
FAKE_MANEUVERS = [
  {
    'distance': 482.0,    # ~0.3 mi
    'type': 'turn',
    'modifier': 'right',
    'instruction': 'Emory Street',
  },
  {
    'distance': 1609.0,   # ~1.0 mi
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
SPEED_LIMIT  = 65   # km/h or mph — whatever your UI is set to


def main():
  pm = messaging.PubMaster(['navigationd'])
  print('Publishing fake navigationd at 3 Hz — kill with Ctrl+C')

  # Slowly tick distance down to simulate approach
  distance = FAKE_MANEUVERS[0]['distance']
  while True:
    msg = messaging.new_message('navigationd')
    msg.valid = True

    nd = msg.navigationd
    nd.upcomingTurn   = 'right'
    nd.currentSpeedLimit = SPEED_LIMIT
    nd.bannerInstructions = BANNER_TEXT
    nd.distanceFromRoute  = 0.0
    nd.valid = True

    maneuvers = []
    for i, m in enumerate(FAKE_MANEUVERS):
      maneuver = custom.Navigationd.Maneuver.new_message(
        distance   = distance if i == 0 else m['distance'],
        type       = m['type'],
        modifier   = m['modifier'],
        instruction= m['instruction'],
      )
      maneuvers.append(maneuver)

    nd.allManeuvers = maneuvers
    pm.send('navigationd', msg)

    # Slowly decrement distance so you can see it counting down
    distance = max(10.0, distance - 5.0)
    if distance <= 10.0:
      distance = FAKE_MANEUVERS[0]['distance']   # loop back

    time.sleep(1 / 3)   # 3 Hz


if __name__ == '__main__':
  main()
