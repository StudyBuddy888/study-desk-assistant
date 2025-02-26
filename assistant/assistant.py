import pyttsx3
import speech_recognition as sr
import requests
import time
from pymongo import MongoClient
import os

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty("rate", 150)
engine.setProperty("volume", 1.0)

# MongoDB Atlas Connection
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["study_tracker"]

# DeepSeek API Key
DEEPSEEK_API_KEY = ""

def speak(text):
    """Convert text to speech"""
    print(f"Assistant: {text}")  # For debugging
    engine.say(text)
    engine.runAndWait()

def listen():
    """Listen for user input via microphone"""
    recognizer = sr.Recognizer()
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
        return ""

def deepseek_query(text):
    """Send user query to DeepSeek API"""
    url = "https://api.deepseek.com/v1/assistant"
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    data = {"input": text}
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json().get("output", "I couldn't process that.")
    return "Error in processing request."

def assistant():
    """Main voice assistant loop"""
    speak("Hello, how can I assist you today?")
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
