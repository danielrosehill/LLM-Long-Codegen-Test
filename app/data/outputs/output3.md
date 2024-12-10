# Qwen 2.5 Coder 32B Instruct Via Open Web UI (Via Open Router)

Given the requirements and the need to avoid using `Tkinter`, I will use `PyQt5` for the GUI, which is a powerful and attractive library for building cross-platform applications. Below is a detailed implementation guide split into logical chunks.

### 1. GUI Setup

First, we will set up the main GUI with the necessary components: configuration area, microphone selection, start/stop buttons, and system tray integration.

#### GUI Setup Script (`gui_setup.py`)

```python
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QLineEdit, QComboBox, QAction, QSystemTrayIcon, QMenu, QMessageBox
from PyQt5.QtCore import Qt, QObject, pyqtSignal

class MainWindow(QMainWindow):
    start_dictation_signal = pyqtSignal()
    stop_dictation_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Speech-to-Text Transcription")
        self.setGeometry(100, 100, 400, 300)

        self.config_area = QWidget()
        self.setup_ui()

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(Qt.UserIcon))
        self.tray_icon.activated.connect(self.show_or_hide)
        self.tray_icon.show()

    def setup_ui(self):
        layout = QVBoxLayout()

        api_key_label = QLabel("OpenAI API Key:")
        self.api_key_line_edit = QLineEdit()
        layout.addWidget(api_key_label)
        layout.addWidget(self.api_key_line_edit)

        microphone_label = QLabel("Select Microphone:")
        self.microphone_combo = QComboBox()
        layout.addWidget(microphone_label)
        layout.addWidget(self.microphone_combo)

        self.load_microphones()

        start_button = QPushButton("Start Dictation")
        start_button.clicked.connect(self.start_dictation)
        stop_button = QPushButton("Stop Dictation")
        stop_button.clicked.connect(self.stop_dictation)

        layout.addWidget(start_button)
        layout.addWidget(stop_button)

        self.config_area.setLayout(layout)
        self.setCentralWidget(self.config_area)

    def load_microphones(self):
        # Load available microphones here (placeholder)
        microphones = ["Microphone 1", "Microphone 2", "Microphone 3"]
        self.microphone_combo.addItems(microphones)

    def start_dictation(self):
        self.start_dictation_signal.emit()

    def stop_dictation(self):
        self.stop_dictation_signal.emit()

    def show_or_hide(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            if self.isMinimized():
                self.showNormal()
            else:
                self.hide()

    def closeEvent(self, event):
        event.ignore()
        self.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
```

### 2. Audio Input Handling

Next, we will handle capturing audio from the selected microphone.

#### Audio Handling Script (`audio_handling.py`)

```python
import pyaudio
import threading

class AudioCaptureWorker(QObject):
    audio_chunk_ready = pyqtSignal(bytes)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = False
        self.microphone_index = 0
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.chunk_size = 1024

    def start(self):
        self.running = True
        threading.Thread(target=self.capture_audio, daemon=True).start()

    def stop(self):
        self.running = False

    def capture_audio(self):
        audio = pyaudio.PyAudio()
        stream = audio.open(format=self.audio_format,
                            channels=self.channels,
                            rate=self.rate,
                            input=True,
                            input_device_index=self.microphone_index,
                            frames_per_buffer=self.chunk_size)

        while self.running:
            data = stream.read(self.chunk_size)
            self.audio_chunk_ready.emit(data)

        stream.stop_stream()
        stream.close()
        audio.terminate()

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication, QLabel
    from PyQt5.QtCore import QObject, pyqtSignal

    class MainWindow(QObject):
        def __init__(self):
            super().__init__()
            self.audio_worker = AudioCaptureWorker()
            self.audio_worker.audio_chunk_ready.connect(self.handle_audio_chunk)
            self.audio_worker.start()

        def handle_audio_chunk(self, audio_chunk):
            print(f"Received audio chunk of size {len(audio_chunk)}")

    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())
```

### 3. API Integration

Integrate with the OpenAI Whisper API for speech-to-text transcription.

#### API Integration Script (`api_integration.py`)

```python
import requests
import json

class WhisperAPI:
    def __init__(self, api_key):
        self.api_url = "https://api.openai.com/v1/audio/transcriptions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def transcribe_audio(self, audio_chunk):
        files = {"file": ("audio.wav", audio_chunk)}
        data = {"model": "whisper-1"}

        response = requests.post(self.api_url, headers=self.headers, files=files, data=data)

        if response.status_code == 200:
            transcription = response.json().get("text", "")
            return transcription
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

if __name__ == "__main__":
    api_key = "your_openai_api_key"
    whisper_api = WhisperAPI(api_key)

    audio_chunk = b"your_audio_data_here"  # Replace with actual audio data
    transcription = whisper_api.transcribe_audio(audio_chunk)
    print(f"Transcription: {transcription}")
```

### 4. Text Input Integration

Automatically insert transcribed text into any active text field across applications.

#### Text Input Integration Script (`text_input_integration.py`)

For this part, we need cross-platform solutions to send keystrokes to other applications. `pyautogui` can be used for this purpose.

```python
import pyautogui
import time

def send_text_to_active_window(text):
    pyautogui.write(text, interval=0.01)

if __name__ == "__main__":
    text_to_send = "Hello, this is a test transcription."
    time.sleep(2)  # Give time to focus on a text field
    send_text_to_active_window(text_to_send)
```

### 5. Persistent Settings

Store user configurations securely and persistently.

#### Persistent Settings Script (`persistent_settings.py`)

```python
import keyring
import json

class SettingsManager:
    def __init__(self, service_name="speech-to-text"):
        self.service_name = service_name

    def save_api_key(self, api_key):
        keyring.set_password(self.service_name, "api_key", api_key)

    def load_api_key(self):
        return keyring.get_password(self.service_name, "api_key")

    def save_config(self, config):
        with open("config.json", "w") as config_file:
            json.dump(config, config_file)

    def load_config(self):
        try:
            with open("config.json", "r") as config_file:
                return json.load(config_file)
        except FileNotFoundError:
            return {}

if __name__ == "__main__":
    settings_manager = SettingsManager()
    settings_manager.save_api_key("your_openai_api_key")
    api_key = settings_manager.load_api_key()
    print(f"Loaded API Key: {api_key}")

    config = {"microphone_index": 1, "start_shortcut": "F1", "stop_shortcut": "F2"}
    settings_manager.save_config(config)
    loaded_config = settings_manager.load_config()
    print(f"Loaded Config: {loaded_config}")
```

### 6. Main Application Script

Finally, combine all the components into a main application script.

#### Main Application Script (`main.py`)

```python
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal
from gui_setup import MainWindow as GUI_MainWindow
from audio_handling import AudioCaptureWorker
from api_integration import WhisperAPI
from text_input_integration import send_text_to_active_window
from persistent_settings import SettingsManager

class MainApplication(QObject):
    def __init__(self):
        super().__init__()
        self.settings_manager = SettingsManager()
        self.load_settings()

        self.gui = GUI_MainWindow()
        self.audio_worker = AudioCaptureWorker()
        self.whisper_api = WhisperAPI(self.api_key)

        self.connect_signals()

    def load_settings(self):
        self.api_key = self.settings_manager.load_api_key()
        config = self.settings_manager.load_config()
        self.microphone_index = config.get("microphone_index", 0)
        self.audio_worker.microphone_index = self.microphone_index

    def connect_signals(self):
        self.gui.start_dictation_signal.connect(self.start_dictation)
        self.gui.stop_dictation_signal.connect(self.stop_dictation)
        self.audio_worker.audio_chunk_ready.connect(self.process_audio_chunk)

    def start_dictation(self):
        self.audio_worker.start()
        self.gui.statusBar().showMessage("Dictation Started")

    def stop_dictation(self):
        self.audio_worker.stop()
        self.gui.statusBar().showMessage("Dictation Stopped")

    def process_audio_chunk(self, audio_chunk):
        transcription = self.whisper_api.transcribe_audio(audio_chunk)
        if transcription:
            send_text_to_active_window(transcription)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_app = MainApplication()
    main_app.gui.show()
    sys.exit(app.exec_())
```

### 7. Keyboard Shortcuts

Allow users to configure two keyboard shortcuts for starting and stopping dictation.

#### Keyboard Shortcuts Script (`keyboard_shortcuts.py`)

```python
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt

class ShortcutManager:
    def __init__(self, parent):
        self.parent = parent
        self.shortcuts = self.load_shortcuts()

    def load_shortcuts(self):
        config = self.parent.settings_manager.load_config()
        return {
            "start": config.get("start_shortcut", "F1"),
            "stop": config.get("stop_shortcut", "F2")
        }

    def set_shortcut(self, key, shortcut):
        self.shortcuts[key] = shortcut
        config = self.parent.settings_manager.load_config()
        config[key] = shortcut
        self.parent.settings_manager.save_config(config)

    def setup_shortcuts(self):
        self.setup_start_shortcut()
        self.setup_stop_shortcut()

    def setup_start_shortcut(self):
        shortcut_seq = QKeySequence(self.shortcuts["start"])
        self.parent.parent_gui.parent().registerShortcut(shortcut_seq, self.start_dictation)

    def setup_stop_shortcut(self):
        shortcut_seq = QKeySequence(self.shortcuts["stop"])
        self.parent.parent_gui.parent().registerShortcut(shortcut_seq, self.stop_dictation)

    def start_dictation(self):
        self.parent.start_dictation()

    def stop_dictation(self):
        self.parent.stop_dictation()

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
    from PyQt5.QtCore import QObject, pyqtSignal

    class MainWindow(QMainWindow):
        def __init__(self, parent):
            super().__init__(parent)
            self.setWindowTitle("Shortcut Manager")
            self.setGeometry(100, 100, 400, 300)

            self.shortcut_manager = ShortcutManager(self)
            self.shortcut_manager.setup_shortcuts()

    class MainApplication(QObject):
        def __init__(self):
            super().__init__()
            self.settings_manager = SettingsManager("speech-to-text")
            self.gui = MainWindow(self)

            self.connect_signals()

        def connect_signals(self):
            pass

        def start_dictation(self):
            print("Dictation Started")

        def stop_dictation(self):
            print("Dictation Stopped")

    app = QApplication(sys.argv)
    main_app = MainApplication()
    main_app.gui.show()
    sys.exit(app.exec_())
```

### Final Notes

1. **Integration**: Ensure all components are integrated properly by running each script independently and then gradually combining them into the main application.
2. **Testing**: Test each part of the application separately to ensure stability and functionality.
3. **Security**: Ensure sensitive data like API keys are handled securely using libraries like `keyring`.
4. **Error Handling**: Add proper error handling for network requests, audio processing, and GUI interactions.

This implementation should meet the requirements specified for a Python-based GUI application for real-time speech-to-text transcription using the OpenAI Whisper API on OpenSUSE Linux.