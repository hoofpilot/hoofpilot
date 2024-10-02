#include "selfdrive/ui/qt/offroad/driving_mode_panel.h"
#include "selfdrive/ui/qt/widgets/driving_mode_helpers.h"
#include "selfdrive/ui/qt/widgets/driving_mode_info_dialog.h"
#include "common/params.h"
#include <QEvent>

DrivingModePanel::DrivingModePanel(QWidget* parent) : QWidget(parent) {
  setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);
  mainLayout = new QVBoxLayout(this);
  mainLayout->setContentsMargins(0, 0, 0, 0);

  buttonWidget = new QWidget(this);
  QVBoxLayout* buttonLayout = new QVBoxLayout(buttonWidget);
  buttonLayout->setContentsMargins(0, 0, 0, 0);
  buttonLayout->setSpacing(20);

  auto addDrivingModeButton = [&](const QString &text, DrivingMode mode) {
    DrivingModeButton *button = new DrivingModeButton(text, mode, params, this);
    buttonLayout->addWidget(button);
    connect(button, &DrivingModeButton::clicked, [=]() {
      emit modeSelected(mode);
    });
    connect(button, &DrivingModeButton::drivingModeChanged, this, &DrivingModePanel::updateButtons);
    button->installEventFilter(this);
    return button;
  };

  chillButton = addDrivingModeButton("chill mode", DrivingMode::Chill);
  experimentalButton = addDrivingModeButton("Experimental Mode", DrivingMode::Experimental);
  stockADASButton = addDrivingModeButton("Stock ADAS Mode", DrivingMode::StockADAS);

  infoDialog = new DrivingModeInfoDialog(DrivingMode::Chill, this);
  connect(infoDialog, &DrivingModeInfoDialog::accepted, this, &DrivingModePanel::onInfoDialogAccepted);
  connect(infoDialog, &DrivingModeInfoDialog::rejected, this, &DrivingModePanel::onInfoDialogRejected);

  stackedLayout = new QStackedLayout();
  stackedLayout->addWidget(buttonWidget);
  stackedLayout->addWidget(infoDialog);

  mainLayout->addLayout(stackedLayout);

  connect(this, &DrivingModePanel::drivingModeChanged, this, &DrivingModePanel::updateButtons);

  if (!params.getBool("OpenpilotEnabledToggle") && !params.getBool("ExperimentalMode")) {
    setDrivingMode(params, DrivingMode::Chill, this);
  }

  updateButtons();

  // Timer to periodically check for parameter changes
  updateTimer = new QTimer(this);
  connect(updateTimer, &QTimer::timeout, this, &DrivingModePanel::checkParamsAndUpdate);
  updateTimer->start(1000);
}

bool DrivingModePanel::eventFilter(QObject *obj, QEvent *event) {
  if (event->type() == QEvent::MouseButtonDblClick) {
    DrivingModeButton *button = qobject_cast<DrivingModeButton*>(obj);
    if (button) {
      onDrivingModeButtonDoubleClicked(button->getMode());
      return true;
    }
  }
  return QWidget::eventFilter(obj, event);
}

void DrivingModePanel::onDrivingModeButtonDoubleClicked(DrivingMode mode) {
  infoDialog->show(mode);
  stackedLayout->setCurrentWidget(infoDialog);
}

void DrivingModePanel::updateButtons() {
  chillButton->updateState();
  experimentalButton->updateState();
  stockADASButton->updateState();
}

void DrivingModePanel::checkParamsAndUpdate() {
  if (hasDrivingModeChanged(params)) {
    updateButtons();
  }
}

void DrivingModePanel::onInfoDialogAccepted() {
  DrivingMode mode = getCurrentDrivingMode(params);
  setDrivingMode(params, mode, this);
  emit modeSelected(mode);
  updateButtons();
  stackedLayout->setCurrentWidget(buttonWidget);
}

void DrivingModePanel::onInfoDialogRejected() {
  stackedLayout->setCurrentWidget(buttonWidget);
}
