#pragma once

#include <QWidget>
#include <QLabel>
#include <QPushButton>
#include <QVBoxLayout>
#include "selfdrive/ui/qt/widgets/driving_mode_helpers.h"

class DrivingModeInfoDialog : public QWidget {
  Q_OBJECT

public:
  explicit DrivingModeInfoDialog(DrivingMode mode, QWidget *parent = nullptr);

signals:
  void accepted();
  void rejected();

public slots:
  void show(DrivingMode mode);

private:
  QLabel *iconLabel;
  QLabel *titleLabel;
  QLabel *contentLabel;
  QPushButton *cancelButton;
  QPushButton *enableButton;

  void setupUI();
  void setModeInfo(DrivingMode mode);
};
