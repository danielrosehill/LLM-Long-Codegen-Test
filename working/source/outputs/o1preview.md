# o1 Preview (LibreChat - API Integration)

Sure! Below is a Python script that implements the specified application using PyQt5 for the GUI. The script is organized into logical sections for clarity.

Please note that you'll need to install the necessary Python packages before running the script:

```bash
pip install PyQt5 pyaudio requests keyboard
```

### **1. GUI Setup with PyQt5**

```python
# gui.py
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
import settings

class SpeechToTextApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Load settings
        self.api_key = settings.get_api_key()
        self.selected_microphone = settings.get_microphone()
        self.start_shortcut = settings.get_start_shortcut()
        self.stop_shortcut = settings.get_stop_shortcut()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Speech-to-Text Application')

        # Central widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        # Layouts
        main_layout = QtWidgets.QVBoxLayout()
        config_group = QtWidgets.QGroupBox("Configuration")
        config_layout = QtWidgets.QFormLayout()
        control_group = QtWidgets.QGroupBox("Controls")
        control_layout = QtWidgets.QHBoxLayout()

        # Configuration widgets
        self.api_key_input = QtWidgets.QLineEdit()
        self.api_key_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.api_key_input.setText(self.api_key)
        config_layout.addRow("OpenAI API Key:", self.api_key_input)

        self.microphone_select = QtWidgets.QComboBox()
        self.populate_microphones()
        config_layout.addRow("Select Microphone:", self.microphone_select)

        self.start_shortcut_input = QtWidgets.QKeySequenceEdit()
        self.start_shortcut_input.setKeySequence(self.start_shortcut)
        config_layout.addRow("Start Shortcut:", self.start_shortcut_input)

        self.stop_shortcut_input = QtWidgets.QKeySequenceEdit()
        self.stop_shortcut_input.setKeySequence(self.stop_shortcut)
        config_layout.addRow("Stop Shortcut:", self.stop_shortcut_input)

        save_button = QtWidgets.QPushButton("Save Settings")
        save_button.clicked.connect(self.save_settings)
        config_layout.addWidget(save_button)

        config_group.setLayout(config_layout)

        # Control widgets
        self.start_button = QtWidgets.QPushButton("Start Dictation")
        self.start_button.clicked.connect(self.start_dictation)
        self.stop_button = QtWidgets.QPushButton("Stop Dictation")
        self.stop_button.clicked.connect(self.stop_dictation)
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        control_group.setLayout(control_layout)

        # Add groups to main layout
        main_layout.addWidget(config_group)
        main_layout.addWidget(control_group)
        central_widget.setLayout(main_layout)

        # System Tray
        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_ComputerIcon))
        show_action = QtWidgets.QAction("Show", self)
        quit_action = QtWidgets.QAction("Exit", self)
        hide_action = QtWidgets.QAction("Hide", self)
        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(QtWidgets.QApplication.instance().quit)
        tray_menu = QtWidgets.QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def populate_microphones(self):
        # Placeholder for microphone selection
        self.microphone_select.addItem("Default Microphone")
        # You can populate with actual microphone devices available on the system

    def save_settings(self):
        # Save the API key securely
        settings.save_api_key(self.api_key_input.text())
        settings.save_microphone(self.microphone_select.currentText())
        settings.save_start_shortcut(self.start_shortcut_input.keySequence().toString())
        settings.save_stop_shortcut(self.stop_shortcut_input.keySequence().toString())
        QtWidgets.QMessageBox.information(self, "Settings", "Settings saved successfully.")

    def start_dictation(self):
        # Placeholder function for starting dictation
        QtWidgets.QMessageBox.information(self, "Dictation", "Dictation started.")

    def stop_dictation(self):
        # Placeholder function for stopping dictation
        QtWidgets.QMessageBox.information(self, "Dictation", "Dictation stopped.")

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Speech-to-Text Application",
            "Application was minimized to Tray",
            QtWidgets.QSystemTrayIcon.Information,
            2000
        )

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = SpeechToTextApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
```

### **2. Settings Management**

```python
# settings.py
import keyring
from keyrings.cryptfile.cryptfile import CryptFileKeyring
import os
import json

keyring.set_keyring(CryptFileKeyring())
keyring.get_keyring().keyring_key = "your_encryption_password"

CONFIG_FILE = 'config.json'

def get_api_key():
    api_key = keyring.get_password('openai', 'api_key')
    return api_key if api_key else ''

def save_api_key(api_key):
    keyring.set_password('openai', 'api_key', api_key)

def get_microphone():
    config = load_config()
    return config.get('microphone', '')

def save_microphone(microphone):
    config = load_config()
    config['microphone'] = microphone
    save_config(config)

def get_start_shortcut():
    config = load_config()
    return config.get('start_shortcut', '')

def save_start_shortcut(shortcut):
    config = load_config()
    config['start_shortcut'] = shortcut
    save_config(config)

def get_stop_shortcut():
    config = load_config()
    return config.get('stop_shortcut', '')

def save_stop_shortcut(shortcut):
    config = load_config()
    config['stop_shortcut'] = shortcut
    save_config(config)

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)
```

### **3. Audio Input Handling and OpenAI Whisper API Integration**

```python
# audio_transcriber.py
import pyaudio
import threading
import requests
import json
import settings

class AudioTranscriber:
    def __init__(self):
        self.api_key = settings.get_api_key()
        self.chunk = 1024  # Record in chunks of 1024 samples
        self.sample_format = pyaudio.paInt16  # 16 bits per sample
        self.channels = 1
        self.fs = 44100  # Record at 44100 samples per second
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.is_recording = False

    def start_recording(self):
        self.is_recording = True
        self.frames = []
        self.stream = self.p.open(format=self.sample_format,
                                  channels=self.channels,
                                  rate=self.fs,
                                  frames_per_buffer=self.chunk,
                                  input=True)
        threading.Thread(target=self.record).start()

    def stop_recording(self):
        self.is_recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()

    def record(self):
        while self.is_recording:
            data = self.stream.read(self.chunk, exception_on_overflow=False)
            self.frames.append(data)
            if len(self.frames) >= int(self.fs / self.chunk * 5):  # Send every 5 seconds
                self.send_to_api()
                self.frames = []

    def send_to_api(self):
        print("Sending audio data to API...")
        audio_data = b''.join(self.frames)
        headers = {
            'Authorization': f'Bearer {self.api_key}',
        }
        response = requests.post(
            'https://api.openai.com/v1/audio/transcriptions',
            headers=headers,
            files={'file': ('audio.wav', audio_data, 'audio/wav')},
            data={'model': 'whisper-1'},
        )
        if response.status_code == 200:
            text = response.json().get('text', '')
            print("Transcribed Text:", text)
            self.insert_text(text)
        else:
            print("API Error:", response.text)

    def insert_text(self, text):
        # Code to insert text into active application
        # This might require platform-specific implementations
        pass
```

### **4. Keyboard Shortcuts Handling**

```python
# shortcut_handler.py
import threading
import keyboard
import settings

class ShortcutHandler:
    def __init__(self, start_callback, stop_callback):
        self.start_shortcut = settings.get_start_shortcut()
        self.stop_shortcut = settings.get_stop_shortcut()
        self.start_callback = start_callback
        self.stop_callback = stop_callback
        self.running = True
        threading.Thread(target=self.listen_for_shortcuts).start()

    def listen_for_shortcuts(self):
        while self.running:
            if self.start_shortcut:
                keyboard.add_hotkey(self.start_shortcut, self.start_callback)
            if self.stop_shortcut:
                keyboard.add_hotkey(self.stop_shortcut, self.stop_callback)
            keyboard.wait()

    def stop(self):
        self.running = False
        keyboard.unhook_all()
```

### **5. Main Application Integration**

Update the `SpeechToTextApp` class in `gui.py` to integrate the `AudioTranscriber` and `ShortcutHandler`.

```python
# In gui.py, within the SpeechToTextApp class
from audio_transcriber import AudioTranscriber
from shortcut_handler import ShortcutHandler

class SpeechToTextApp(QtWidgets.QMainWindow):
    # ... [existing code] ...

    def init_ui(self):
        # ... [existing code] ...

        # Initialize AudioTranscriber and ShortcutHandler
        self.transcriber = AudioTranscriber()
        self.shortcut_handler = ShortcutHandler(self.start_dictation, self.stop_dictation)

    def save_settings(self):
        # ... [existing code] ...
        # Update shortcuts in ShortcutHandler
        self.shortcut_handler.start_shortcut = settings.get_start_shortcut()
        self.shortcut_handler.stop_shortcut = settings.get_stop_shortcut()

    def start_dictation(self):
        self.transcriber.start_recording()
        QtWidgets.QMessageBox.information(self, "Dictation", "Dictation started.")

    def stop_dictation(self):
        self.transcriber.stop_recording()
        QtWidgets.QMessageBox.information(self, "Dictation", "Dictation stopped.")

    def closeEvent(self, event):
        # ... [existing code] ...
        self.shortcut_handler.stop()
```

### **6. Text Input Integration**

Implement the `insert_text` method in `AudioTranscriber` to insert text into the active text field.

```python
# In audio_transcriber.py
import platform

    def insert_text(self, text):
        if platform.system() == 'Linux':
            from pynput.keyboard import Controller, Key
            keyboard = Controller()
            keyboard.type(text)
        else:
            print("Text insertion not implemented for this OS.")
```

### **Complete Application Files**

Ensure all the code snippets are saved in their respective files:

- `gui.py`
- `settings.py`
- `audio_transcriber.py`
- `shortcut_handler.py`

### **Running the Application**

Run the application using:

```bash
python gui.py
```

### **Notes**

- **Microphone Selection**: The `populate_microphones` method in `SpeechToTextApp` currently adds a placeholder. To list actual microphones, you can use `pyaudio` to enumerate available devices.

```python
def populate_microphones(self):
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if dev['maxInputChannels'] > 0:
            self.microphone_select.addItem(dev['name'])
    p.terminate()
```

- **Text Insertion**: The method provided uses `pynput` to simulate keyboard typing. Install it using `pip install pynput`.

- **Security**: The API key is stored securely using `keyring` with encryption provided by `CryptFileKeyring`. Make sure to set a strong encryption password.

- **Error Handling**: The code includes basic error handling. For production use, enhance it to handle exceptions and edge cases.

- **Dependencies**: Ensure all dependencies are installed:

```bash
pip install PyQt5 pyaudio requests keyboard pynput keyring cryptography
```

- **Global Keyboard Shortcuts**: The `keyboard` module requires root privileges on Linux to capture global shortcuts. Run the application with appropriate permissions or consider using alternative methods for handling shortcuts on Linux.

- **OpenAI Whisper API**: Replace `'https://api.openai.com/v1/audio/transcriptions'` with the correct endpoint if needed, and ensure your API key has the necessary permissions.

- **Testing**: Test each component individually to ensure it works as expected before integrating.

---

This implementation should meet the specified requirements and provide a solid foundation for further enhancements.