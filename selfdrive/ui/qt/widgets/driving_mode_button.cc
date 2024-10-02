#include "selfdrive/ui/qt/widgets/driving_mode_button.h"
#include "selfdrive/ui/qt/widgets/driving_mode_helpers.h"
#include "selfdrive/ui/qt/util.h"

#include <QVBoxLayout>
#include <QLabel>
#include <QHBoxLayout>
#include <QPainter>

DrivingModeButton::DrivingModeButton(const QString &text, DrivingMode mode, Params &params, QWidget *parent)
    : QPushButton(parent), mode(mode), params(params) {
  setFixedHeight(230);
  setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Fixed);

  setContentsMargins(10, 10, 50, 10); // 50px right padding for statusCircle

  QHBoxLayout *mainLayout = new QHBoxLayout(this);
  mainLayout->setContentsMargins(0, 0, 0, 0);

  QVBoxLayout *textLayout = new QVBoxLayout();
  textLayout->setAlignment(Qt::AlignLeft | Qt::AlignVCenter);

  QLabel *textLabel = new QLabel(text, this);
  textLabel->setAlignment(Qt::AlignLeft | Qt::AlignTop);
  textLayout->addWidget(textLabel);

  textLayout->addStretch();

  mainLayout->addLayout(textLayout);
  mainLayout->addStretch();

  statusCircle = new QWidget(this);
  statusCircle->setFixedSize(76, 76);
  mainLayout->addWidget(statusCircle, 0, Qt::AlignVCenter);

  setLayout(mainLayout);

  connect(this, &QPushButton::clicked, this, &DrivingModeButton::onClicked);
  updateState();
}

void DrivingModeButton::updateState() {
  isCurrentMode = (getCurrentDrivingMode(params) == mode);
  setEnabled(!isCurrentMode);

  const double disabledButtonOpacity = 0.3;
  QString textColor = isCurrentMode ? "white" : "#555555";

  struct GradientColors {
    QColor start;
    QColor end;
  };

  const std::map<DrivingMode, GradientColors> gradients = {
    {DrivingMode::Chill, {QColor("#00c88c"), QColor("#0077be")}},
    {DrivingMode::Experimental, {QColor("#ff8c2f"), QColor("#c62a1d")}},
    {DrivingMode::StockADAS, {QColor("#1f1c18"), QColor("#6e7e8b")}}
  };

  auto colors = gradients.at(mode);

  if (!isCurrentMode) {
    colors.start.setAlphaF(disabledButtonOpacity);
    colors.end.setAlphaF(disabledButtonOpacity);
  }

  QString backgroundColor = QString("qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, "
                                    "stop:0 %1, stop:1 %2)")
                                    .arg(colors.start.name(QColor::HexArgb),
                                         colors.end.name(QColor::HexArgb));

  QString styleSheet = QString(R"(
    QPushButton {
      border-radius: 25px;
      background: %1;
      padding: 0px;
    }
    QLabel {
      font-size: 70px;
      font-weight: 700;
      color: %2;
      background-color: rgba(0, 0, 0, 0);
      border-radius: 5px;
      padding: 5px;
    }
  )").arg(backgroundColor, textColor);

  setStyleSheet(styleSheet);
  update();
}

void DrivingModeButton::paintEvent(QPaintEvent *event) {
  QPushButton::paintEvent(event);
  drawStatusCircle();
}

void DrivingModeButton::drawStatusCircle() {
  QPainter painter(this);
  painter.setRenderHint(QPainter::Antialiasing);

  QRect circleRect = statusCircle->geometry();
  painter.setPen(QPen(Qt::black, 20));
  painter.setBrush(isCurrentMode ? QColor("#00FF00") : Qt::transparent);
  painter.drawEllipse(circleRect);
}

void DrivingModeButton::onClicked() {
  setDrivingMode(params, mode);
  updateState();
  emit drivingModeChanged();
}
