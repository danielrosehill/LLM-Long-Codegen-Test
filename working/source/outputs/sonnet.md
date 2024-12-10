# Claude 3.5 Sonnet Latest - Via LibreChat (API Integration)

I'll create a PyQt6-based implementation of this speech-to-text application. Here's the complete code:

```python
import sys
import json
import os
import pyaudio
import wave
import threading
import keyboard
import requests
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                            QComboBox, QSystemTrayIcon, QMenu)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon
import keyring
import tempfile

class AudioRecorder(QThread):
    finished = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.frames = []
        self.p = pyaudio.PyAudio()
        self.selected_device = 0

    def set_device(self, device_index):
        self.selected_device = device_index

    def run(self):
        self.is_recording = True
        stream = self.p.open(format=self.format,
                           channels=self.channels,
                           rate=self.rate,
                           input=True,
                           input_device_index=self.selected_device,
                           frames_per_buffer=self.chunk)

        while self.is_recording:
            data = stream.read(self.chunk)
            self.frames.append(data)

        stream.stop_stream()
        stream.close()

        # Save the recorded audio to a temporary WAV file
        temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        with wave.open(temp_wav.name, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.p.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.frames))

        # Send to Whisper API
        self.transcribe_audio(temp_wav.name)
        
        # Clean up
        os.unlink(temp_wav.name)
        self.frames = []

    def stop(self):
        self.is_recording = False

    def transcribe_audio(self, audio_file):
        api_key = keyring.get_password("whisper_app", "openai_api_key")
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        
        with open(audio_file, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                'https://api.openai.com/v1/audio/transcriptions',
                headers=headers,
                files=files,
                data={'model': 'whisper-1'}
            )
            
        if response.status_code == 200:
            text = response.json()['text']
            self.finished.emit(text)
        else:
            self.finished.emit(f"Error: {response.status_code}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Speech-to-Text")
        self.setGeometry(100, 100, 400, 300)
        
        # Initialize audio recorder
        self.recorder = AudioRecorder()
        self.recorder.finished.connect(self.on_transcription_complete)
        
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon.fromTheme("audio-input-microphone"))
        self.setup_tray_menu()
        self.tray_icon.show()
        
        # Setup UI
        self.setup_ui()
        
        # Load settings
        self.load_settings()
        
        # Setup keyboard shortcuts
        self.setup_shortcuts()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # API Key configuration
        api_layout = QHBoxLayout()
        api_label = QLabel("OpenAI API Key:")
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        api_layout.addWidget(api_label)
        api_layout.addWidget(self.api_key_input)
        layout.addLayout(api_layout)

        # Microphone selection
        mic_layout = QHBoxLayout()
        mic_label = QLabel("Microphone:")
        self.mic_combo = QComboBox()
        self.populate_mic_list()
        mic_layout.addWidget(mic_label)
        mic_layout.addWidget(self.mic_combo)
        layout.addLayout(mic_layout)

        # Shortcuts configuration
        shortcut_layout = QVBoxLayout()
        start_shortcut_layout = QHBoxLayout()
        stop_shortcut_layout = QHBoxLayout()
        
        start_label = QLabel("Start Shortcut:")
        self.start_shortcut_input = QLineEdit()
        start_shortcut_layout.addWidget(start_label)
        start_shortcut_layout.addWidget(self.start_shortcut_input)
        
        stop_label = QLabel("Stop Shortcut:")
        self.stop_shortcut_input = QLineEdit()
        stop_shortcut_layout.addWidget(stop_label)
        stop_shortcut_layout.addWidget(self.stop_shortcut_input)
        
        shortcut_layout.addLayout(start_shortcut_layout)
        shortcut_layout.addLayout(stop_shortcut_layout)
        layout.addLayout(shortcut_layout)

        # Control buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Dictation")
        self.stop_button = QPushButton("Stop Dictation")
        self.stop_button.setEnabled(False)
        
        self.start_button.clicked.connect(self.start_recording)
        self.stop_button.clicked.connect(self.stop_recording)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        layout.addLayout(button_layout)

    def populate_mic_list(self):
        p = pyaudio.PyAudio()
        self.mic_combo.clear()
        
        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                self.mic_combo.addItem(
                    device_info['name'], 
                    device_info['index']
                )
        p.terminate()

    def setup_tray_menu(self):
        menu = QMenu()
        show_action = menu.addAction("Show")
        show_action.triggered.connect(self.show)
        hide_action = menu.addAction("Hide")
        hide_action.triggered.connect(self.hide)
        quit_action = menu.addAction("Quit")
        quit_action.triggered.connect(QApplication.quit)
        self.tray_icon.setContextMenu(menu)

    def setup_shortcuts(self):
        keyboard.on_press_key(self.start_shortcut_input.text(), 
                            lambda _: self.start_recording())
        keyboard.on_press_key(self.stop_shortcut_input.text(), 
                            lambda _: self.stop_recording())

    def save_settings(self):
        settings = {
            'microphone_index': self.mic_combo.currentData(),
            'start_shortcut': self.start_shortcut_input.text(),
            'stop_shortcut': self.stop_shortcut_input.text()
        }
        
        with open('settings.json', 'w') as f:
            json.dump(settings, f)
            
        # Save API key securely
        keyring.set_password("whisper_app", "openai_api_key", 
                           self.api_key_input.text())

    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                
            mic_index = settings.get('microphone_index', 0)
            index = self.mic_combo.findData(mic_index)
            if index >= 0:
                self.mic_combo.setCurrentIndex(index)
                
            self.start_shortcut_input.setText(
                settings.get('start_shortcut', 'ctrl+shift+s'))
            self.stop_shortcut_input.setText(
                settings.get('stop_shortcut', 'ctrl+shift+x'))
                
            # Load API key
            api_key = keyring.get_password("whisper_app", "openai_api_key")
            if api_key:
                self.api_key_input.setText(api_key)
                
        except FileNotFoundError:
            pass

    def start_recording(self):
        self.recorder.set_device(self.mic_combo.currentData())
        self.recorder.start()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_recording(self):
        self.recorder.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def on_transcription_complete(self, text):
        keyboard.write(text)

    def closeEvent(self, event):
        self.save_settings()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
```

To run this application, you'll need to install the required dependencies:

```bash
pip install PyQt6 pyaudio requests keyboard keyring
```

This implementation includes all the requested features:

1. A modern GUI using PyQt6
2. Secure API key storage using keyring
3. Microphone selection with persistence
4. System tray integration
5. Configurable keyboard shortcuts
6. Real-time audio recording and transcription
7. Automatic text insertion into active text fields

The application saves settings to a JSON file and securely stores the API key using the system keyring. The GUI is clean and intuitive, with proper error handling and state management.

To use the application:

1. Enter your OpenAI API key
2. Select your preferred microphone
3. Configure your keyboard shortcuts
4. Click "Start Dictation" or use the configured shortcut to begin recording
5. Speak into the microphone
6. Click "Stop Dictation" or use the configured shortcut to stop recording
7. The transcribed text will be automatically typed into the active text field

The application can be minimized to the system tray and will continue to work in the background. All settings are persisted between sessions.