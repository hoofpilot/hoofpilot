#include "selfdrive/ui/qt/widgets/driving_mode_helpers.h"
#include "selfdrive/ui/qt/offroad/driving_mode_panel.h"

DrivingMode getCurrentDrivingMode(Params& params) {
  bool openpilotEnabled = params.getBool("OpenpilotEnabledToggle");
  bool experimentalMode = params.getBool("ExperimentalMode");

  if (!openpilotEnabled) return DrivingMode::StockADAS;
  return experimentalMode ? DrivingMode::Experimental : DrivingMode::Chill;
}

void setDrivingMode(Params& params, DrivingMode mode, QObject* panel) {
  DrivingMode currentMode = getCurrentDrivingMode(params);
  if (currentMode != mode) {
    switch (mode) {
      case DrivingMode::StockADAS:
        params.putBool("OpenpilotEnabledToggle", false);
        params.putBool("ExperimentalMode", false);
        break;
      case DrivingMode::Chill:
        params.putBool("OpenpilotEnabledToggle", true);
        params.putBool("ExperimentalMode", false);
        break;
      case DrivingMode::Experimental:
        params.putBool("OpenpilotEnabledToggle", true);
        params.putBool("ExperimentalMode", true);
        break;
    }
    if (panel) {
      QMetaObject::invokeMethod(panel, "drivingModeChanged", Qt::QueuedConnection);
    }
  }
}

bool hasDrivingModeChanged(Params& params) {
  bool lastOpenpilotEnabled = params.getBool("LastOpenpilotEnabledToggle");
  bool lastExperimentalMode = params.getBool("LastExperimentalMode");

  bool currentOpenpilotEnabled = params.getBool("OpenpilotEnabledToggle");
  bool currentExperimentalMode = params.getBool("ExperimentalMode");

  if (currentOpenpilotEnabled != lastOpenpilotEnabled || currentExperimentalMode != lastExperimentalMode) {
    params.putBool("LastOpenpilotEnabledToggle", currentOpenpilotEnabled);
    params.putBool("LastExperimentalMode", currentExperimentalMode);
    return true;
  }
  return false;
}
