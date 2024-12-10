# Meta Llama 3.3 70B Instruct (Via Hugging Face Chat)

Below is a basic implementation of the speech-to-text application using PyQt for the GUI, PyAudio for handling audio input, and the OpenAI Whisper API for speech-to-text transcription.

### Installation

To run this code, you need to install the following packages:
```bash
pip install PyQt5 pyaudio requests keyboard keyring
```
You also need to install the OpenAI Whisper API library:
```bash
pip install openai
```
### Code

#### Main Application

```python
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox, QPushButton, QLineEdit, QSystemTrayIcon, QMenu
from PyQt5.QtCore import Qt
import pyaudio
import threading
import requests
import keyboard
import keyring
from openai import Whisper

class SpeechToTextApp(QWidget):
    def __init__(self):
        super().__init__()

        self.api_key = self.load_api_key()
        self.microphone_index = self.load_microphone_index()
        self.start_shortcut = self.load_start_shortcut()
        self.stop_shortcut = self.load_stop_shortcut()

        self.init_ui()

    def init_ui(self):
        self.setGeometry(100, 100, 300, 200)
        self.layout = QVBoxLayout()

        self.api_key_input = QLineEdit()
        self.api_key_input.setText(self.api_key)
        self.layout.addWidget(self.api_key_input)

        self.microphone_combo = QComboBox()
        self.microphone_combo.addItems(self.get_microphone_list())
        self.microphone_combo.setCurrentIndex(self.microphone_index)
        self.layout.addWidget(self.microphone_combo)

        self.start_button = QPushButton("Start Dictation")
        self.start_button.clicked.connect(self.start_dictation)
        self.layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Dictation")
        self.stop_button.clicked.connect(self.stop_dictation)
        self.stop_button.setEnabled(False)
        self.layout.addWidget(self.stop_button)

        self.setLayout(self.layout)

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(self.style().SP_DesktopIcon))
        self.tray_icon.menu = QMenu()
        self.tray_icon.menu.addAction("Show", self.show)
        self.tray_icon.menu.addAction("Hide", self.hide)
        self.tray_icon.setContextMenu(self.tray_icon.menu)

    def get_microphone_list(self):
        p = pyaudio.PyAudio()
        microphone_list = []
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            if dev['maxInputChannels'] > 0:
                microphone_list.append(dev['name'])
        p.terminate()
        return microphone_list

    def load_api_key(self):
        return keyring.get_password("speech_to_text", "api_key") or ""

    def load_microphone_index(self):
        try:
            with open("microphone_index.txt", "r") as f:
                return int(f.read())
        except FileNotFoundError:
            return 0

    def load_start_shortcut(self):
        try:
            with open("start_shortcut.txt", "r") as f:
                return f.read()
        except FileNotFoundError:
            return "ctrl+shift+s"

    def load_stop_shortcut(self):
        try:
            with open("stop_shortcut.txt", "r") as f:
                return f.read()
        except FileNotFoundError:
            return "ctrl+shift+t"

    def start_dictation(self):
        self.api_key = self.api_key_input.text()
        keyring.set_password("speech_to_text", "api_key", self.api_key)
        self.microphone_index = self.microphone_combo.currentIndex()
        with open("microphone_index.txt", "w") as f:
            f.write(str(self.microphone_index))

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        self.dictation_thread = threading.Thread(target=self.dictation_loop)
        self.dictation_thread.start()

        keyboard.add_hotkey(self.start_shortcut, self.start_dictation)
        keyboard.add_hotkey(self.stop_shortcut, self.stop_dictation)

    def stop_dictation(self):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

        keyboard.unhook_all()

    def dictation_loop(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)

        while self.stop_button.isEnabled():
            audio = stream.read(1024)
            if audio:
                response = requests.post(
                    "https://api.openai.com/v1/whisper/transcribe",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={"audio": audio, "model": "whisper-1"}
                )
                if response.status_code == 200:
                    transcription = response.json()["text"]
                    keyboard.write(transcription)

        stream.stop_stream()
        stream.close()        
        p.terminate()

def main():
    app = QApplication(sys.argv)
    ex = SpeechToTextApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
```

### Explanation

This code creates a GUI application with a configuration section for inputting the OpenAI API key, selecting the microphone, and starting/stopping dictation. The application uses the OpenAI Whisper API for speech-to-text transcription and keyboard shortcuts for starting and stopping dictation.

The `SpeechToTextApp` class initializes the GUI and sets up the event handlers for the buttons and keyboard shortcuts. The `start_dictation` method starts the dictation loop, which captures audio from the selected microphone, sends it to the OpenAI Whisper API, and inserts the transcribed text into the currently active text field. The `stop_dictation` method stops the dictation loop and unregisters the keyboard shortcuts.

The `dictation_loop` method runs in a separate thread to avoid blocking the GUI thread. It uses the PyAudio library to capture audio from the microphone and the requests library to send the audio to the OpenAI Whisper API.

Note that this code requires the OpenAI API key to be stored securely using the keyring library. You can modify the code to use a different method for storing the API key.

Also, this code uses the `keyboard` library to handle global keyboard shortcuts. You may need to modify the code to use a different library or approach depending on your specific requirements.

### Example Use Case

1. Run the application and input your OpenAI API key in the configuration section.
2. Select the microphone you want to use for dictation.
3. Click the "Start Dictation" button or press the keyboard shortcut (default is Ctrl+Shift+S) to start dictation.
4. Speak into the microphone, and the transcribed text will be inserted into the currently active text field.
5. Click the "Stop Dictation" button or press the keyboard shortcut (default is Ctrl+Shift+T) to stop dictation.

Note that this code is a basic implementation and may require modifications to suit your specific requirements. You may need to add error handling, improve the GUI, or modify the dictation loop to suit your needs.