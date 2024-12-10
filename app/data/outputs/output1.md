# Qwen 2.5 Coder 32B Instruct Via Hugging Face Chat

Certainly! Given the requirements, we'll use `PyQt5` for the GUI, `pyaudio` for audio handling, `requests` for API integration, and `keyboard` for handling global keyboard shortcuts. We'll also use `keyring` for secure storage of the API key and `configparser` for storing other configurations.

Let's break down the implementation into logical chunks:

### Chunk 1: GUI Setup with PyQt5

First, we'll set up the main GUI with PyQt5. This will include the configuration area, microphone selection, and start/stop buttons.

```python
import sys
import configparser
import keyring
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QSystemTrayIcon, QMenu, QAction, QInputDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

class SpeechToTextApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Speech-to-Text with OpenAI Whisper")
        self.setGeometry(100, 100, 400, 300)
        
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        
        self.api_key = keyring.get_password('openai', 'api_key')
        self.microphone_index = self.config.getint('Settings', 'microphone_index', fallback=0)
        self.start_shortcut = self.config.get('Shortcuts', 'start', fallback='ctrl+shift+s')
        self.stop_shortcut = self.config.get('Shortcuts', 'stop', fallback='ctrl+shift+e')
        
        self.init_ui()
        self.init_tray()
        self.load_settings()
        
    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        self.api_key_label = QLabel("OpenAI API Key:")
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.PasswordEchoOnEdit)
        self.api_key_input.setText(self.api_key if self.api_key else "")
        
        self.microphone_label = QLabel("Select Microphone:")
        self.microphone_combo = QComboBox()
        self.load_microphones()
        
        self.start_button = QPushButton("Start Dictation")
        self.stop_button = QPushButton("Stop Dictation")
        
        self.layout.addWidget(self.api_key_label)
        self.layout.addWidget(self.api_key_input)
        self.layout.addWidget(self.microphone_label)
        self.layout.addWidget(self.microphone_combo)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.stop_button)
        
        self.start_button.clicked.connect(self.start_dictation)
        self.stop_button.clicked.connect(self.stop_dictation)
        
    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(QIcon("icon.png"), self)
        self.tray_icon.setToolTip("Speech-to-Text with OpenAI Whisper")
        self.tray_icon.activated.connect(self.toggle_visibility)
        
        self.tray_menu = QMenu(self)
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide)
        self.tray_menu.addAction(show_action)
        self.tray_menu.addAction(hide_action)
        
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()
        
    def load_microphones(self):
        import pyaudio
        p = pyaudio.PyAudio()
        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                self.microphone_combo.addItem(device_info['name'], i)
        self.microphone_combo.setCurrentIndex(self.microphone_index)
        
    def load_settings(self):
        self.microphone_combo.setCurrentIndex(self.microphone_index)
        
    def toggle_visibility(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.setVisible(not self.isVisible())
            
    def start_dictation(self):
        self.api_key = self.api_key_input.text()
        keyring.set_password('openai', 'api_key', self.api_key)
        self.microphone_index = self.microphone_combo.itemData(self.microphone_combo.currentIndex())
        self.config['Settings'] = {
            'microphone_index': str(self.microphone_index)
        }
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)
        # Start audio capture and transcription
        print("Starting dictation...")
        
    def stop_dictation(self):
        # Stop audio capture and transcription
        print("Stopping dictation...")
        
    def closeEvent(self, event):
        self.tray_icon.hide()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = SpeechToTextApp()
    main_window.show()
    sys.exit(app.exec_())
```

### Chunk 2: Audio Handling with PyAudio

Next, we'll handle audio input using `pyaudio`.

```python
import pyaudio
import wave
import threading
import queue

class AudioHandler:
    def __init__(self, microphone_index):
        self.microphone_index = microphone_index
        self.audio_queue = queue.Queue()
        self.stream = None
        self.is_running = False
        self.chunks = []
        
    def start(self):
        self.is_running = True
        self.chunks = []
        p = pyaudio.PyAudio()
        self.stream = p.open(format=pyaudio.paInt16,
                             channels=1,
                             rate=16000,
                             input=True,
                             frames_per_buffer=1024,
                             input_device_index=self.microphone_index)
        self.audio_thread = threading.Thread(target=self.read_audio)
        self.audio_thread.start()
        
    def read_audio(self):
        while self.is_running:
            data = self.stream.read(1024)
            self.chunks.append(data)
            self.audio_queue.put(data)
        
    def stop(self):
        self.is_running = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.audio_thread.join()
        
    def get_chunks(self):
        return self.chunks
```

### Chunk 3: API Integration with OpenAI Whisper

Now, we'll integrate with the OpenAI Whisper API using `requests`.

```python
import requests
import json

class WhisperAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = "https://api.openai.com/v1/audio/transcriptions"
        
    def transcribe(self, audio_data):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "multipart/form-data"
        }
        files = {
            "file": ("audio.wav", audio_data, "audio/wav")
        }
        data = {
            "model": "whisper-1"
        }
        response = requests.post(self.url, headers=headers, files=files, data=data)
        if response.status_code == 200:
            return response.json()['text']
        else:
            return None
```

### Chunk 4: Text Input Integration with Keyboard

Finally, we'll handle text input into active applications using the `keyboard` library.

```python
import keyboard
import pyperclip

class TextInputHandler:
    def __init__(self, start_shortcut, stop_shortcut):
        self.start_shortcut = start_shortcut
        self.stop_shortcut = stop_shortcut
        self.is_dictating = False
        
    def start_listening(self):
        keyboard.add_hotkey(self.start_shortcut, self.start_dictation)
        keyboard.add_hotkey(self.stop_shortcut, self.stop_dictation)
        keyboard.wait()
        
    def start_dictation(self):
        self.is_dictating = True
        print("Dictation started...")
        
    def stop_dictation(self):
        self.is_dictating = False
        print("Dictation stopped...")
        
    def insert_text(self, text):
        if self.is_dictating:
            pyperclip.copy(text)
            keyboard.send('ctrl+v')
```

### Integrating All Chunks

Now, let's integrate all the chunks into the main application.

```python
import sys
import configparser
import keyring
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QSystemTrayIcon, QMenu, QAction, QInputDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import pyaudio
import wave
import threading
import queue
import requests
import json
import keyboard
import pyperclip

class SpeechToTextApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Speech-to-Text with OpenAI Whisper")
        self.setGeometry(100, 100, 400, 300)
        
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        
        self.api_key = keyring.get_password('openai', 'api_key')
        self.microphone_index = self.config.getint('Settings', 'microphone_index', fallback=0)
        self.start_shortcut = self.config.get('Shortcuts', 'start', fallback='ctrl+shift+s')
        self.stop_shortcut = self.config.get('Shortcuts', 'stop', fallback='ctrl+shift+e')
        
        self.audio_handler = AudioHandler(self.microphone_index)
        self.whisper_api = WhisperAPI(self.api_key)
        self.text_input_handler = TextInputHandler(self.start_shortcut, self.stop_shortcut)
        
        self.init_ui()
        self.init_tray()
        self.load_settings()
        self.text_input_handler.start_listening()
        
    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        self.api_key_label = QLabel("OpenAI API Key:")
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.PasswordEchoOnEdit)
        self.api_key_input.setText(self.api_key if self.api_key else "")
        
        self.microphone_label = QLabel("Select Microphone:")
        self.microphone_combo = QComboBox()
        self.load_microphones()
        
        self.start_button = QPushButton("Start Dictation")
        self.stop_button = QPushButton("Stop Dictation")
        
        self.layout.addWidget(self.api_key_label)
        self.layout.addWidget(self.api_key_input)
        self.layout.addWidget(self.microphone_label)
        self.layout.addWidget(self.microphone_combo)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.stop_button)
        
        self.start_button.clicked.connect(self.start_dictation)
        self.stop_button.clicked.connect(self.stop_dictation)
        
    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(QIcon("icon.png"), self)
        self.tray_icon.setToolTip("Speech-to-Text with OpenAI Whisper")
        self.tray_icon.activated.connect(self.toggle_visibility)
        
        self.tray_menu = QMenu(self)
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide)
        self.tray_menu.addAction(show_action)
        self.tray_menu.addAction(hide_action)
        
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()
        
    def load_microphones(self):
        p = pyaudio.PyAudio()
        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                self.microphone_combo.addItem(device_info['name'], i)
        self.microphone_combo.setCurrentIndex(self.microphone_index)
        
    def load_settings(self):
        self.microphone_combo.setCurrentIndex(self.microphone_index)
        
    def toggle_visibility(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.setVisible(not self.isVisible())
            
    def start_dictation(self):
        self.api_key = self.api_key_input.text()
        keyring.set_password('openai', 'api_key', self.api_key)
        self.microphone_index = self.microphone_combo.itemData(self.microphone_combo.currentIndex())
        self.config['Settings'] = {
            'microphone_index': str(self.microphone_index)
        }
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)
        self.audio_handler.start()
        self.text_input_handler.start_dictation()
        threading.Thread(target=self.process_audio).start()
        
    def stop_dictation(self):
        self.audio_handler.stop()
        self.text_input_handler.stop_dictation()
        
    def process_audio(self):
        while self.audio_handler.is_running:
            chunks = self.audio_handler.get_chunks()
            if chunks:
                audio_data = b''.join(chunks)
                transcription = self.whisper_api.transcribe(audio_data)
                if transcription:
                    self.text_input_handler.insert_text(transcription)
                self.audio_handler.chunks = []
        
    def closeEvent(self, event):
        self.tray_icon.hide()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = SpeechToTextApp()
    main_window.show()
    sys.exit(app.exec_())
```

### Additional Notes

1. **Icon File**: Ensure you have an `icon.png` file in the same directory as your script for the system tray icon.
2. **Permissions**: Make sure you have the necessary permissions to record audio and use global keyboard shortcuts.
3. **Testing**: Test the application on OpenSUSE Linux to ensure compatibility and functionality.

This implementation should meet the specified requirements and provide a functional GUI application for real-time speech-to-text transcription using the OpenAI Whisper API on OpenSUSE Linux.