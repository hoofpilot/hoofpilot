#pragma once

#include <QWidget>
#include <QVBoxLayout>
#include <QTimer>
#include "selfdrive/ui/qt/widgets/driving_mode_button.h"
#include "selfdrive/ui/qt/widgets/driving_mode_info_dialog.h"
#include <QStackedLayout>
#include <QFrame>

class DrivingModePanel : public QWidget {
  Q_OBJECT

signals:
  void drivingModeChanged();
  void modeSelected(DrivingMode mode);

public:
  DrivingModePanel(QWidget* parent = nullptr);

private slots:
  void updateButtons();
  void checkParamsAndUpdate();
  void onDrivingModeButtonDoubleClicked(DrivingMode mode);

public:
  bool eventFilter(QObject *obj, QEvent *event) override;

private:
  DrivingModeButton* stockADASButton;
  DrivingModeButton* chillButton;
  DrivingModeButton* experimentalButton;
  DrivingModeInfoDialog* infoDialog;
  Params params;
  QTimer* updateTimer;
  QVBoxLayout* mainLayout;
  QWidget* buttonWidget;
  QStackedLayout* stackedLayout;

  void onInfoDialogAccepted();
  void onInfoDialogRejected();
};
