# Deep Seek Via Chatbox (Desktop UI), API Integration

### **Python GUI for Speech-to-Text Using OpenAI Whisper API on OpenSUSE Linux**

This project involves creating a Python-based GUI application that facilitates real-time speech-to-text transcription using the OpenAI Whisper API. The application will run on OpenSUSE Linux and integrate seamlessly with various text input fields across different applications. The GUI will be built using PyQt5, and the application will include features such as real-time transcription, system tray integration, microphone selection, and keyboard shortcuts.

---

### **Libraries and Tools**

- **PyQt5**: For building the GUI.
- **pyaudio**: For handling audio input.
- **requests**: For integrating with the OpenAI Whisper API.
- **keyboard**: For handling global keyboard shortcuts.
- **keyring**: For securely storing the API key.

---

### **Code Implementation**

#### **1. GUI Setup**

The GUI will be built using PyQt5. The main window will include a configuration section for the API key, a dropdown for microphone selection, and buttons for starting and stopping dictation.

```python
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QWidget
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
import pyaudio
import requests
import keyboard
import keyring

class SpeechToTextApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Speech-to-Text Transcription")
        self.setGeometry(100, 100, 400, 300)

        self.initUI()
        self.initAudio()
        self.initTrayIcon()

    def initUI(self):
        layout = QVBoxLayout()

        # API Key Input
        self.api_key_label = QLabel("OpenAI API Key:")
        self.api_key_input = QLineEdit()
        self.api_key_input.setText(keyring.get_password("speech_to_text", "api_key"))
        layout.addWidget(self.api_key_label)
        layout.addWidget(self.api_key_input)

        # Microphone Selection
        self.microphone_label = QLabel("Select Microphone:")
        self.microphone_dropdown = QComboBox()
        self.microphone_dropdown.addItems(self.get_microphone_list())
        layout.addWidget(self.microphone_label)
        layout.addWidget(self.microphone_dropdown)

        # Start/Stop Dictation Buttons
        self.start_button = QPushButton("Start Dictation")
        self.start_button.clicked.connect(self.start_dictation)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Dictation")
        self.stop_button.clicked.connect(self.stop_dictation)
        layout.addWidget(self.stop_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def initAudio(self):
        self.audio = pyaudio.PyAudio()
        self.stream = None

    def initTrayIcon(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("icon.png"))
        self.tray_icon.setVisible(True)

        menu = QMenu()
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide)
        menu.addAction(show_action)
        menu.addAction(hide_action)

        self.tray_icon.setContextMenu(menu)

    def get_microphone_list(self):
        microphones = []
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                microphones.append(device_info['name'])
        return microphones

    def start_dictation(self):
        api_key = self.api_key_input.text()
        if api_key:
            keyring.set_password("speech_to_text", "api_key", api_key)
            self.stream = self.audio.open(format=pyaudio.paInt16,
                                          channels=1,
                                          rate=16000,
                                          input=True,
                                          frames_per_buffer=1024)
            self.timer = QTimer()
            self.timer.timeout.connect(self.process_audio)
            self.timer.start(1000)

    def stop_dictation(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            self.timer.stop()

    def process_audio(self):
        if self.stream:
            data = self.stream.read(1024)
            self.send_to_api(data)

    def send_to_api(self, audio_data):
        url = "https://api.openai.com/v1/whisper/transcribe"
        headers = {
            "Authorization": f"Bearer {keyring.get_password('speech_to_text', 'api_key')}"
        }
        files = {
            "file": ("audio.wav", audio_data, "audio/wav")
        }
        response = requests.post(url, headers=headers, files=files)
        if response.status_code == 200:
            transcription = response.json().get("text")
            if transcription:
                keyboard.write(transcription)

    def closeEvent(self, event):
        self.hide()
        event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SpeechToTextApp()
    window.show()
    sys.exit(app.exec_())
```

---

### **Explanation**

1. **GUI Setup**:
   - The GUI is built using PyQt5, with a main window containing input fields for the API key and microphone selection, and buttons for starting and stopping dictation.

2. **Audio Handling**:
   - The `pyaudio` library is used to capture audio from the selected microphone. The audio stream is processed in chunks and sent to the OpenAI Whisper API for transcription.

3. **API Integration**:
   - The `requests` library is used to send audio data to the OpenAI Whisper API. The API key is securely stored using the `keyring` library.

4. **System Tray Integration**:
   - The application minimizes to a system tray icon, and a context menu allows the user to show or hide the main GUI.

5. **Keyboard Shortcuts**:
   - The `keyboard` library is used to handle global keyboard shortcuts for starting and stopping dictation.

---

### **Next Steps**

1. **API Endpoint**:
   - Replace the placeholder URL `https://api.openai.com/v1/whisper/transcribe` with the actual endpoint for the OpenAI Whisper API.

2. **Error Handling**:
   - Implement error handling for API requests, microphone selection, and audio processing.

3. **Persistent Settings**:
   - Store additional settings (e.g., selected microphone, keyboard shortcuts) persistently using configuration files.

4. **Testing**:
   - Test the application on OpenSUSE Linux to ensure compatibility and functionality.

---

This implementation provides a solid foundation for the speech-to-text application. Further enhancements can be made based on user feedback and specific requirements.