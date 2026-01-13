import pyray as rl
from openpilot.common.constants import CV
from openpilot.common.params import Params
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app, FontWeight, FONT_SCALE
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets import Widget

PARAM_KEY = "ApiCache_DriveStats"

TITLE_FONT_SIZE = 51
NUMBER_FONT_SIZE = 78
UNIT_FONT_SIZE = 51

BG_COLOR = rl.Color(51, 51, 51, 255)
UNIT_COLOR = rl.Color(160, 160, 160, 255)


class DriveStatsWidget(Widget):
  def __init__(self, params: Params):
    super().__init__()
    self._params = params
    self._font_medium = gui_app.font(FontWeight.MEDIUM)
    self._font_regular = gui_app.font(FontWeight.NORMAL)
    self._stats = {"all": {}, "week": {}}
    self._metric = ui_state.is_metric
    self._set_defaults()

  def set_parent_rect(self, parent_rect: rl.Rectangle) -> None:
    super().set_parent_rect(parent_rect)
    self._rect.width = parent_rect.width
    self._rect.height = self._compute_height()

  def _compute_height(self) -> float:
    section_height = (
      TITLE_FONT_SIZE * FONT_SCALE +
      30 +
      NUMBER_FONT_SIZE * FONT_SCALE +
      10 +
      UNIT_FONT_SIZE * FONT_SCALE +
      20
    )
    return 30 + 50 + section_height + 40 + section_height + 50 + 30

  def _set_defaults(self):
    self._stats["all"] = {"routes": 0, "distance": 0.0, "minutes": 0.0}
    self._stats["week"] = {"routes": 0, "distance": 0.0, "minutes": 0.0}

  def _update_state(self):
    data = self._params.get(PARAM_KEY) or {}
    if isinstance(data, dict):
      self._stats["all"] = data.get("all", self._stats["all"])
      self._stats["week"] = data.get("week", self._stats["week"])
    self._metric = ui_state.is_metric

  def _render(self, rect):
    content_x = rect.x + 50
    content_y = rect.y + 50
    content_w = rect.width - 100

    content_y = self._draw_section(tr("ALL TIME"), self._stats["all"], content_x, content_y, content_w)
    content_y += 40
    self._draw_section(tr("PAST WEEK"), self._stats["week"], content_x, content_y, content_w)

  def _draw_section(self, title, stats, x, y, width):
    rl.draw_text_ex(self._font_medium, title, rl.Vector2(x, y), TITLE_FONT_SIZE, 0, rl.WHITE)
    y += int(TITLE_FONT_SIZE * FONT_SCALE) + 30

    col_width = width / 3
    routes = int(stats.get("routes", 0) or 0)
    distance = float(stats.get("distance", 0.0) or 0.0)
    minutes = float(stats.get("minutes", 0.0) or 0.0)
    distance_val = int(distance * (CV.MPH_TO_KPH if self._metric else 1.0))
    hours_val = int(minutes / 60.0)

    values = [str(routes), str(distance_val), str(hours_val)]
    units = [tr("Drives"), tr("KM") if self._metric else tr("Miles"), tr("Hours")]

    for idx, value in enumerate(values):
      cell_x = x + col_width * idx
      text_size = measure_text_cached(self._font_medium, value, NUMBER_FONT_SIZE)
      value_x = cell_x + (col_width - text_size.x) / 2
      rl.draw_text_ex(self._font_medium, value, rl.Vector2(value_x, y), NUMBER_FONT_SIZE, 0, rl.WHITE)

    y += int(NUMBER_FONT_SIZE * FONT_SCALE) + 10

    for idx, unit in enumerate(units):
      cell_x = x + col_width * idx
      unit_size = measure_text_cached(self._font_regular, unit, UNIT_FONT_SIZE)
      unit_x = cell_x + (col_width - unit_size.x) / 2
      rl.draw_text_ex(self._font_regular, unit, rl.Vector2(unit_x, y), UNIT_FONT_SIZE, 0, UNIT_COLOR)

    y += int(UNIT_FONT_SIZE * FONT_SCALE) + 20
    return y
