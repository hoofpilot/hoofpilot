#include "selfdrive/ui/qt/offroad/info_display_bar.h"

InfoDisplayBar::InfoDisplayBar(QWidget *parent) : QWidget(parent) {
  QHBoxLayout *layout = new QHBoxLayout(this);
  layout->setContentsMargins(30, 35, 55, 35);
  layout->setSpacing(10);

  messageLabel = new QLabel(this);
  messageLabel->setAlignment(Qt::AlignLeft | Qt::AlignVCenter);
  messageLabel->setWordWrap(true);
  layout->addWidget(messageLabel, 1);

  iconLabel = new QLabel(this);
  iconLabel->setAlignment(Qt::AlignRight | Qt::AlignVCenter);
  iconLabel->setFixedSize(65, 65);
  layout->addWidget(iconLabel);

  setStyleSheet(R"(
    InfoDisplayBar {
      background-color: #000000;
      border: 4px solid #F5F5F5;
      border-radius: 25px;
    }
    QLabel {
      font-size: 45px;
      color: white;
      background-color: transparent;
    }
  )");

  setAutoFillBackground(true);
  setAttribute(Qt::WA_StyledBackground, true);

  resetTimer = new QTimer(this);
  resetTimer->setSingleShot(true);
  connect(resetTimer, &QTimer::timeout, this, &InfoDisplayBar::resetToDefaultMessage);

  resetToDefaultMessage();
}

void InfoDisplayBar::showModeMessage(DrivingMode mode) {
  QString message;
  QString iconPath;
  switch (mode) {
    case DrivingMode::StockADAS:
      message = "Stock ADAS mode enabled";
      iconPath = "../assets/img_stock_adas.png";
      break;
    case DrivingMode::Chill:
      message = "chill mode enabled";
      iconPath = "../assets/img_chffr_wheel.png";
      break;
    case DrivingMode::Experimental:
      message = "Experimental mode enabled";
      iconPath = "../assets/img_experimental.svg";
      break;
  }
  messageLabel->setText(message);
  iconLabel->setPixmap(QPixmap(iconPath).scaled(65, 65, Qt::KeepAspectRatio, Qt::SmoothTransformation));
  resetTimer->start(3000);
}

void InfoDisplayBar::resetToDefaultMessage() {
  messageLabel->setText(DEFAULT_MESSAGE);
  iconLabel->clear();
}
