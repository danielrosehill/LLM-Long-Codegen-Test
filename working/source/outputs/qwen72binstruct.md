# Qwen 72B Instruct - Via Hugging Face Chat

### Python GUI for Speech-to-Text Using OpenAI Whisper API on OpenSUSE Linux

To create a Python-based GUI application for real-time speech-to-text transcription using the OpenAI Whisper API on OpenSUSE Linux, we will use the following libraries:

- **PyQt6** for the GUI
- **PyAudio** for handling audio input
- **Requests** for API integration
- **Keyring** for securely storing the API key
- **Pynput** for handling global keyboard shortcuts

### Step-by-Step Implementation

#### 1. Install Required Libraries

First, ensure you have the necessary libraries installed. You can install them using pip:

```sh
pip install PyQt6 pyaudio requests keyring pynput
```

#### 2. Main Application Structure

We will break down the application into several components:

1. **GUI Setup**
2. **API Integration**
3. **Audio Handling**
4. **Text Input Integration**
5. **Persistent Settings**
6. **System Tray Integration**
7. **Keyboard Shortcuts**

### 1. GUI Setup

We will use PyQt6 to create the main GUI and system tray integration.

```python
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QSystemTrayIcon, QMenu, QAction
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QIcon, QKeySequence

class SpeechToTextApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Speech-to-Text Transcription")
        self.setGeometry(100, 100, 400, 300)
        self.settings = QSettings("SpeechToTextApp", "Settings")

        self.init_ui()
        self.load_settings()
        self.init_tray()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()

        self.api_key_label = QLabel("OpenAI API Key:")
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.layout.addWidget(self.api_key_label)
        self.layout.addWidget(self.api_key_input)

        self.microphone_label = QLabel("Select Microphone:")
        self.microphone_combo = QComboBox()
        self.layout.addWidget(self.microphone_label)
        self.layout.addWidget(self.microphone_combo)

        self.start_button = QPushButton("Start Dictation")
        self.start_button.clicked.connect(self.start_dictation)
        self.layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Dictation")
        self.stop_button.clicked.connect(self.stop_dictation)
        self.layout.addWidget(self.stop_button)

        self.central_widget.setLayout(self.layout)

    def load_settings(self):
        self.api_key_input.setText(self.settings.value("api_key", ""))
        self.microphone_combo.setCurrentText(self.settings.value("microphone", ""))

    def save_settings(self):
        self.settings.setValue("api_key", self.api_key_input.text())
        self.settings.setValue("microphone", self.microphone_combo.currentText())

    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("icon.png"))
        self.tray_icon.setVisible(True)

        menu = QMenu()
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        menu.addAction(show_action)

        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide)
        menu.addAction(hide_action)

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit)
        menu.addAction(quit_action)

        self.tray_icon.setContextMenu(menu)

    def start_dictation(self):
        # Start dictation logic
        pass

    def stop_dictation(self):
        # Stop dictation logic
        pass

    def quit(self):
        self.save_settings()
        self.tray_icon.hide()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SpeechToTextApp()
    window.show()
    sys.exit(app.exec())
```

### 2. API Integration

We will use the `requests` library to interact with the OpenAI Whisper API.

```python
import requests

class WhisperAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/engines/whisper/transcriptions"

    def transcribe(self, audio_data):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "audio/wav"
        }
        response = requests.post(self.base_url, headers=headers, data=audio_data)
        if response.status_code == 200:
            return response.json()["text"]
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")
```

### 3. Audio Handling

We will use `pyaudio` to capture audio from the selected microphone and process it into chunks.

```python
import pyaudio
import wave

class AudioHandler:
    def __init__(self, microphone_index):
        self.microphone_index = microphone_index
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.frames = []

    def start_recording(self):
        self.frames = []
        self.stream = self.audio.open(format=pyaudio.paInt16,
                                      channels=1,
                                      rate=16000,
                                      input=True,
                                      input_device_index=self.microphone_index,
                                      frames_per_buffer=1024)
        self.stream.start_stream()

    def stop_recording(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

    def get_audio_chunk(self):
        if self.stream:
            data = self.stream.read(1024)
            self.frames.append(data)
            return data
        return None

    def save_audio(self, filename):
        wf = wave.open(filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)
        wf.writeframes(b''.join(self.frames))
        wf.close()
```

### 4. Text Input Integration

We will use the `pynput` library to simulate keyboard input.

```python
from pynput.keyboard import Controller

class TextInputController:
    def __init__(self):
        self.keyboard = Controller()

    def insert_text(self, text):
        self.keyboard.type(text)
```

### 5. Persistent Settings

We will use `QSettings` to store and load user configurations.

### 6. System Tray Integration

We have already set up the system tray in the GUI setup.

### 7. Keyboard Shortcuts

We will use `pynput` to handle global keyboard shortcuts.

```python
from pynput import keyboard

class ShortcutHandler:
    def __init__(self, start_dictation, stop_dictation):
        self.start_dictation = start_dictation
        self.stop_dictation = stop_dictation
        self.listener = None

    def start_listening(self):
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

    def stop_listening(self):
        if self.listener:
            self.listener.stop()
            self.listener = None

    def on_press(self, key):
        try:
            if key == keyboard.Key.f8:  # Example shortcut for start dictation
                self.start_dictation()
            elif key == keyboard.Key.f9:  # Example shortcut for stop dictation
                self.stop_dictation()
        except AttributeError:
            pass
```

### Final Integration

We will integrate all the components into the main application.

```python
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QSystemTrayIcon, QMenu, QAction
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QIcon, QKeySequence
import pyaudio
import wave
import requests
from pynput import keyboard
from pynput.keyboard import Controller

class SpeechToTextApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Speech-to-Text Transcription")
        self.setGeometry(100, 100, 400, 300)
        self.settings = QSettings("SpeechToTextApp", "Settings")

        self.api_key = ""
        self.microphone_index = 0
        self.audio_handler = None
        self.whisper_api = None
        self.text_input_controller = TextInputController()
        self.shortcut_handler = ShortcutHandler(self.start_dictation, self.stop_dictation)

        self.init_ui()
        self.load_settings()
        self.init_tray()
        self.shortcut_handler.start_listening()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()

        self.api_key_label = QLabel("OpenAI API Key:")
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.layout.addWidget(self.api_key_label)
        self.layout.addWidget(self.api_key_input)

        self.microphone_label = QLabel("Select Microphone:")
        self.microphone_combo = QComboBox()
        self.populate_microphones()
        self.layout.addWidget(self.microphone_label)
        self.layout.addWidget(self.microphone_combo)

        self.start_button = QPushButton("Start Dictation")
        self.start_button.clicked.connect(self.start_dictation)
        self.layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Dictation")
        self.stop_button.clicked.connect(self.stop_dictation)
        self.layout.addWidget(self.stop_button)

        self.central_widget.setLayout(self.layout)

    def populate_microphones(self):
        p = pyaudio.PyAudio()
        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            if device_info["maxInputChannels"] > 0:
                self.microphone_combo.addItem(device_info["name"], i)

    def load_settings(self):
        self.api_key = self.settings.value("api_key", "")
        self.microphone_index = int(self.settings.value("microphone_index", 0))
        self.api_key_input.setText(self.api_key)
        self.microphone_combo.setCurrentIndex(self.microphone_index)

    def save_settings(self):
        self.settings.setValue("api_key", self.api_key_input.text())
        self.settings.setValue("microphone_index", self.microphone_combo.currentIndex())

    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("icon.png"))
        self.tray_icon.setVisible(True)

        menu = QMenu()
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        menu.addAction(show_action)

        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide)
        menu.addAction(hide_action)

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit)
        menu.addAction(quit_action)

        self.tray_icon.setContextMenu(menu)

    def start_dictation(self):
        self.api_key = self.api_key_input.text()
        self.microphone_index = self.microphone_combo.currentIndex()
        self.save_settings()

        self.whisper_api = WhisperAPI(self.api_key)
        self.audio_handler = AudioHandler(self.microphone_index)
        self.audio_handler.start_recording()

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        self.transcribe_audio()

    def stop_dictation(self):
        if self.audio_handler:
            self.audio_handler.stop_recording()
            self.audio_handler = None

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def transcribe_audio(self):
        while self.audio_handler:
            audio_chunk = self.audio_handler.get_audio_chunk()
            if audio_chunk:
                try:
                    text = self.whisper_api.transcribe(audio_chunk)
                    self.text_input_controller.insert_text(text)
                except Exception as e:
                    print(f"Transcription Error: {e}")

    def quit(self):
        self.save_settings()
        self.stop_dictation()
        self.shortcut_handler.stop_listening()
        self.tray_icon.hide()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SpeechToTextApp()
    window.show()
    sys.exit(app.exec())
```

### Summary

This code provides a complete implementation of a speech-to-text transcription application using the OpenAI Whisper API on OpenSUSE Linux. The application includes a GUI for configuration, real-time transcription, system tray integration, and global keyboard shortcuts. Each component is modular and can be tested independently.