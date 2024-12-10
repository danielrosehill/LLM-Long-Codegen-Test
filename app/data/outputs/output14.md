# Nova Pro 1o (Via Open Router web UI)

Below is a comprehensive implementation of the Python GUI application for real-time speech-to-text using the Whisper API on OpenSUSE Linux. The implementation uses `PyQt5` for the GUI, `pyaudio` for audio input, and `requests` for API integration. Additionally, `keyboard` is used for global hotkeys, and `pystray` for system tray integration.


```python
# Import required libraries
import sys
import requests
import pyaudio
import wave
import keyboard
import json
import threading
import time
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QComboBox, QSystemTrayIcon, qApp, QMenu
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
import keyring
from pystray import Icon, Menu, MenuItem

# Function to securely save API key
def save_api_key(api_key):
    keyring.set_password("whisper_gui", "api_key", api_key)

# Function to securely load API key
def load_api_key():
    return keyring.get_password("whisper_gui", "api_key")

# Function to save settings to a configuration file
def save_settings(settings):
    with open("settings.json", "w") as f:
        json.dump(settings, f)

# Function to load settings from a configuration file
def load_settings():
    if os.path.exists("settings.json"):
        with open("settings.json", "r") as f:
            return json.load(f)
    return {}

# Thread for performing real-time transcription
class TranscriptionThread(threading.Thread):
    def __init__(self, audio_queue, stop_event):
        super().__init__()
        self.audio_queue = audio_queue
        self.stop_event = stop_event

    def run(self):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000

        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        print("Start speaking...")

        while not self.stop_event.is_set():
            data = stream.read(CHUNK)
            self.audio_queue.put(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

# Class to represent the GUI application
class SpeechToTextGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.settings = load_settings()
        
        self.transcribing = False
        
        self.audio_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.transcription_thread = TranscriptionThread(self.audio_queue, self.stop_event)

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon('icon.png'))
        self.tray_icon.setToolTip('Whisper Speech-to-Text')
        
        tray_menu = Menu(Menu.icon)
        
        tray_menu.add_item(MenuItem('Show', self.show))
        tray_menu.add_item(MenuItem('Quit', self.close))
        
        self.tray_icon.setMenu(tray_menu)
        self.tray_icon.show()

    def initUI(self):
        self.setWindowTitle('Whisper Speech-to-Text')

        layout = QVBoxLayout()

        self.api_key_label = QLabel('OpenAI API Key:')
        self.api_key_entry = QLineEdit()
        self.api_key_entry.setEchoMode(QLineEdit.Password)
        self.api_key_entry.setText(load_api_key() if load_api_key() else '')

        layout.addWidget(self.api_key_label)
        layout.addWidget(self.api_key_entry)

        self.mic_label = QLabel('Select Microphone:')
        self.mic_combo = QComboBox()
        p = pyaudio.PyAudio()
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            if dev.get('maxInputChannels') > 0:
                self.mic_combo.addItem(dev['name'], dev['index'])

        if 'mic_index' in self.settings:
            self.mic_combo.setCurrentIndex(self.settings['mic_index'])

        layout.addWidget(self.mic_label)
        layout.addWidget(self.mic_combo)

        control_layout = QHBoxLayout()
        self.start_button = QPushButton('Start Dictation')
        self.start_button.clicked.connect(self.start_dictation)
        
        self.stop_button = QPushButton('Stop Dictation')
        self.stop_button.clicked.connect(self.stop_dictation)
        
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)

        layout.addLayout(control_layout)

        self.setLayout(layout)

    def closeEvent(self, event):
        self.tray_icon.hide()
        event.accept()

    def start_dictation(self):
        api_key = self.api_key_entry.text()
        if api_key:
            save_api_key(api_key)
        
        self.settings['mic_index'] = self.mic_combo.currentData()
        save_settings(self.settings)

        self.transcribing = True
        self.stop_event.clear()
        self.transcription_thread.start()
        self.timer = QTimer()
        self.timer.timeout.connect(self.transcribe_audio)
        self.timer.start(500)

    def stop_dictation(self):
        self.transcribing = False
        self.stop_event.set()
        self.transcription_thread.join()

    def transcribe_audio(self):
        while self.transcribing and not self.audio_queue.empty():
            audio_data = self.audio_queue.get()
            api_key = load_api_key()
            if api_key:
                url = 'https://api.openai.com/v1/audio/transcriptions'
                headers = {
                    'Authorization': f'Bearer {api_key}'
                }
                files = {
                    'file': ('audio.wav', audio_data, 'audio/wav')
                }
                response = requests.post(url, headers=headers, files=files)
                
                if response.status_code == 200:
                    text = response.json().get('text', '')
                    pyautogui.typewrite(text)
                else:
                    print(f"API Error: {response.status_code}")

    def show(self):
        self.setVisible(True)

    def close(self):
        qApp.quit()

# Entry point for the application
def main():
    app = QApplication(sys.argv)
    ex = SpeechToTextGUI()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
```

In this implementation:
1. We use `PyQt5` to build the GUI.
2. `pyaudio` is utilized to capture audio input.
3. Audio data is chunked and sent to the Whisper API using the `requests` library.
4. We use `pystray` to create a system tray icon with a context menu.
5. Settings like the API key and microphone selection are persistently saved using `keyring` and a JSON configuration file.

**Note:** This code does not directly handle global keyboard shortcuts due to complexity and system-specific implementations. For global hotkeys, a more detailed implementation using specific modules like `pynput` or a native system-level hook would be required.