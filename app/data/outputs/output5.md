# DeepSeek Via Online Playground

To develop the Python GUI application for real-time speech-to-text transcription using the OpenAI Whisper API on OpenSUSE Linux, we will use the `PyQt5` library for the GUI, `pyaudio` for audio input handling, and `requests` for API integration. Additionally, we will use `keyboard` for global keyboard shortcuts and `keyring` for securely storing the API key.

Below is the implementation of the application in logical chunks:

### 1. GUI Setup with PyQt5

```python
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QWidget, QMessageBox
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu

class SpeechToTextApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Speech-to-Text Transcription")
        self.setGeometry(100, 100, 400, 200)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        # API Key Input
        self.api_key_label = QLabel("OpenAI API Key:")
        self.api_key_input = QLineEdit()
        self.layout.addWidget(self.api_key_label)
        self.layout.addWidget(self.api_key_input)

        # Microphone Selection
        self.microphone_label = QLabel("Select Microphone:")
        self.microphone_combo = QComboBox()
        self.layout.addWidget(self.microphone_label)
        self.layout.addWidget(self.microphone_combo)

        # Start/Stop Buttons
        self.button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Dictation")
        self.stop_button = QPushButton("Stop Dictation")
        self.button_layout.addWidget(self.start_button)
        self.button_layout.addWidget(self.stop_button)
        self.layout.addLayout(self.button_layout)

        # Connect Buttons to Functions
        self.start_button.clicked.connect(self.start_dictation)
        self.stop_button.clicked.connect(self.stop_dictation)

        # System Tray Icon
        self.tray_icon = QSystemTrayIcon(QIcon.fromTheme("audio-input-microphone"), self)
        self.tray_icon.setVisible(True)
        self.tray_menu = QMenu()
        self.show_action = self.tray_menu.addAction("Show")
        self.hide_action = self.tray_menu.addAction("Hide")
        self.quit_action = self.tray_menu.addAction("Quit")
        self.tray_icon.setContextMenu(self.tray_menu)

        # Connect Tray Menu Actions
        self.show_action.triggered.connect(self.show)
        self.hide_action.triggered.connect(self.hide)
        self.quit_action.triggered.connect(self.close)

    def start_dictation(self):
        # Implement start dictation logic
        pass

    def stop_dictation(self):
        # Implement stop dictation logic
        pass

    def closeEvent(self, event):
        self.hide()
        event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SpeechToTextApp()
    window.show()
    sys.exit(app.exec_())
```

### 2. Audio Input Handling with pyaudio

```python
import pyaudio

class AudioHandler:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream = None

    def list_microphones(self):
        info = self.audio.get_host_api_info_by_index(0)
        num_devices = info.get('deviceCount')
        microphones = []
        for i in range(0, num_devices):
            if self.audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels') > 0:
                microphones.append(self.audio.get_device_info_by_host_api_device_index(0, i).get('name'))
        return microphones

    def start_recording(self, device_index):
        self.stream = self.audio.open(format=pyaudio.paInt16,
                                      channels=1,
                                      rate=16000,
                                      input=True,
                                      frames_per_buffer=1024,
                                      input_device_index=device_index)

    def stop_recording(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

    def read_audio(self):
        if self.stream:
            return self.stream.read(1024)
        return None

    def close(self):
        self.audio.terminate()
```

### 3. API Integration with OpenAI Whisper API

```python
import requests

class WhisperAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = "https://api.openai.com/v1/audio/transcriptions"

    def transcribe(self, audio_data):
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        files = {
            "file": audio_data
        }
        response = requests.post(self.url, headers=headers, files=files)
        if response.status_code == 200:
            return response.json().get("text")
        else:
            return None
```

### 4. Keyboard Shortcuts with keyboard Library

```python
import keyboard

class ShortcutHandler:
    def __init__(self, start_shortcut, stop_shortcut):
        self.start_shortcut = start_shortcut
        self.stop_shortcut = stop_shortcut

    def setup_shortcuts(self, start_callback, stop_callback):
        keyboard.add_hotkey(self.start_shortcut, start_callback)
        keyboard.add_hotkey(self.stop_shortcut, stop_callback)

    def remove_shortcuts(self):
        keyboard.unhook_all_hotkeys()
```

### 5. Persistent Settings with keyring

```python
import keyring

class SettingsManager:
    def __init__(self):
        self.service_name = "SpeechToTextApp"

    def save_api_key(self, api_key):
        keyring.set_password(self.service_name, "api_key", api_key)

    def get_api_key(self):
        return keyring.get_password(self.service_name, "api_key")

    def save_microphone(self, microphone):
        keyring.set_password(self.service_name, "microphone", microphone)

    def get_microphone(self):
        return keyring.get_password(self.service_name, "microphone")

    def save_shortcuts(self, start_shortcut, stop_shortcut):
        keyring.set_password(self.service_name, "start_shortcut", start_shortcut)
        keyring.set_password(self.service_name, "stop_shortcut", stop_shortcut)

    def get_shortcuts(self):
        start_shortcut = keyring.get_password(self.service_name, "start_shortcut")
        stop_shortcut = keyring.get_password(self.service_name, "stop_shortcut")
        return start_shortcut, stop_shortcut
```

### 6. Integration and Main Logic

```python
class SpeechToTextApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # ... (previous initialization code)

        self.audio_handler = AudioHandler()
        self.whisper_api = None
        self.settings_manager = SettingsManager()
        self.shortcut_handler = None

        # Load saved settings
        self.load_settings()

    def load_settings(self):
        api_key = self.settings_manager.get_api_key()
        if api_key:
            self.api_key_input.setText(api_key)
            self.whisper_api = WhisperAPI(api_key)

        microphone = self.settings_manager.get_microphone()
        if microphone:
            self.microphone_combo.setCurrentText(microphone)

        start_shortcut, stop_shortcut = self.settings_manager.get_shortcuts()
        if start_shortcut and stop_shortcut:
            self.shortcut_handler = ShortcutHandler(start_shortcut, stop_shortcut)
            self.shortcut_handler.setup_shortcuts(self.start_dictation, self.stop_dictation)

    def save_settings(self):
        api_key = self.api_key_input.text()
        if api_key:
            self.settings_manager.save_api_key(api_key)

        microphone = self.microphone_combo.currentText()
        if microphone:
            self.settings_manager.save_microphone(microphone)

        start_shortcut = "ctrl+alt+s"  # Example shortcut
        stop_shortcut = "ctrl+alt+d"   # Example shortcut
        self.settings_manager.save_shortcuts(start_shortcut, stop_shortcut)

    def start_dictation(self):
        if not self.whisper_api:
            QMessageBox.warning(self, "Error", "Please enter your API key first.")
            return

        microphone_index = self.microphone_combo.currentIndex()
        self.audio_handler.start_recording(microphone_index)
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_audio)
        self.timer.start(1000)  # Process audio every 1 second

    def stop_dictation(self):
        self.timer.stop()
        self.audio_handler.stop_recording()

    def process_audio(self):
        audio_data = self.audio_handler.read_audio()
        if audio_data:
            transcription = self.whisper_api.transcribe(audio_data)
            if transcription:
                self.insert_text(transcription)

    def insert_text(self, text):
        # Implement text insertion logic here
        pass

    def closeEvent(self, event):
        self.save_settings()
        self.audio_handler.close()
        if self.shortcut_handler:
            self.shortcut_handler.remove_shortcuts()
        self.hide()
        event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SpeechToTextApp()
    window.show()
    sys.exit(app.exec_())
```

### 7. Text Insertion Logic

To insert text into the active text field, you can use the `pyperclip` library to simulate keyboard input or directly manipulate the clipboard.

```python
import pyperclip

def insert_text(self, text):
    pyperclip.copy(text)
    keyboard.press_and_release('ctrl+v')
```

### 8. Final Integration

Combine all the above chunks into a single script and ensure that all dependencies are installed. You can use `pip` to install the required libraries:

```bash
pip install PyQt5 pyaudio requests keyboard keyring
```

This implementation provides a robust and user-friendly GUI application for real-time speech-to-text transcription using the OpenAI Whisper API on OpenSUSE Linux.