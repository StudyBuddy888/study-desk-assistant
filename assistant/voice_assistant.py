import pyttsx3
import speech_recognition as sr
from deepseek_api import deepseek_query
import time

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty("rate", 150)
engine.setProperty("volume", 1.0)

def speak(text):
    """Convert text to speech"""
    print(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    """Listen for user input via microphone"""
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            try:
                audio = recognizer.listen(source, timeout=10)
                command = recognizer.recognize_google(audio).lower()
                print(f"User said: {command}")
                return command
            except sr.UnknownValueError:
                speak("Sorry, I didn't catch that. Can you repeat?")
            except sr.RequestError:
                speak("Speech service is unavailable at the moment.")
    except OSError:
        print("❌ Error: No microphone detected!")
        return ""
    
    return ""

def assistant():
    """Main voice assistant loop"""
    speak("Hello! How can I assist you today?")

    while True:
        command = listen()
        if command:
            if "exit" in command or "stop" in command:
                speak("Goodbye! Have a productive day!")
                break
            else:
                response = deepseek_query(command)
                speak(response)

if __name__ == "__main__":
    assistant()
