#!/usr/bin/env python3
import os

from openpilot.system.hardware import TICI
from openpilot.common.realtime import config_realtime_process, set_core_affinity
from openpilot.system.ui.lib.application import gui_app, OFFROAD_FPS, ONROAD_FPS
from openpilot.selfdrive.ui.layouts.main import MainLayout
from openpilot.selfdrive.ui.mici.layouts.main import MiciMainLayout
from openpilot.selfdrive.ui.ui_state import ui_state

BIG_UI = gui_app.big_ui()


def main():
  cores = {5, }
  config_realtime_process(0, 51)

  gui_app.init_window("UI", fps=OFFROAD_FPS)
  if BIG_UI:
    MainLayout()
  else:
    MiciMainLayout()

  def _on_road_transition():
    gui_app.set_fps(ONROAD_FPS if ui_state.started else OFFROAD_FPS)
  ui_state.add_offroad_transition_callback(_on_road_transition)

  for should_render in gui_app.render():
    ui_state.update()
    if should_render:
      # reaffine after power save offlines our core
      if TICI and os.sched_getaffinity(0) != cores:
        try:
          set_core_affinity(list(cores))
        except OSError:
          pass


if __name__ == "__main__":
  main()
