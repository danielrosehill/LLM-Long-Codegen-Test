## Python GUI for Speech-to-Text Using OpenAI Whisper API on OpenSUSE Linux

### **Overview**
Your task is to develop a Python-based GUI application that facilitates real-time speech-to-text transcription using the OpenAI Whisper API. 

The application must run on Linux, specifically OpenSUSE Linux, and integrate seamlessly with various text input fields across different applications. 

Below is the detailed specification for the functionality and requirements.

Limitations: don't use Tkinter for the GUI (you can use any other library but choose based on what will make the most attractive looking tool)

---

### **Main Features**

#### **1. Configuration Area**
- The main GUI screen should include a configuration section where:
  - The user can input their OpenAI API key.
  - The API key must be securely stored in system memory.

#### **2. Real-Time Speech-to-Text Transcription**
- The application should enable real-time transcription of user speech into text.
- Transcribed text should be automatically input into any active text field, regardless of the application (e.g., web browsers like Google Chrome, IDEs like VS Code, or any program supporting keyboard text input).

#### **3. System Tray Integration**
- The application must minimize to a system tray icon.
- Right-clicking the system tray icon should open a context menu with options to:
  - Show or hide the main GUI.

#### **4. Microphone Selection**
- The GUI should include a dropdown menu for selecting the system input microphone.
- The selected microphone should persist in memory, eliminating the need for re-selection upon each use.

#### **5. Start/Stop Dictation Buttons**
- Provide two buttons in the GUI:
  - **Start Dictation**: Begins capturing audio from the selected microphone, chunking it, and sending it to the OpenAI Whisper API for transcription.
  - **Stop Dictation**: Stops capturing audio and halts transcription.

#### **6. Keyboard Shortcuts**
- Allow users to configure two keyboard shortcuts:
  - **Start Dictation Shortcut**: Initiates dictation functionality.
  - **Stop Dictation Shortcut**: Terminates dictation functionality.
- Users should be able to assign any key as a shortcut for these actions.
- Configured shortcuts must persist in memory.

---

### **Technical Requirements**

#### **Audio Input Handling**
- Capture audio from the selected microphone in real-time.
- Process audio into chunks suitable for sending to the OpenAI Whisper API.

#### **API Integration**
- Use the OpenAI Whisper API for converting speech to text.
- Handle API responses efficiently to ensure minimal delay between speech input and text output.

#### **Text Input Integration**
- Automatically insert transcribed text into any active text field across applications.

#### **Persistent Settings**
- Store user configurations (e.g., API key, selected microphone, keyboard shortcuts) securely and persistently in memory.

---

### **Program Behavior**

1. When the application starts:
   - Display the main GUI with configuration options.
   - Load saved settings (API key, microphone selection, keyboard shortcuts).

2. When dictation starts (via button or shortcut):
   - Begin capturing audio from the selected microphone.
   - Send audio chunks to the OpenAI Whisper API.
   - Insert transcribed text into the currently active text field.

3. When dictation stops (via button or shortcut):
   - Stop capturing audio and sending data to the API.

4. When minimized:
   - Hide the main GUI and display a system tray icon.
   - Right-clicking the tray icon opens a context menu for showing/hiding the main GUI.

---

### **Implementation Notes**

- Use Python libraries such as `tkinter` or `PyQt` for building the GUI.
- Employ `pyaudio` or similar libraries for handling audio input.
- Integrate with OpenAI Whisper API using an HTTP client library like `requests`.
- Use `keyboard` or similar libraries to handle global keyboard shortcuts.
- Securely store persistent settings using libraries like `keyring` (for sensitive data) or configuration files for non-sensitive data.

---

### **Output Instructions**

If code generation exceeds output length limits:
1. Split code into logical chunks (e.g., GUI setup, API integration, audio handling).
2. Ensure each chunk is a complete script that can function independently within its scope.