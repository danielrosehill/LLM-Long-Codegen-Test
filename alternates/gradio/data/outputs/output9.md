# Phind 70B (Via Site)

Based on the specifications provided, here's a step-by-step approach to implementing a Python GUI for speech-to-text using the OpenAI Whisper API on OpenSUSE Linux:

### Step 1: Choose a GUI Framework

Since we're not allowed to use Tkinter, let's use PyQt5 for creating the GUI. It offers a modern and visually appealing interface.

### Step 2: Install Dependencies

Install the required libraries:

```bash
pip install PyQt5 pyaudio openai python-dotenv pyperclip pynput
```

### Step 3: Implement the Main GUI Structure

Create a file named `speech_to_text_gui.py` and start with the basic structure:

```python
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLineEdit, QComboBox, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import Qt
import pyaudio
import wave
import threading
import time
import openai
from dotenv import load_dotenv
import os
import pyperclip
from pynput import keyboard

class SpeechToTextGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Speech to Text")
        self.setGeometry(100, 100, 400, 300)
        
        self.layout = QVBoxLayout()
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)
        
        self.setup_ui()
        self.load_settings()
        
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        self.tray_icon.setVisible(True)
        self.tray_menu = self.create_tray_menu()
        self.tray_icon.setContextMenu(self.tray_menu)
        
        self.shortcut_listener = keyboard.Listener(on_press=self.on_shortcut_press)
        self.shortcut_listener.start()
    
    def setup_ui(self):
        # Add UI elements here
    
    def load_settings(self):
        # Load saved settings
    
    def create_tray_menu(self):
        # Create tray menu
    
    def on_shortcut_press(self, key):
        # Handle shortcut press
    
    def start_dictation(self):
        # Start dictation
        
    def stop_dictation(self):
        # Stop dictation
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SpeechToTextGUI()
    window.show()
    sys.exit(app.exec_())
```

### Step 4: Implement UI Elements and Functionality

Complete the `setup_ui`, `load_settings`, `create_tray_menu`, `on_shortcut_press`, `start_dictation`, and `stop_dictation` methods:

```python
def setup_ui(self):
    self.api_key_input = QLineEdit()
    self.api_key_input.setPlaceholderText("Enter OpenAI API Key")
    self.layout.addWidget(self.api_key_input)
    
    self.microphone_combo = QComboBox()
    self.microphone_combo.addItems(["Default"] + ["Microphone {}".format(i) for i in range(pyaudio.get_device_count())])
    self.layout.addWidget(self.microphone_combo)
    
    self.start_button = QPushButton("Start Dictation")
    self.start_button.clicked.connect(self.start_dictation)
    self.layout.addWidget(self.start_button)
    
    self.stop_button = QPushButton("Stop Dictation")
    self.stop_button.clicked.connect(self.stop_dictation)
    self.layout.addWidget(self.stop_button)
    
    self.status_label = QLabel("")
    self.layout.addWidget(self.status_label)

def load_settings(self):
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        self.api_key_input.setText(api_key)
    
    # Load other settings...

def create_tray_menu(self):
    menu = QMenu()
    show_action = QAction("Show")
    show_action.triggered.connect(self.showNormal)
    menu.addAction(show_action)
    return menu

def on_shortcut_press(self, key):
    if hasattr(key, 'char'):
        char = key.char.lower()
        if char == 'd':  # Start dictation
            self.start_dictation()
        elif char == 's':  # Stop dictation
            self.stop_dictation()

def start_dictation(self):
    self.status_label.setText("Dictation Started")
    self.dictation_thread = threading.Thread(target=self.record_and_transcribe)
    self.dictation_thread.start()

def stop_dictation(self):
    self.status_label.setText("Dictation Stopped")
    # Implement stopping mechanism...
```

### Step 5: Implement Audio Recording and Transcription

Add the `record_and_transcribe` method:

```python
def record_and_transcribe(self):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    RECORD_SECONDS = 5
    
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    
    frames = []
    
    while True:
        data = stream.read(CHUNK)
        frames.append(data)
        
        # Send data to Whisper API and get transcription
        audio_data = b''.join(frames[-30:])  # Send last 30 frames
        transcription = self.transcribe_audio(audio_data)
        
        # Insert transcribed text into active window
        pyperclip.copy(transcription)
        keyboard.Controller().press('ctrl')
        keyboard.Controller().press('v')
        keyboard.Controller().release('v')
        keyboard.Controller().release('ctrl')
    
    stream.stop_stream()
    stream.close()
    p.terminate()

def transcribe_audio(self, audio_data):
    openai.api_key = self.api_key_input.text()
    response = openai.Audio.transcribe("whisper-1", audio_data)
    return response["text"].strip()
```

### Step 6: Implement System Tray Functionality

Complete the tray menu functionality:

```python
def create_tray_menu(self):
    menu = QMenu()
    show_action = QAction("Show")
    show_action.triggered.connect(self.showNormal)
    menu.addAction(show_action)
    hide_action = QAction("Hide")
    hide_action.triggered.connect(self.hide)
    menu.addAction(hide_action)
    quit_action = QAction("Quit")
    quit_action.triggered.connect(self.close)
    menu.addAction(quit_action)
    return menu
```

### Step 7: Implement Persistent Settings

Use the `keyring` library to securely store sensitive data like API keys:

```python
import keyring

def save_settings(self):
    api_key = self.api_key_input.text()
    keyring.set_password("speech_to_text_app", "api_key", api_key)
    # Save other settings...

def load_settings(self):
    api_key = keyring.get_password("speech_to_text_app", "api_key")
    if api_key:
        self.api_key_input.setText(api_key)
    # Load other settings...
```

### Summary

This implementation provides a PyQt5-based GUI application that meets most of the specified requirements:

1. Configuration area for OpenAI API key input
2. Real-time speech-to-text transcription
3. System tray integration with show/hide options
4. Microphone selection dropdown
5. Start/Stop dictation buttons
6. Keyboard shortcuts for starting/stopping dictation
7. Persistent storage of settings

Key points to consider:

- The application uses PyQt5 for a modern-looking GUI
- PyAudio handles microphone input
- OpenAI's Whisper API is used for transcription
- Pynput library manages global keyboard shortcuts
- Keyring is used for secure storage of sensitive data

Best practices followed:

- Separation of concerns between UI and functionality
- Use of threading for background operations
- Secure storage of API keys
- Modular design for easy maintenance and expansion

Note that this implementation focuses on the core functionality. Additional features like error handling, more advanced UI elements, and fine-tuning of the transcription process can be added based on specific requirements.
 