import time
import pyray as rl
from dataclasses import dataclass
from cereal import messaging, log
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.hardware import TICI
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.label import Label

AlertSize = log.SelfdriveState.AlertSize
AlertStatus = log.SelfdriveState.AlertStatus

ALERT_MARGIN = 40
ALERT_PADDING = 60
ALERT_LINE_SPACING = 45
ALERT_BORDER_RADIUS = 30

ALERT_FONT_SMALL = 66
ALERT_FONT_MEDIUM = 74
ALERT_FONT_BIG = 88

ALERT_HEIGHTS = {
  AlertSize.small: 271,
  AlertSize.mid: 420,
}

SELFDRIVE_STATE_TIMEOUT = 5  # Seconds
SELFDRIVE_UNRESPONSIVE_TIMEOUT = 10  # Seconds

# Constants
ALERT_COLORS = {
  AlertStatus.normal: rl.Color(0x15, 0x15, 0x15, 0xF1),      # #151515 with alpha 0xF1
  AlertStatus.userPrompt: rl.Color(0xDA, 0x6F, 0x25, 0xF1),  # #DA6F25 with alpha 0xF1
  AlertStatus.critical: rl.Color(0xC9, 0x22, 0x31, 0xF1),    # #C92231 with alpha 0xF1
}


@dataclass
class Alert:
  text1: str = ""
  text2: str = ""
  size: int = 0
  status: int = 0


# Pre-defined alert instances
ALERT_STARTUP_PENDING = Alert(
  text1=tr("hoofpilot Unavailable"),
  text2=tr("Waiting to start"),
  size=AlertSize.mid,
  status=AlertStatus.normal,
)

ALERT_CRITICAL_TIMEOUT = Alert(
  text1=tr("TAKE CONTROL IMMEDIATELY"),
  text2=tr("System Unresponsive"),
  size=AlertSize.full,
  status=AlertStatus.critical,
)

ALERT_CRITICAL_REBOOT = Alert(
  text1=tr("System Unresponsive"),
  text2=tr("Reboot Device"),
  size=AlertSize.mid,
  status=AlertStatus.normal,
)


class AlertRenderer(Widget):
  def __init__(self):
    super().__init__()
    self.font_regular: rl.Font = gui_app.font(FontWeight.NORMAL)
    self.font_bold: rl.Font = gui_app.font(FontWeight.BOLD)
    self._last_alert: Alert | None = None
    self._last_alert_time = 0.0
    self._pending_alert: Alert | None = None
    self._pending_alert_time = 0.0
    self._startup_alert_until = 0.0
    self._startup_latch_until = 0.0
    self._startup_pending_active = False
    self._startup_pending_clear_after = 0.0

    # font size is set dynamically
    self._full_text1_label = Label("", font_size=0, font_weight=FontWeight.BOLD, text_alignment=rl.GuiTextAlignment.TEXT_ALIGN_CENTER,
                                   text_alignment_vertical=rl.GuiTextAlignmentVertical.TEXT_ALIGN_TOP)
    self._full_text2_label = Label("", font_size=ALERT_FONT_BIG, text_alignment=rl.GuiTextAlignment.TEXT_ALIGN_CENTER,
                                   text_alignment_vertical=rl.GuiTextAlignmentVertical.TEXT_ALIGN_TOP)

  def get_alert(self, sm: messaging.SubMaster) -> Alert | None:
    """Generate the current alert based on selfdrive state."""
    ss = sm['selfdriveState']

    # Check if selfdriveState messages have stopped arriving
    recv_frame = sm.recv_frame['selfdriveState']
    if not sm.updated['selfdriveState']:
      time_since_onroad = time.monotonic() - ui_state.started_time

      # 1. Never received selfdriveState since going onroad
      waiting_for_startup = recv_frame < ui_state.started_frame
      if waiting_for_startup and time_since_onroad > 5:
        # Latch startup pending until we have a stable selfdriveState update.
        self._startup_pending_active = True
        return ALERT_STARTUP_PENDING

      # 2. Lost communication with selfdriveState after receiving it
      if TICI and not waiting_for_startup:
        ss_missing = time.monotonic() - sm.recv_time['selfdriveState']
        if ss_missing > SELFDRIVE_STATE_TIMEOUT:
          if ss.enabled and (ss_missing - SELFDRIVE_STATE_TIMEOUT) < SELFDRIVE_UNRESPONSIVE_TIMEOUT:
            return ALERT_CRITICAL_TIMEOUT
          return ALERT_CRITICAL_REBOOT

    # Clear startup pending after a stable selfdriveState update.
    if self._startup_pending_active and sm.updated['selfdriveState'] and recv_frame >= ui_state.started_frame:
      if self._startup_pending_clear_after == 0.0:
        self._startup_pending_clear_after = time.monotonic() + 1.0
      elif time.monotonic() >= self._startup_pending_clear_after:
        self._startup_pending_active = False
        self._startup_pending_clear_after = 0.0

    if self._startup_pending_active:
      return ALERT_STARTUP_PENDING

    # No alert if size is none
    if ss.alertSize == 0:
      return None

    # Don't get old alert
    if recv_frame < ui_state.started_frame:
      return None

    # Return current alert
    return Alert(text1=ss.alertText1, text2=ss.alertText2, size=ss.alertSize.raw, status=ss.alertStatus.raw)

  def _render(self, rect: rl.Rectangle):
    alert = self._debounce_alert(self.get_alert(ui_state.sm))
    if not alert:
      return

    alert_rect = self._get_alert_rect(rect, alert.size)
    self._draw_background(alert_rect, alert)

    text_rect = rl.Rectangle(
      alert_rect.x + ALERT_PADDING,
      alert_rect.y + ALERT_PADDING,
      alert_rect.width - 2 * ALERT_PADDING,
      alert_rect.height - 2 * ALERT_PADDING
    )
    self._draw_text(text_rect, alert)

  def _get_alert_rect(self, rect: rl.Rectangle, size: int) -> rl.Rectangle:
    if size == AlertSize.full:
      return rect

    h = ALERT_HEIGHTS.get(size, rect.height)
    return rl.Rectangle(rect.x + ALERT_MARGIN, rect.y + rect.height - h + ALERT_MARGIN,
                        rect.width - ALERT_MARGIN * 2, h - ALERT_MARGIN * 2)

  def _draw_background(self, rect: rl.Rectangle, alert: Alert) -> None:
    color = ALERT_COLORS.get(alert.status, ALERT_COLORS[AlertStatus.normal])

    if alert.size != AlertSize.full:
      roundness = ALERT_BORDER_RADIUS / (min(rect.width, rect.height) / 2)
      rl.draw_rectangle_rounded(rect, roundness, 10, color)
    else:
      rl.draw_rectangle_rec(rect, color)

  def _draw_text(self, rect: rl.Rectangle, alert: Alert) -> None:
    if alert.size == AlertSize.small:
      self._draw_centered(alert.text1, rect, self.font_bold, ALERT_FONT_MEDIUM)

    elif alert.size == AlertSize.mid:
      self._draw_centered(alert.text1, rect, self.font_bold, ALERT_FONT_BIG, center_y=False)
      rect.y += ALERT_FONT_BIG + ALERT_LINE_SPACING
      self._draw_centered(alert.text2, rect, self.font_regular, ALERT_FONT_SMALL, center_y=False)

    else:
      is_long = len(alert.text1) > 15
      font_size1 = 132 if is_long else 177

      top_offset = 200 if is_long or '\n' in alert.text1 else 270
      title_rect = rl.Rectangle(rect.x, rect.y + top_offset, rect.width, 600)
      self._full_text1_label.set_font_size(font_size1)
      self._full_text1_label.set_text(alert.text1)
      self._full_text1_label.render(title_rect)

      bottom_offset = 361 if is_long else 420
      subtitle_rect = rl.Rectangle(rect.x, rect.y + rect.height - bottom_offset, rect.width, 300)
      self._full_text2_label.set_text(alert.text2)
      self._full_text2_label.render(subtitle_rect)

  def _draw_centered(self, text, rect, font, font_size, center_y=True, color=rl.WHITE) -> None:
    text_size = measure_text_cached(font, text, font_size)
    x = rect.x + (rect.width - text_size.x) / 2
    y = rect.y + ((rect.height - text_size.y) / 2 if center_y else 0)
    rl.draw_text_ex(font, text, rl.Vector2(x, y), font_size, 0, color)

  def _debounce_alert(self, alert: Alert | None) -> Alert | None:
    now = time.monotonic()
    if alert and alert.status == AlertStatus.critical:
      self._last_alert = alert
      self._last_alert_time = now
      self._pending_alert = None
      return alert

    if alert and alert.text1 == ALERT_STARTUP_PENDING.text1 and alert.text2 == ALERT_STARTUP_PENDING.text2:
      if (now - ui_state.started_time) < 3.0:
        return None
      # Keep the startup pending alert stable to avoid entry flicker.
      if self._last_alert != alert:
        if self._pending_alert != alert:
          self._pending_alert = alert
          self._pending_alert_time = now
          return self._last_alert
        if (now - self._pending_alert_time) < 1.0:
          return self._last_alert
        self._pending_alert = None
      if self._startup_alert_until <= now:
        self._startup_alert_until = now + 2.0
      if self._startup_latch_until <= now:
        self._startup_latch_until = now + 12.0
      self._last_alert = alert
      self._last_alert_time = now
      return alert

    if alert is None:
      if self._startup_latch_until > now and self._last_alert == ALERT_STARTUP_PENDING:
        return self._last_alert
      if self._startup_alert_until > now:
        return self._last_alert
      if self._last_alert and (now - self._last_alert_time) < 1.0:
        return self._last_alert
      self._last_alert = None
      self._pending_alert = None
      return None

    if self._last_alert and alert == self._last_alert:
      self._last_alert_time = now
      self._pending_alert = None
      return alert

    if self._pending_alert != alert:
      self._pending_alert = alert
      self._pending_alert_time = now
      return self._last_alert

    if (now - self._pending_alert_time) >= 0.2:
      self._last_alert = alert
      self._last_alert_time = now
      self._pending_alert = None
      return alert

    return self._last_alert
