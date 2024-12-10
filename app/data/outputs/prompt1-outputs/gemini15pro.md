# Gemini 1.5 Pro Via Google AI Studio

```python
import os
import sys
import keyring
import pyaudio
import openai
import keyboard
import threading
import pyperclip

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QComboBox, QSystemTrayIcon, QMenu, QAction)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize, Qt

CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100


class WhisperApp(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Whisper Transcriber")
        self.setWindowIcon(QIcon.fromTheme("microphone"))  # Or provide a path to an icon file

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon.fromTheme("microphone"))  # Same icon as window
        self.tray_icon.activated.connect(self.show)  # Click to show/hide

        tray_menu = QMenu()
        show_action = QAction("Show/Hide", tray_menu)
        show_action.triggered.connect(self.toggle_visibility)
        tray_menu.addAction(show_action)
        exit_action = QAction("Exit", tray_menu)
        exit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(exit_action)
        self.tray_icon.setContextMenu(tray_menu)

        self.tray_icon.show()

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # API Key
        api_key_layout = QHBoxLayout()
        api_key_label = QLabel("OpenAI API Key:")
        self.api_key_input = QLineEdit()
        api_key_layout.addWidget(api_key_label)
        api_key_layout.addWidget(self.api_key_input)
        layout.addLayout(api_key_layout)
        self.api_key_input.textChanged.connect(self.save_api_key)
        self.load_api_key() #Load API Key


        # Microphone Selection
        mic_layout = QHBoxLayout()
        mic_label = QLabel("Microphone:")
        self.mic_combo = QComboBox()
        mic_layout.addWidget(mic_label)
        mic_layout.addWidget(self.mic_combo)
        layout.addLayout(mic_layout)
        self.populate_mics()


        # Start/Stop Buttons
        buttons_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Dictation")
        self.stop_button = QPushButton("Stop Dictation")
        self.stop_button.setEnabled(False)  # Initially disabled
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.stop_button)
        layout.addLayout(buttons_layout)
        self.start_button.clicked.connect(self.start_dictation)
        self.stop_button.clicked.connect(self.stop_dictation)



        self.p = pyaudio.PyAudio()
        self.stream = None
        self.is_recording = False

        self.start_shortcut = "ctrl+alt+s" # Default
        self.stop_shortcut = "ctrl+alt+x"  # Default

        keyboard.add_hotkey(self.start_shortcut, self.start_dictation)
        keyboard.add_hotkey(self.stop_shortcut, self.stop_dictation)


    def populate_mics(self):
        info = self.p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        for i in range(0, numdevices):
                if (self.p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                    self.mic_combo.addItem(self.p.get_device_info_by_host_api_device_index(0, i).get('name'))



    def save_api_key(self, text):
        keyring.set_password("whisper-transcriber", "api_key", text)


    def load_api_key(self):
        api_key = keyring.get_password("whisper-transcriber", "api_key")
        if api_key:
            self.api_key_input.setText(api_key)
            openai.api_key = api_key




    def start_dictation(self):
        if not self.api_key_input.text():  # Check for API key before starting
            return  # Or display an error message


        self.is_recording = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        try:
            selected_mic_index = self.mic_combo.currentIndex()  # Implement logic to store and use selected microphone index
            self.stream = self.p.open(format=FORMAT,
                                    channels=CHANNELS,
                                    rate=RATE,
                                    input=True,
                                    input_device_index=selected_mic_index,  # Use the selected mic
                                    frames_per_buffer=CHUNK_SIZE)


            self.recording_thread = threading.Thread(target=self.record_audio)
            self.recording_thread.start()


        except OSError as e:
            print(f"Error opening microphone: {e}")  # Handle errors appropriately
            self.is_recording = False
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)

    def stop_dictation(self):
        self.is_recording = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()


    def record_audio(self):
        while self.is_recording:
            try:
                audio_data = self.stream.read(CHUNK_SIZE)
                transcript = self.transcribe_audio(audio_data)
                if transcript:
                    self.insert_text(transcript)


            except Exception as e:  # Catch and handle potential errors during recording
                print(f"Error during recording: {e}")
                break # Exit the loop if an error occurs



    def transcribe_audio(self, audio_data):
        try:
            response = openai.Audio.transcribe("whisper-1", audio_data)
            return response['text']
        except openai.error.OpenAIError as e:
            print(f"OpenAI API Error: {e}")
            return None # Handle API errors appropriately


    def insert_text(self, text):
        pyperclip.copy(text) # Copy to clipboard
        keyboard.send('ctrl+v')  # Paste from clipboard



    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def closeEvent(self, event):  # Override closeEvent to minimize to tray
        event.ignore()
        self.hide()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WhisperApp()
    window.show()
    sys.exit(app.exec())

```


Key improvements and explanations in this version:

* **PyQt6 for GUI:** Uses PyQt6, a powerful and cross-platform GUI toolkit, for a more modern and visually appealing interface.

* **System Tray Integration:**  Implements system tray functionality (minimize to tray, context menu).

* **Microphone Selection:**  Includes a dropdown for selecting the microphone, utilizing `pyaudio` to get available devices.

* **API Key Security:**  Securely stores the API key using `keyring`.

* **Error Handling:** Includes more robust error handling to catch potential issues during recording and API calls.

* **Clearer Code Structure:** The code is better organized and more readable, using descriptive variable names and comments.

* **Threading:**  Uses a separate thread for recording and transcribing to prevent GUI freezes.


**Installation (on OpenSUSE):**

1. **Install Python and pip:**  Make sure Python and pip are installed.
2. **Install required libraries:**
   ```bash
   pip install pyqt6 pyaudio openai keyboard pyperclip keyring
   ```
3. **Install OpenAI Python Library:**
    ```bash
    pip install openai
    ```


Remember to replace the placeholder comments with the appropriate error handling and microphone persistence logic. This refined version offers a much more robust and user-friendly experience.  The use of PyQt6 significantly enhances the visual appeal compared to Tkinter.