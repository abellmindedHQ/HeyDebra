from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QGraphicsOpacityEffect, QGraphicsDropShadowEffect
from PyQt6.QtGui import QMovie, QColor, QPainterPath, QRegion, QPixmap
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QRect, QEasingCurve, QParallelAnimationGroup

class DebraGUI(QWidget):
    def __init__(self):
        super().__init__()

        # 💅 Frameless + Always-on-top + Transparent window
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(480, 480)

        # 💡 Rounded mask
        radius = 32
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), radius, radius)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

        # 🧱 Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # 🖼️ Label for GIF
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            background-color: rgba(0, 0, 0, 200);
        """)
        layout.addWidget(self.label)

        # ✖️ Close Button
        self.close_btn = QPushButton("✕", self)
        self.close_btn.setFixedSize(32, 32)
        self.close_btn.move(self.width() - 42, 10)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(0,0,0,120);
                color: white;
                border: 2px solid #FF00CC;
                border-radius: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 204, 120);
            }
        """)
        self.close_btn.clicked.connect(self.close)
        self.close_btn.raise_()

        # ✨ Glow
        glow = QGraphicsDropShadowEffect(self)
        glow.setBlurRadius(50)
        glow.setColor(QColor("#FF00CC"))
        glow.setOffset(0)
        self.label.setGraphicsEffect(glow)

        # 🎞️ Load GIFs
        self.idle_gif = QMovie("assets/debra_idle.gif")
        self.idle_gif.setScaledSize(QSize(480, 480))
        self.idle_gif.setCacheMode(QMovie.CacheMode.CacheAll)
        self.idle_gif.setSpeed(100)

        self.talking_gif = QMovie("assets/debra_talking.gif")
        self.talking_gif.setScaledSize(QSize(480, 480))
        self.talking_gif.setCacheMode(QMovie.CacheMode.CacheAll)
        self.talking_gif.setSpeed(100)

        self.label.setMovie(self.idle_gif)
        self.idle_gif.start()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self._drag_pos)
            self._drag_pos = event.globalPosition().toPoint()

    def set_idle(self):
        self.label.setMovie(self.idle_gif)
        self.idle_gif.start()

    def set_talking(self):
        self.label.setMovie(self.talking_gif)
        self.talking_gif.start()

    def update_text(self, text: str, animated: bool = False):
        print(f"[GUI] {text}")
        if animated:
            self.set_talking()
        else:
            self.set_idle()

    def closeEvent(self, event):
        print("[DEBUG] GUI closed — shutting down.")
        import sys
        sys.exit()

    def animate_entrance(self):
        opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(opacity_effect)

        opacity_anim = QPropertyAnimation(opacity_effect, b"opacity")
        opacity_anim.setStartValue(0.0)
        opacity_anim.setEndValue(1.0)
        opacity_anim.setDuration(1000)

        start_rect = QRect(self.x() + self.width() // 2, self.y() + self.height() // 2, 1, 1)
        end_rect = QRect(self.x(), self.y(), self.width(), self.height())

        geo_anim = QPropertyAnimation(self, b"geometry")
        geo_anim.setStartValue(start_rect)
        geo_anim.setEndValue(end_rect)
        geo_anim.setDuration(1000)
        geo_anim.setEasingCurve(QEasingCurve.Type.OutBack)

        self.anim_group = QParallelAnimationGroup()
        self.anim_group.addAnimation(opacity_anim)
        self.anim_group.addAnimation(geo_anim)
        self.anim_group.start()