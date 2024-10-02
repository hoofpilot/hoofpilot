#pragma once

#include <QWidget>
#include <QLabel>
#include <QHBoxLayout>
#include <QTimer>
#include "selfdrive/ui/qt/widgets/driving_mode_helpers.h"

class InfoDisplayBar : public QWidget {
  Q_OBJECT

public:
  explicit InfoDisplayBar(QWidget *parent = nullptr);

public slots:
  void showModeMessage(DrivingMode mode);

private:
  const QString DEFAULT_MESSAGE = "Tap mode for more info";
  QLabel *messageLabel;
  QLabel *iconLabel;
  QTimer *resetTimer;

  void resetToDefaultMessage();
};
