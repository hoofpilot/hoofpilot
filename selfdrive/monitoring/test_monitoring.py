import pytest

from cereal import car, log
from openpilot.common.realtime import DT_DMON
from openpilot.selfdrive.monitoring.helpers import DriverMonitoring, DRIVER_MONITOR_SETTINGS
from openpilot.system.hardware import HARDWARE

EventName = log.OnroadEvent.EventName
dm_settings = DRIVER_MONITOR_SETTINGS(device_type=HARDWARE.get_device_type())

TEST_TIMESPAN = 120
DISTRACTED_SECONDS_TO_ORANGE = dm_settings._DISTRACTED_TIME - dm_settings._DISTRACTED_PROMPT_TIME_TILL_TERMINAL + 1
DISTRACTED_SECONDS_TO_RED = dm_settings._DISTRACTED_TIME + 1
INVISIBLE_SECONDS_TO_ORANGE = dm_settings._AWARENESS_TIME - dm_settings._AWARENESS_PROMPT_TIME_TILL_TERMINAL + 1
INVISIBLE_SECONDS_TO_RED = dm_settings._AWARENESS_TIME + 1


def make_msg(face_detected, distracted=False, model_uncertain=False):
  ds = log.DriverStateV2.new_message()
  ds.leftDriverData.faceOrientation = [0., 0., 0.]
  ds.leftDriverData.facePosition = [0., 0.]
  ds.leftDriverData.faceProb = 1. * face_detected
  ds.leftDriverData.eyesVisibleProb = 1.
  ds.leftDriverData.eyesClosedProb = 1. * distracted
  ds.leftDriverData.faceOrientationStd = [1. * model_uncertain, 1. * model_uncertain, 1. * model_uncertain]
  ds.leftDriverData.facePositionStd = [1. * model_uncertain, 1. * model_uncertain]
  ds.leftDriverData.phoneProb = 0.
  return ds


msg_NO_FACE_DETECTED = make_msg(False)
msg_ATTENTIVE = make_msg(True)
msg_DISTRACTED = make_msg(True, distracted=True)
msg_ATTENTIVE_UNCERTAIN = make_msg(True, model_uncertain=True)
msg_DISTRACTED_UNCERTAIN = make_msg(True, distracted=True, model_uncertain=True)
msg_DISTRACTED_BUT_SOMEHOW_UNCERTAIN = make_msg(True, distracted=True, model_uncertain=dm_settings._POSESTD_THRESHOLD * 1.5)

car_interaction_DETECTED = True
car_interaction_NOT_DETECTED = False

always_no_face = [msg_NO_FACE_DETECTED] * int(TEST_TIMESPAN / DT_DMON)
always_attentive = [msg_ATTENTIVE] * int(TEST_TIMESPAN / DT_DMON)
always_distracted = [msg_DISTRACTED] * int(TEST_TIMESPAN / DT_DMON)
always_true = [True] * int(TEST_TIMESPAN / DT_DMON)
always_false = [False] * int(TEST_TIMESPAN / DT_DMON)


class TestMonitoring:
  def _run_seq(self, msgs, interaction, engaged, standstill):
    DM = DriverMonitoring()
    events = []
    for idx in range(len(msgs)):
      DM._update_states(msgs[idx], [0, 0, 0], 0, engaged[idx], standstill[idx])
      DM._update_events(interaction[idx], engaged[idx], standstill[idx], 0, 0)
      events.append(DM.current_events)
    assert len(events) == len(msgs), f"got {len(events)} for {len(msgs)} driverState input msgs"
    return events, DM

  def _assert_no_events(self, events):
    assert all(not len(e) for e in events)

  def test_fully_aware_driver(self):
    events, _ = self._run_seq(always_attentive, always_false, always_true, always_false)
    self._assert_no_events(events)

  def test_fully_distracted_driver(self):
    events, d_status = self._run_seq(always_distracted, always_false, always_true, always_false)
    assert len(events[int((d_status.settings._DISTRACTED_TIME - d_status.settings._DISTRACTED_PRE_TIME_TILL_TERMINAL) / 2 / DT_DMON)]) == 0
    idx1 = int((d_status.settings._DISTRACTED_TIME - d_status.settings._DISTRACTED_PRE_TIME_TILL_TERMINAL +
                ((d_status.settings._DISTRACTED_PRE_TIME_TILL_TERMINAL - d_status.settings._DISTRACTED_PROMPT_TIME_TILL_TERMINAL) / 2)) / DT_DMON)
    assert events[idx1].names[0] == EventName.driverDistracted1
    assert events[int((d_status.settings._DISTRACTED_TIME - d_status.settings._DISTRACTED_PROMPT_TIME_TILL_TERMINAL +
                    ((d_status.settings._DISTRACTED_PROMPT_TIME_TILL_TERMINAL) / 2)) / DT_DMON)].names[0] == EventName.driverDistracted2
    assert events[int((d_status.settings._DISTRACTED_TIME +
                    ((TEST_TIMESPAN - 10 - d_status.settings._DISTRACTED_TIME) / 2)) / DT_DMON)].names[0] == EventName.driverDistracted3
    assert isinstance(d_status.awareness, float)

  def test_fully_invisible_driver(self):
    events, d_status = self._run_seq(always_no_face, always_false, always_true, always_false)
    assert len(events[int((d_status.settings._AWARENESS_TIME - d_status.settings._AWARENESS_PRE_TIME_TILL_TERMINAL) / 2 / DT_DMON)]) == 0
    idx1 = int((d_status.settings._AWARENESS_TIME - d_status.settings._AWARENESS_PRE_TIME_TILL_TERMINAL +
               ((d_status.settings._AWARENESS_PRE_TIME_TILL_TERMINAL - d_status.settings._AWARENESS_PROMPT_TIME_TILL_TERMINAL) / 2)) / DT_DMON)
    assert events[idx1].names[0] == EventName.driverUnresponsive1
    assert events[int((d_status.settings._AWARENESS_TIME - d_status.settings._AWARENESS_PROMPT_TIME_TILL_TERMINAL +
                      ((d_status.settings._AWARENESS_PROMPT_TIME_TILL_TERMINAL) / 2)) / DT_DMON)].names[0] == EventName.driverUnresponsive2
    assert events[int((d_status.settings._AWARENESS_TIME +
                      ((TEST_TIMESPAN - 10 - d_status.settings._AWARENESS_TIME) / 2)) / DT_DMON)].names[0] == EventName.driverUnresponsive3


def _build_sm(selfdrive_enabled, lat_active, steering_pressed, gas_pressed):
  cs = car.CarState.new_message()
  cs.vEgo = 30.0
  cs.gearShifter = car.CarState.GearShifter.drive
  cs.steeringPressed = steering_pressed
  cs.gasPressed = gas_pressed
  ss = log.SelfdriveState.new_message()
  ss.enabled = selfdrive_enabled
  cc = car.CarControl.new_message()
  cc.latActive = lat_active
  mv2 = log.ModelDataV2.new_message()
  mv2.meta.disengagePredictions.brakeDisengageProbs = [0.0]
  lc = log.LiveCalibrationData.new_message()
  lc.rpyCalib = [0.0, 0.0, 0.0]
  return {
    'carState': cs, 'selfdriveState': ss, 'carControl': cc,
    'modelV2': mv2, 'liveCalibration': lc, 'driverStateV2': make_msg(False),
  }


@pytest.mark.parametrize("selfdrive_enabled, lat_active, steering, gas, expected_op_engaged, expected_driver_engaged", [
  (False, False, False, False, False, False),
  (True, False, False, False, True, False),
  (False, True, False, False, True, False),
  (True, True, False, False, True, False),
  (False, True, False, True, True, False),
  (True, True, False, True, True, True),
  (False, True, True, False, True, True),
])
def test_run_step_engagement(selfdrive_enabled, lat_active, steering, gas,
                             expected_op_engaged, expected_driver_engaged):
  sm = _build_sm(selfdrive_enabled, lat_active, steering, gas)
  dm = DriverMonitoring()
  captured = {}
  orig = dm._update_events

  def spy(driver_engaged, op_engaged, standstill, wrong_gear, car_speed):
    captured['driver_engaged'] = driver_engaged
    captured['op_engaged'] = op_engaged
    return orig(driver_engaged, op_engaged, standstill, wrong_gear, car_speed)

  dm._update_events = spy
  dm.run_step(sm, demo=False)
  assert captured['op_engaged'] == expected_op_engaged
  assert captured['driver_engaged'] == expected_driver_engaged
