#include "selfdrive/ui/qt/widgets/wifi.h"

#include <QHBoxLayout>
#include <QLabel>
#include <QPixmap>
#include <QPushButton>

WiFiPromptWidget::WiFiPromptWidget(QWidget *parent) : QFrame(parent) {
  setStyleSheet("background-color: #333333; border-radius: 25px;");

  stack = new QStackedLayout(this);

  // Setup Wi-Fi
  QWidget *setup = new QWidget;
  QVBoxLayout *setup_layout = new QVBoxLayout(setup);
  setup_layout->setContentsMargins(56, 60, 56, 40);
  setup_layout->setSpacing(45);

  QLabel *setup_icon = new QLabel;
  setup_icon->setPixmap(QPixmap("../assets/offroad/icon_wifi_setup.svg").scaledToWidth(225, Qt::SmoothTransformation));
  setup_icon->setAlignment(Qt::AlignCenter);

  QLabel *setup_desc = new QLabel(tr("Connect to Wi-Fi to upload driving data and help improve openpilot"));
  setup_desc->setStyleSheet("font-size: 40px; font-weight: 400; padding: 0 50px;");
  setup_desc->setWordWrap(true);
  setup_desc->setAlignment(Qt::AlignCenter);

  QPushButton *settings_btn = new QPushButton(tr("Setup Wi-Fi"));
  settings_btn->setStyleSheet(R"(
    QPushButton {
      font-size: 48px;
      font-weight: 500;
      border-radius: 20px;
      background-color: #465BEA;
      padding: 32px;
    }
    QPushButton:pressed {
      background-color: #3049F4;
    }
  )");
  connect(settings_btn, &QPushButton::clicked, [=]() { emit openSettings(1); });

  setup_layout->addWidget(setup_icon);
  setup_layout->addStretch();
  setup_layout->addWidget(setup_desc);
  setup_layout->addStretch();
  setup_layout->addWidget(settings_btn);

  stack->addWidget(setup);

  // Uploading data
  QWidget *uploading = new QWidget;
  QVBoxLayout *uploading_layout = new QVBoxLayout(uploading);
  uploading_layout->setContentsMargins(50, 60, 50, 60);
  uploading_layout->setSpacing(0); // Without this WiFi and Connected labels spacing too far apart

  QLabel *uploading_icon = new QLabel;
  uploading_icon->setPixmap(QPixmap("../assets/offroad/icon_wifi_uploading.svg").scaledToWidth(200, Qt::SmoothTransformation));
  uploading_icon->setAlignment(Qt::AlignCenter);

  QLabel *top_label = new QLabel(tr("Wi-Fi"));
  top_label->setStyleSheet("font-size: 58px; font-weight: 400;");
  top_label->setAlignment(Qt::AlignCenter);

  QLabel *bottom_label = new QLabel(tr("Connected"));
  bottom_label->setStyleSheet("font-size: 77px; font-weight: 600; color: #AAED70;");
  bottom_label->setAlignment(Qt::AlignCenter);

  QLabel *uploading_desc = new QLabel(tr("Training data will be pulled periodically while your device is on Wi-Fi"));
  uploading_desc->setStyleSheet("font-size: 42px; font-weight: 400;");
  uploading_desc->setWordWrap(true);
  uploading_desc->setAlignment(Qt::AlignCenter);

  uploading_layout->addWidget(uploading_icon);
  uploading_layout->addStretch();
  uploading_layout->addWidget(top_label);
  uploading_layout->addWidget(bottom_label);
  uploading_layout->addStretch();
  uploading_layout->addWidget(uploading_desc);

  stack->addWidget(uploading);

  QObject::connect(uiState(), &UIState::uiUpdate, this, &WiFiPromptWidget::updateState);
}

void WiFiPromptWidget::updateState(const UIState &s) {
  if (!isVisible()) return;

  auto &sm = *(s.sm);

  auto network_type = sm["deviceState"].getDeviceState().getNetworkType();
  auto uploading = network_type == cereal::DeviceState::NetworkType::WIFI ||
      network_type == cereal::DeviceState::NetworkType::ETHERNET;
  stack->setCurrentIndex(uploading ? 1 : 0);
}