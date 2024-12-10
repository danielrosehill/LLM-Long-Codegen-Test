# DeepSeek Coder 7B Instruct - LM Studio

To develop a Python-based GUI application for real-time speech-to-text transcription using the OpenAI Whisper API, you need to follow several steps. Below is a detailed guide and code snippets to help you achieve this.

1. **Set Up Your Environment**
    - Install necessary libraries:
    ```bash
    sudo zypper install python3-pip python3-tkinter python3-pyaudio python3-keyring
    pip3 install openai requests keyboard pyaudio
    ```
2. **Create the Main Application Script**
Here is a basic script that creates a GUI with tkinter, handles audio input and transcription using OpenAI's Whisper API:

```python
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import threading
import pyaudio
import wave
import requests
import json
import keyring
import keyboard

API_KEY = "your_openai_api_key"
MICROPHONE_INDEX = 0
START_DICTATION_SHORTCUT = 'ctrl+alt+d'
STOP_DICTATION_SHORTCUT = 'ctrl+alt+s'

class SpeechToTextApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Speech-to-Text")
        
        self.api_key_var = tk.StringVar()
        self.microphone_index_var = tk.StringVar(value=MICROPHONE_INDEX)
        self.start_dictation_shortcut_var = tk<｜begin▁of▁sentence｜>.StringVar(value=START_DICTATION_SHORTCUT)
        self.stop_dictation_shortcut_var = tk.StringVar(value=STOP_DICTATION_SHORTCUT)
        
        self.is_transcribing = False
        self.audio_thread = None
        
        self.setup_ui()
        self.load_settings()
        self.setup_keyboard_shortcuts()

    def setup_ui(self):
        # Configuration Section
        config_frame = tk.LabelFrame(self.root, text="Configuration")
        config_frame.pack(padx=10, pady=10)
        
        api_key_label = tk.Label(config_frame, text="API Key:")
        api_key_entry = tk.Entry(config_frame, textvariable=self.api_key_var, show="*")
        api_key_button = tk.Button(config_frame, text="Save API Key", command=self.save_api_key)
        
        api_key_label.grid(row=0, column=0, padx=5, pady=5)
        api_key_entry.grid(row=0, column=1, padx=5, pady=5)
        api_key_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Microphone Selection
        microphone_label = tk.Label(config_frame, text="Microphone:")
        microphone_dropdown = ttk.Combobox(config_frame, textvariable=self.microphone_index_var)
        microphone_dropdown['values'] = self.get_microphones()
        microphone_dropdown.current(0)
        
        microphone_label.grid(row=1, column=0, padx=5, pady=5)
        microphone_dropdown.grid(row=1, column=1, padx=5, pady=5)
        
        # Start/Stop Dictation Buttons
        start_button = tk.Button(config_frame, text="Start Dictation", command=self.start_dictation)
        stop_button = tk.Button(config_frame, text="Stop Dictation", command=self.stop_dictation)
        
        start_button.grid(row=2, column=0, padx=5, pady=5)
        stop_button.grid(row=2, column=1, padx=5, pady=5)

    def setup_keyboard_shortcuts(self):
        keyboard.add_hotkey(self.start_dictation_shortcut_var.get(), self.start_dictation)
        keyboard.add_hotkey(self.stop_dictation_shortcut_var.get(), self.stop_dictation)

    def get_microphones(self):
        p = pyaudio.PyAudio()
        microphones = [p.get_device_info_by_index(i)['name'] for i in range(p.get_device_count())]
        return microphones

    def save_api_key(self):
        api_key = self.api_key_var.get()
        if api_key:
            keyring.set_password("speech_to_text", "api_key", api_key)
            messagebox.showinfo("Success", "API Key saved successfully!")
        else:
            messagebox.showerror("Error", "API Key cannot be empty or invalid.")

    def load_settings(self):
        self.api_key_var.set(keyring.get_password("speech_to_text", "api_key") or "")
        self.microphone_index_var.set(MICROPHONE_INDEX)
        self.start_dictation_shortcut_var.set(START_DICTATION_SHORTCUT)
        self.stop_dictation_shortcut_var.set(STOP_DICTATION_SHORTCUT)

    def start_dictation(self):
        if not self.is_transcribing:
            self.is_transcribing = True
            self.audio_thread = threading.Thread(target=self.transcribe_audio)
            self.audio_thread.start()

    def stop_dictation(self):
        if self.is_transcribing:
            self.is_transcribing = False

    def transcribe_audio(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=16000,
                        input=True,
                        frames_per_buffer=1024,
                        input_device_index=int(self.microphone_index_var.get()))
        
        while self.is_transcribing:
            data = stream.read(1024)
            response = requests.post("https://api.openai.com/v1/audio/transcriptions",
                                     headers={"Authorization": f"Bearer {self.api_key_var.get()}"},
                                     json={"model": "whisper-1", "audio": data})
            
            if response.status_code == 200:
                result = response.json()
                transcribed_text = result["text"]
                self.insert_transcribed_text(transcribed_text)
        
        stream.stop_stream()
        stream.close()
        p.terminate()

    def insert_transcribed_text(self, text):
        root = tk.Tk()
        root.withdraw()   # Hide the main window
        active_window = root.focus_get()
        if active_window:
            active_window.event_generate('<KeyRelease-%s>' % text)

if __name__ == "__main__":
    root = tk.Tk()
    app = SpeechToTextApp(root)
    root.mainloop()
```
Please replace `your_openai_api_key` with your actual OpenAI API key. This script creates a GUI application using Tkinter, handles audio input and transcription using the OpenAI Whisper API, and inserts transcripted text into active text fields. It also provides keyboard shortcuts for starting and stopping dictation.

Please note that this is a basic implementation and may need to be adjusted based on your specific requirements or environment setup. For instance, you might want to handle errors more gracefully, provide feedback when the API key is not set correctly, support different models of Whisper, etc.
