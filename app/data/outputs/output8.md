# Le Chat By Mistral

Sure, let's break down the implementation into logical chunks. We'll start with the GUI setup using `PyQt5`, followed by audio handling, API integration, and finally, system tray integration and keyboard shortcuts.

### **1. GUI Setup using PyQt5**

First, let's set up the main GUI with configuration options, microphone selection, and start/stop dictation buttons.

```python
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import pyaudio
import wave
import requests
import json
import keyboard
import keyring

class SpeechToTextApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Speech-to-Text App')
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        # API Key Input
        self.api_key_label = QLabel('OpenAI API Key:')
        self.api_key_input = QLineEdit()
        layout.addWidget(self.api_key_label)
        layout.addWidget(self.api_key_input)

        # Microphone Selection
        self.mic_label = QLabel('Select Microphone:')
        self.mic_dropdown = QComboBox()
        self.populate_microphones()
        layout.addWidget(self.mic_label)
        layout.addWidget(self.mic_dropdown)

        # Start/Stop Dictation Buttons
        self.start_button = QPushButton('Start Dictation')
        self.stop_button = QPushButton('Stop Dictation')
        self.start_button.clicked.connect(self.start_dictation)
        self.stop_button.clicked.connect(self.stop_dictation)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)

        self.setLayout(layout)

        # System Tray
        self.tray_icon = QSystemTrayIcon(QIcon('icon.png'), self)
        self.tray_icon.setToolTip('Speech-to-Text App')
        self.tray_icon.show()

        self.tray_menu = QMenu()
        self.show_action = QAction('Show', self)
        self.hide_action = QAction('Hide', self)
        self.quit_action = QAction('Quit', self)
        self.show_action.triggered.connect(self.show)
        self.hide_action.triggered.connect(self.hide)
        self.quit_action.triggered.connect(QApplication.instance().quit)
        self.tray_menu.addAction(self.show_action)
        self.tray_menu.addAction(self.hide_action)
        self.tray_menu.addAction(self.quit_action)
        self.tray_icon.setContextMenu(self.tray_menu)

    def populate_microphones(self):
        p = pyaudio.PyAudio()
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                self.mic_dropdown.addItem(info['name'])

    def start_dictation(self):
        print("Dictation started")
        # Implement audio capture and API integration here

    def stop_dictation(self):
        print("Dictation stopped")
        # Implement stopping audio capture here

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            'Speech-to-Text App',
            'Application was minimized to Tray',
            QSystemTrayIcon.Information,
            2000
        )

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SpeechToTextApp()
    ex.show()
    sys.exit(app.exec_())
```

### **2. Audio Handling**

Next, let's handle audio input using `pyaudio` and send it to the OpenAI Whisper API.

```python
import threading

class AudioHandler:
    def __init__(self, api_key, microphone_index):
        self.api_key = api_key
        self.microphone_index = microphone_index
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.is_listening = False

    def start_listening(self):
        self.is_listening = True
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=16000,
                                  input=True,
                                  input_device_index=self.microphone_index,
                                  frames_per_buffer=1024,
                                  stream_callback=self.callback)
        self.stream.start_stream()

    def stop_listening(self):
        self.is_listening = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()

    def callback(self, in_data, frame_count, time_info, status):
        if self.is_listening:
            threading.Thread(target=self.send_to_api, args=(in_data,)).start()
        return (in_data, pyaudio.paContinue)

    def send_to_api(self, audio_data):
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        response = requests.post('https://api.openai.com/v1/audio/transcriptions',
                                 headers=headers,
                                 data=json.dumps({'audio': audio_data}))
        if response.status_code == 200:
            transcription = response.json().get('text', '')
            self.insert_text(transcription)

    def insert_text(self, text):
        # Implement text insertion into active text field here
        pass
```

### **3. System Tray Integration and Keyboard Shortcuts**

Finally, let's integrate system tray functionality and keyboard shortcuts.

```python
class SpeechToTextApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.audio_handler = None
        self.load_settings()

    def initUI(self):
        # Existing initUI code...

        # Keyboard Shortcuts
        self.start_shortcut = keyboard.add_hotkey('ctrl+shift+s', self.start_dictation)
        self.stop_shortcut = keyboard.add_hotkey('ctrl+shift+x', self.stop_dictation)

    def start_dictation(self):
        api_key = self.api_key_input.text()
        microphone_index = self.mic_dropdown.currentIndex()
        self.audio_handler = AudioHandler(api_key, microphone_index)
        self.audio_handler.start_listening()

    def stop_dictation(self):
        if self.audio_handler:
            self.audio_handler.stop_listening()

    def load_settings(self):
        api_key = keyring.get_password('speech_to_text_app', 'api_key')
        if api_key:
            self.api_key_input.setText(api_key)
        # Load other settings like microphone index and shortcuts

    def save_settings(self):
        api_key = self.api_key_input.text()
        keyring.set_password('speech_to_text_app', 'api_key', api_key)
        # Save other settings like microphone index and shortcuts

    def closeEvent(self, event):
        self.save_settings()
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            'Speech-to-Text App',
            'Application was minimized to Tray',
            QSystemTrayIcon.Information,
            2000
        )
```

### **4. Text Input Integration**

To insert transcribed text into any active text field, you can use libraries like `pyautogui` or `pyperclip`.

```python
import pyperclip
import pyautogui

class AudioHandler:
    # Existing AudioHandler code...

    def insert_text(self, text):
        pyperclip.copy(text)
        pyautogui.hotkey('ctrl', 'v')
```

### **Conclusion**

This implementation provides a basic structure for the speech-to-text application. You can further enhance it by adding error handling, improving the UI, and optimizing performance. Make sure to test the application thoroughly on OpenSUSE Linux to ensure compatibility and functionality.