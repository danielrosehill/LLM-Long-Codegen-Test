# Nova Pro 1o Run 2 (Open Router)

Certainly! Below, I'll outline a Python GUI application using PyQt5 for the described functionalities. Ensure you have all the required libraries installed:

```bash
pip install pyqt5 pyqt5-tools pyaudio openai keyboard keyring
```

## Step 1: Configuration and Persistent Settings

We'll use `keyring` to store the API key securely, and a JSON file for other settings.

```python
import keyring
import json
import os

SETTINGS_FILE = "settings.json"

def save_settings(api_key, microphone, start_shortcut, stop_shortcut):
    keyring.set_password("whisper_gui", "api_key", api_key)
    settings = {
        "microphone": microphone,
        "start_shortcut": start_shortcut,
        "stop_shortcut": stop_shortcut
    }
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f)

def load_settings():
    api_key = keyring.get_password("whisper_gui", "api_key")
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
            return api_key, settings.get("microphone", ""), settings.get("start_shortcut", ""), settings.get("stop_shortcut", "")
    return api_key, "", "", ""
```

## Step 2: GUI with PyQt5

```python
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QSystemTrayIcon, QMenu
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt
import sys

class WhisperGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.setup_tray_icon()
        
        self.api_key, self.microphone, self.start_shortcut, self.stop_shortcut = load_settings()
        
    def initUI(self):
        self.setWindowTitle('Whisper Speech-to-Text')
        
        layout = QVBoxLayout()
        
        self.api_key_label = QLabel('OpenAI API Key:')
        self.api_key_input = QLineEdit(self)
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setText(self.api_key)
        
        self.microphone_label = QLabel('Select Microphone:')
        self.microphone_combo = QComboBox(self)
        # Load available microphones here (you need to implement this part using pyaudio)
        
        self.start_button = QPushButton('Start Dictation')
        self.start_button.clicked.connect(self.start_dictation)
        
        self.stop_button = QPushButton('Stop Dictation')
        self.stop_button.clicked.connect(self.stop_dictation)

        layout.addWidget(self.api_key_label)
        layout.addWidget(self.api_key_input)
        layout.addWidget(self.microphone_label)
        layout.addWidget(self.microphone_combo)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        
        self.setLayout(layout)
        
    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(QIcon("whisper_icon.png"), self)
        self.tray_icon.setToolTip('Whisper Speech-to-Text')

        tray_menu = QMenu()
        show_action = tray_menu.addAction("Show")
        show_action.triggered.connect(self.show)
        exit_action = tray_menu.addAction("Exit")
        exit_action.triggered.connect(QApplication.instance().quit)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def start_dictation(self):
        print("Start Dictation Clicked")
        # Implement the start dictation logic here
        
    def stop_dictation(self):
        print("Stop Dictation Clicked")
        # Implement the stop dictation logic here

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Whisper Speech-to-Text",
            "Application is running in the background.",
            QSystemTrayIcon.Information,
            2000
        )

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WhisperGUI()
    ex.show()
    sys.exit(app.exec_())
```

## Step 3: Audio Handling and Transcription

For brevity, only the main components are shown. You need to integrate `pyaudio` for capturing audio and `openai` for transcription.

```python
import pyaudio
import wave
import openai
import keyboard

# For real use, encapsulate these in a class or functions
openai.api_key = 'your_api_key'  # This should be loaded from secure storage

def record_audio(duration=5):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    WAVE_OUTPUT_FILENAME = "output.wav"

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Recording")

    frames = []

    for i in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Finished Recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def transcribe_audio(file_path):
    with open(file_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript["text"]
```

## Step 4: Integrate Transcription with GUI

Integrate the transcription logic into your GUI and handle events appropriately.

```python
# Inside WhisperGUI class

def start_dictation(self):
    api_key = self.api_key_input.text()
    self.microphone = self.microphone_combo.currentText()
    save_settings(api_key, self.microphone, self.start_shortcut, self.stop_shortcut)
    
    openai.api_key = api_key
    
    def on_start():
        print("Dictation started")
        while self.is_recording:
            record_audio()
            text = transcribe_audio("output.wav")
            keyboard.send(text)

    self.is_recording = True
    self.record_thread = threading.Thread(target=on_start)
    self.record_thread.start()
    
def stop_dictation(self):
    self.is_recording = False
    if self.record_thread.is_alive():
        self.record_thread.join()
    print("Dictation stopped")
```

## Final Notes

This implementation covers the primary components. You'll need to extend it by:

1. Properly handling audio input (list available microphones, select the correct one).
2. Ensuring secure storage and retrieval of the API key.
3. Handling global keyboard shortcuts.
4. Making the GUI more robust and user-friendly.