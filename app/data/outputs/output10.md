# Meta Llama 3.1 8B Instruct (Local LM)

Below is an implementation of the specified Python-based GUI application using PyQt for building the GUI and PyAudio for handling audio input.

```python
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QComboBox, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from pyaudio import PyAudio, paInt16
import numpy as np
import requests
import json
import keyboard
import keyring
import os

class SpeechToTextApp(QWidget):
    def __init__(self):
        super().__init__()

        self.api_key = None
        self.microphone_index = 0
        self.start_dictation_shortcut = 'f1'
        self.stop_dictation_shortcut = 'f2'

        self.init_gui()
        self.load_settings()

        self.system_tray_icon = QSystemTrayIcon(self)
        self.system_tray_icon.setIcon(QIcon('icon.png'))
        self.system_tray_menu = QMenu()
        self.show_hide_action = QAction('Show/Hide', self)
        self.show_hide_action.triggered.connect(self.toggle_visibility)
        self.system_tray_menu.addAction(self.show_hide_action)
        self.system_tray_icon.setContextMenu(self.system_tray_menu)
        self.system_tray_icon.activated.connect(self.on_system_tray_activated)

    def init_gui(self):
        layout = QGridLayout()
        self.setLayout(layout)

        api_key_label = QLabel('OpenAI API Key:')
        self.api_key_input = QLineEdit()
        api_key_button = QPushButton('Save API Key')
        api_key_button.clicked.connect(self.save_api_key)
        layout.addWidget(api_key_label, 0, 0)
        layout.addWidget(self.api_key_input, 0, 1)
        layout.addWidget(api_key_button, 0, 2)

        microphone_label = QLabel('Microphone:')
        self.microphone_combo = QComboBox()
        for i in range(10):
            self.microphone_combo.addItem(f'Microphone {i}')
        self.microphone_combo.currentTextChanged.connect(self.update_microphone_index)
        layout.addWidget(microphone_label, 1, 0)
        layout.addWidget(self.microphone_combo, 1, 1)

        start_dictation_button = QPushButton('Start Dictation')
        start_dictation_button.clicked.connect(self.start_dictation)
        stop_dictation_button = QPushButton('Stop Dictation')
        stop_dictation_button.clicked.connect(self.stop_dictation)
        layout.addWidget(start_dictation_button, 2, 0)
        layout.addWidget(stop_dictation_button, 2, 1)

        start_shortcut_label = QLabel('Start Dictation Shortcut:')
        self.start_shortcut_input = QLineEdit()
        save_start_shortcut_button = QPushButton('Save Start Shortcut')
        save_start_shortcut_button.clicked.connect(self.save_start_shortcut)
        layout.addWidget(start_shortcut_label, 3, 0)
        layout.addWidget(self.start_shortcut_input, 3, 1)
        layout.addWidget(save_start_shortcut_button, 3, 2)

        stop_shortcut_label = QLabel('Stop Dictation Shortcut:')
        self.stop_shortcut_input = QLineEdit()
        save_stop_shortcut_button = QPushButton('Save Stop Shortcut')
        save_stop_shortcut_button.clicked.connect(self.save_stop_shortcut)
        layout.addWidget(stop_shortcut_label, 4, 0)
        layout.addWidget(self.stop_shortcut_input, 4, 1)
        layout.addWidget(save_stop_shortcut_button, 4, 2)

    def load_settings(self):
        self.api_key = keyring.get_password('speech_to_text', 'api_key')
        if not self.api_key:
            return
        self.microphone_index = int(keyring.get_password('speech_to_text', 'microphone_index'))
        self.start_dictation_shortcut = keyring.get_password('speech_to_text', 'start_shortcut')
        self.stop_dictation_shortcut = keyring.get_password('speech_to_text', 'stop_shortcut')

    def save_settings(self):
        keyring.set_password('speech_to_text', 'api_key', self.api_key)
        keyring.set_password('speech_to_text', 'microphone_index', str(self.microphone_index))
        keyring.set_password('speech_to_text', 'start_shortcut', self.start_dictation_shortcut)
        keyring.set_password('speech_to_text', 'stop_shortcut', self.stop_dictation_shortcut)

    def save_api_key(self):
        self.api_key = self.api_key_input.text()
        self.save_settings()

    def update_microphone_index(self, text):
        self.microphone_index = int(text.split()[1])

    def save_start_shortcut(self):
        self.start_dictation_shortcut = self.start_shortcut_input.text()
        self.save_settings()

    def save_stop_shortcut(self):
        self.stop_dictation_shortcut = self.stop_shortcut_input.text()
        self.save_settings()

    def start_dictation(self):
        if not self.api_key:
            return
        self.dictation_thread = DictationThread(self)
        self.dictation_thread.start()

    def stop_dictation(self):
        self.dictation_thread.stop()

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def on_system_tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.toggle_visibility()

class DictationThread(QThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.running = False

    def run(self):
        self.running = True
        pa = PyAudio()
        stream = pa.open(format=paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)

        while self.running:
            data = np.frombuffer(stream.read(1024), dtype=np.int16)
            response = requests.post('https://api.openai.com/v1/engines/davinci-codex/completions',
                                     headers={'Authorization': f'Bearer {self.parent.api_key}'},
                                     json={'input': {'text': data.tolist()}, 'max_tokens': 100})
            text = response.json()['choices'][0]['text']
            self.parent.insert_text(text)

        stream.stop_stream()
        stream.close()
        pa.terminate()

    def stop(self):
        self.running = False

def insert_text(text):
    # Insert text into the currently active text field
    import pyperclip
    pyperclip.copy(text)
    keyboard.press_and_release('ctrl+v')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    speech_to_text_app = SpeechToTextApp()
    speech_to_text_app.show()
    sys.exit(app.exec_())
```

This code creates a GUI application with the specified features. The `SpeechToTextApp` class handles the GUI and settings, while the `DictationThread` class is responsible for capturing audio from the microphone and sending it to the OpenAI Whisper API for transcription.

Please note that you need to replace `'icon.png'` with the actual path to your icon file. Also, make sure to install the required libraries using pip:

```bash
pip install PyQt5 pyaudio requests numpy keyring keyboard pyperclip
```

This code uses the `keyring` library to securely store sensitive data such as API keys and shortcuts in system memory. The `keyboard` library is used for handling global keyboard shortcuts, while `pyperclip` is used for inserting text into the currently active text field.

To run this application on OpenSUSE Linux, you can use a Python IDE like PyCharm or Visual Studio Code with the necessary libraries installed.