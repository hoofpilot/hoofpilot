#include "driving_mode_info_dialog.h"
#include <QGuiApplication>
#include <QScreen>
#include "selfdrive/ui/qt/widgets/scrollview.h"

DrivingModeInfoDialog::DrivingModeInfoDialog(DrivingMode mode, QWidget *parent)
    : QWidget(parent) {
  setupUI();
  setModeInfo(mode);
  hide(); // Initially hidden

  setStyleSheet(R"(
    DrivingModeInfoDialog {
      background-color: #333333;
      border-radius: 25px;
    }
    QLabel { color: white; }
    #iconLabel { qproperty-alignment: AlignCenter; }
    #titleLabel { font-size: 57px; font-weight: bold; }
    #contentLabel { font-size: 40px; }
    QPushButton {
      font-size: 45px;
      padding: 45px 25px;
      border-radius: 10px;
    }
    #cancelButton {
      background-color: #444444;
      color: white;
    }
    #enableButton {
      background-color: #4CAF50;
      color: white;
    }
  )");

  setAttribute(Qt::WA_StyledBackground, true);
}

void DrivingModeInfoDialog::show(DrivingMode mode) {
  setModeInfo(mode);
  QWidget::show();
}

void DrivingModeInfoDialog::setupUI() {
  QVBoxLayout *mainLayout = new QVBoxLayout(this);
  mainLayout->setContentsMargins(50, 50, 50, 50);
  mainLayout->setSpacing(30);

  QHBoxLayout *headerLayout = new QHBoxLayout();
  headerLayout->setSpacing(20);  // Controls spacing between icon and title

  iconLabel = new QLabel(this);
  iconLabel->setObjectName("iconLabel");
  iconLabel->setFixedSize(100, 100);
  headerLayout->addWidget(iconLabel);

  titleLabel = new QLabel(this);
  titleLabel->setObjectName("titleLabel");
  headerLayout->addWidget(titleLabel);

  headerLayout->addStretch();  // Push icon and title to the left
  mainLayout->addLayout(headerLayout);

  QWidget *scrollContent = new QWidget(this);
  QVBoxLayout *scrollLayout = new QVBoxLayout(scrollContent);
  scrollLayout->setSpacing(20);

  contentLabel = new QLabel(scrollContent);
  contentLabel->setObjectName("contentLabel");
  contentLabel->setWordWrap(true);
  scrollLayout->addWidget(contentLabel);
  scrollLayout->addStretch(1);

  ScrollView *scrollView = new ScrollView(scrollContent, this);
  scrollView->setWidgetResizable(true);
  scrollView->setVerticalScrollBarPolicy(Qt::ScrollBarAsNeeded);
  scrollView->setHorizontalScrollBarPolicy(Qt::ScrollBarAlwaysOff);
  mainLayout->addWidget(scrollView, 1);

  QHBoxLayout *buttonLayout = new QHBoxLayout();
  cancelButton = new QPushButton(tr("Cancel"), this);
  cancelButton->setObjectName("cancelButton");
  enableButton = new QPushButton(tr("Enable"), this);
  enableButton->setObjectName("enableButton");

  buttonLayout->addWidget(cancelButton);
  buttonLayout->addWidget(enableButton);

  mainLayout->addLayout(buttonLayout);

  connect(cancelButton, &QPushButton::clicked, this, &DrivingModeInfoDialog::rejected);
  connect(enableButton, &QPushButton::clicked, this, &DrivingModeInfoDialog::accepted);
}

void DrivingModeInfoDialog::setModeInfo(DrivingMode mode) {
  switch (mode) {
    case DrivingMode::Chill:
      iconLabel->setPixmap(QPixmap("../assets/img_chffr_wheel.png").scaled(100, 100, Qt::KeepAspectRatio, Qt::SmoothTransformation));
      titleLabel->setText(tr("Chill Mode"));
      contentLabel->setText(tr("This is the default mode. It's safe and reliable for everyday driving. "
                               "The system will be more conservative in its actions, prioritizing a smooth and comfortable ride."));
      break;
    case DrivingMode::Experimental:
      iconLabel->setPixmap(QPixmap("../assets/img_experimental.svg").scaled(100, 100, Qt::KeepAspectRatio, Qt::SmoothTransformation));
      titleLabel->setText(tr("Experimental Mode"));
      contentLabel->setText(tr("openpilot defaults to driving in chill mode. Experimental mode enables alpha-level features that aren't ready for chill mode. Experimental features are listed below:\n\n"
                               "End-to-End Longitudinal Control\n\n"
                               "Let the driving model control the gas and brakes. openpilot will drive as it thinks a human would, including stopping for red lights and stop signs. Since the driving model decides the speed to drive, the set speed will only act as an upper bound. This is an alpha quality feature; mistakes should be expected.\n\n"
                               "New Driving Visualization\n\n"
                               "The driving visualization will transition to the road-facing wide-angle camera at low speeds to better show some turns. The Experimental mode logo will also be shown in the top right corner."));
      break;
    case DrivingMode::StockADAS:
      iconLabel->setPixmap(QPixmap());
      titleLabel->setText(tr("Stock ADAS Mode"));
      contentLabel->setText(tr("This mode uses the stock ADAS features of your vehicle. It provides a familiar driving experience "
                               "with the safety features you're accustomed to."));
      break;
  }
}
