# OpenAI GPT 3.5 16K - Via LibreChat (API Integration)

Here's an example implementation of a Python GUI application for speech-to-text using the OpenAI Whisper API on OpenSUSE Linux. This implementation uses the PyQt library for the GUI, PyAudio for audio input handling, requests for API integration, and keyring for securely storing the API key.

Note: This example implementation focuses on the GUI setup and basic functionality. Additional code for audio handling, API integration, and keyboard shortcuts may be required. 

```python
import sys
import os
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QSystemTrayIcon, QMenu, QAction, QComboBox, QVBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import pyaudio
import wave
import keyring

# Whisper API endpoint
API_ENDPOINT = "https://api.openai.com/v1/engines/whisper-beta/completions"

class SpeechToTextApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Set up the main GUI window
        self.setWindowTitle("Speech-to-Text")
        self.setGeometry(100, 100, 300, 200)
        
        # API key configuration
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter API Key")
        self.api_key_input.setText(keyring.get_password("speech_to_text_app", "api_key"))
        
        save_api_key_button = QPushButton("Save API Key")
        save_api_key_button.clicked.connect(self.save_api_key)
        
        # Microphone selection
        self.microphone_combo = QComboBox()
        self.microphone_combo.addItems(self.get_microphone_list())
        
        start_button = QPushButton("Start")
        start_button.clicked.connect(self.start_dictation)
        
        stop_button = QPushButton("Stop")
        stop_button.clicked.connect(self.stop_dictation)
        
        # System tray integration
        self.tray_icon = QSystemTrayIcon(QIcon("icon.png"), self)
        self.tray_icon.setToolTip("Speech-to-Text")
        self.tray_icon.activated.connect(self.show_hide_window)
        
        show_hide_action = QAction("Show/Hide")
        show_hide_action.triggered.connect(self.show_hide_window)
        
        tray_menu = QMenu()
        tray_menu.addAction(show_hide_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.api_key_input)
        layout.addWidget(save_api_key_button)
        layout.addWidget(self.microphone_combo)
        layout.addWidget(start_button)
        layout.addWidget(stop_button)
        self.setLayout(layout)
        
    def save_api_key(self):
        api_key = self.api_key_input.text()
        keyring.set_password("speech_to_text_app", "api_key", api_key)

    def get_microphone_list(self):
        # TODO: Implement method to get the list of available microphones
        return []
        
    def start_dictation(self):
        # TODO: Implement method to start audio capturing and API integration
        pass
    
    def stop_dictation(self):
        # TODO: Implement method to stop audio capturing and API integration
        pass
    
    def show_hide_window(self, reason):
        if reason == QSystemTrayIcon.Trigger or reason == QSystemTrayIcon.MiddleClick:
            if self.isHidden():
                self.show()
            else:
                self.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    speech_to_text_app = SpeechToTextApp()
    speech_to_text_app.show()
    sys.exit(app.exec_())
```

This example provides a basic structure for the GUI application and handles the configuration area, system tray integration, and basic UI elements. You will need to implement the audio input handling, API integration, and keyboard shortcuts based on your specific requirements and the libraries you choose.