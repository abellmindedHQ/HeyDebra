from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton
import sys

class DebraApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HeyDebra")
        self.setStyleSheet("background-color: #1e1e1e; color: #00ffff;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.face_label = QLabel("Floating Debra Face Placeholder")
        self.chat_log = QLabel("Chat log will appear here...")
        self.mic_button = QPushButton("Mic: ON")
        self.wake_button = QPushButton("Wake Word: Enabled")

        layout.addWidget(self.face_label)
        layout.addWidget(self.chat_log)
        layout.addWidget(self.mic_button)
        layout.addWidget(self.wake_button)
        self.setLayout(layout)

def main():
    app = QApplication(sys.argv)
    window = DebraApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
