import speech_recognition as sr
import nltk
from nltk.tokenize import word_tokenize
import pygame
import os
import time
import threading
import keyboard  # For keypress detection
from transformers import pipeline
import pyttsx3  # Text-to-speech library

# Define the main music directory
MUSIC_PATH = r"C:\VibeSync\music"

# Emotion-based folder structure
EMOTION_FOLDERS = {
    "angry": "angry",
    "disgust": "disgust",
    "fear": "fear",
    "happy": "happy",
    "neutral": "neutral",
    "sad": "sad",
    "surprise": "surprise"
}

# Initialize recognizer
recognizer = sr.Recognizer()

# Load Hugging Face emotion classification model
emotion_pipeline = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    return_all_scores=True
)

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Event for skipping songs
skip_song = threading.Event()
current_index = 0  # Track current song index
current_songs = []
current_emotion = None

# Function to speak text
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to list available songs for a given emotion
def list_songs(emotion):
    folder_path = os.path.join(MUSIC_PATH, EMOTION_FOLDERS.get(emotion, ""))
    
    if not os.path.exists(folder_path):
        print(f"⚠️ No music folder found for {emotion}. Please check your path.")
        return []
    
    songs = [f for f in os.listdir(folder_path) if f.endswith((".mp3", ".wav"))]
    if not songs:
        print(f"⚠️ No songs found for {emotion}.")
        return []
    
    print(f"\n🎵 Songs available for {emotion}:")
    for index, song in enumerate(songs):
        letter_index = chr(97 + index)  # Convert to letters (a, b, c...)
        print(f"{index + 1}) {song}")  # Display numerical index starting from 1
    
    return songs

# Function to search for a song in all emotion folders
def find_song(song_name):
    for emotion, folder in EMOTION_FOLDERS.items():
        folder_path = os.path.join(MUSIC_PATH, folder)
        if os.path.exists(folder_path):
            for file in os.listdir(folder_path):
                if song_name.lower() in file.lower():
                    return os.path.join(folder_path, file)  # Return full path of song
    return None

# Function to play a single song
def play_song(song_path):
    print(f"🔍 Debug: Attempting to play song from path: {song_path}")  # Debug print
    pygame.mixer.init()
    try:
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play()
        print(f"\n🎵 Now playing: {os.path.basename(song_path)}")
    except pygame.error as e:
        print(f"⚠️ Error: {e}")

# Function to recognize speech
def recognize_speech():
    with sr.Microphone() as source:
        print("🎤 Listening... (Say 'play' followed by an index number or a song name)")
        recognizer.adjust_for_ambient_noise(source, duration=1)  # Reduce background noise
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
            command = recognizer.recognize_google(audio).lower()
            print(f"🗣 You said: {command}")
            return command
        except sr.WaitTimeoutError:
            print("⏳ Timeout! No speech detected.")
            return None
        except sr.UnknownValueError:
            print("❌ Could not understand audio.")
            return None
        except sr.RequestError:
            print("❌ Error with speech recognition service.")
            return None

# Function to detect emotion from text
def detect_emotion(command):
    tokens = word_tokenize(command.lower())
    for emotion in EMOTION_FOLDERS.keys():
        if emotion in tokens:
            return emotion
    return None

# Convert index number input to correct song
def index_to_song(index):
    if 1 <= index <= len(current_songs):  # Ensure valid range
        song_name = current_songs[index - 1]
        # Construct the full path to the song
        song_path = os.path.join(MUSIC_PATH, EMOTION_FOLDERS[current_emotion], song_name)
        print(f"🔍 Debug: Song path selected: {song_path}")  # Debug print
        return song_path
    else:
        print("⚠️ Invalid song selection! Index out of range.")
    return None

# Convert word number to digit
def word_to_index(word):
    word_map = {
        "first": 0, "second": 1, "third": 2, "fourth": 3, "fifth": 4,
        "sixth": 5, "seventh": 6, "eighth": 7, "ninth": 8, "tenth": 9,
        "eleventh": 10, "twelfth": 11, "thirteenth": 12, "fourteenth": 13,
        "fifteenth": 14, "sixteenth": 15, "seventeenth": 16, "eighteenth": 17,
        "nineteenth": 18, "twentieth": 19
    }
    return word_map.get(word.lower(), -1)  # Return -1 if not found

# Monitor key presses
def monitor_keys():
    global current_index, current_songs
    while True:
        if keyboard.is_pressed('n') and current_songs:
            current_index += 1
            if current_index >= len(current_songs):
                current_index = 0  # Restart from first song
            pygame.mixer.music.stop()
            print("\n⏭️ Playing next song...")
            time.sleep(0.5)
            play_song(current_songs[current_index])
        elif keyboard.is_pressed('q'):
            pygame.mixer.music.stop()
            print("\n👋 Exiting...")
            os._exit(0)

# Main function to handle user input
def main():
    global current_songs, current_emotion, current_index

    pygame.init()
    nltk.download('punkt')

    print("\n🎶 Welcome to VibeSync!")
    print("💡 Say 'next' to play next song | Say 'exit' to quit\n")

    # Voice chatbot asks for mood
    speak("Hi! How are you feeling today? Please say your mood.")
    
    while True:
        print("🎤 Say your mood, song name, or 'play' followed by an index number or a song name.")
        command = recognize_speech()
        
        if not command:
            print("⏳ No command detected, please speak again.")
            continue

        # Exit condition
        if "exit" in command:
            print("👋 Exiting program...")
            break

        # Skip to next song
        elif "next" in command and current_songs:
            current_index = (current_index + 1) % len(current_songs)
            pygame.mixer.music.stop()
            print("\n⏭️ Playing next song...")
            play_song(os.path.join(MUSIC_PATH, EMOTION_FOLDERS[current_emotion], current_songs[current_index]))
            continue

        # Play specific song by letter index
        if command.startswith("play"):
            parts = command.split()
            if len(parts) > 1:
                selection = parts[1]
                
                # 🎯 If user says "play 1", "play 2", convert to index
                if selection.isdigit():
                    index = int(selection)
                    song_path = index_to_song(index)
                    
                    if song_path:
                        play_song(song_path)
                        continue
                    else:
                        print("⚠️ Invalid selection! Try again.")
                        continue

                # 🎯 If user says "play [song name]", find the song and play
                else:
                    song_path = find_song(selection)
                    if song_path:
                        current_songs = [song_path]
                        current_index = 0
                        play_song(song_path)
                        continue
                    else:
                        print("⚠️ Song not found! Try again.")
                        continue

        # Convert word number to index if user says "play one"
        if "play" in command:
            parts = command.split()
            if len(parts) > 1:
                selection = parts[1]
                # Convert word to index if it's a word like "one", "two", etc.
                index = word_to_index(selection)
                if index != -1:
                    song_path = index_to_song(index)
                    if song_path:
                        play_song(song_path)
                        continue
                    else:
                        print("⚠️ Invalid selection! Try again.")
                        continue

        # Detect emotion or search for songs
        detected_emotion = detect_emotion(command)
        current_emotion = detected_emotion if detected_emotion else "neutral"  # Set to neutral if no emotion detected
        
        if current_emotion:  # Ensure we only list songs if emotion is detected
            current_songs = list_songs(current_emotion)
        
        if not current_songs:
            continue

if __name__ == "__main__":
    main()