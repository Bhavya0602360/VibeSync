import speech_recognition as sr
import nltk
from nltk.tokenize import word_tokenize
import pygame
import os
import time
import threading
import keyboard
from transformers import pipeline

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

# Globals
current_index = 0
current_songs = []
current_emotion = None

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
        print(f"{index + 1}. {song}")
    
    return songs

# Function to get full path of a song by emotion and filename
def get_song_path(emotion, filename):
    return os.path.join(MUSIC_PATH, EMOTION_FOLDERS[emotion], filename)

# Function to find a song across all folders
def find_song(song_name):
    for emotion, folder in EMOTION_FOLDERS.items():
        folder_path = os.path.join(MUSIC_PATH, folder)
        if os.path.exists(folder_path):
            for file in os.listdir(folder_path):
                if file.lower() == song_name.lower():
                    return os.path.join(folder_path, file)
    return None

# Function to play a single song
def play_song(song_path):
    pygame.mixer.init()
    pygame.mixer.music.load(song_path)
    pygame.mixer.music.play()
    print(f"\n🎵 Now playing: {os.path.basename(song_path)}")

# Detect emotion from text
def detect_emotion(command):
    tokens = word_tokenize(command.lower())
    for emotion in EMOTION_FOLDERS:
        if emotion in tokens:
            return emotion
    return None

# Hotkey action: Skip to next
def skip_to_next():
    global current_index, current_songs, current_emotion
    if current_songs:
        current_index += 1
        if current_index >= len(current_songs):
            current_index = 0
        pygame.mixer.music.stop()
        print("\n⏭️ Playing next song...")
        time.sleep(0.5)
        next_song_path = (
            get_song_path(current_emotion, current_songs[current_index])
            if current_emotion else current_songs[current_index]
        )
        play_song(next_song_path)

# Hotkey action: Quit program
def quit_program():
    print("\n👋 Exiting...")
    pygame.mixer.music.stop()
    os._exit(0)

# Key monitoring thread
def monitor_keys():
    keyboard.add_hotkey('n', skip_to_next)
    keyboard.add_hotkey('q', quit_program)
    keyboard.wait()

# Main function
def main():
    global current_songs, current_emotion, current_index

    pygame.init()
    nltk.download('punkt')
    threading.Thread(target=monitor_keys, daemon=True).start()

    print("\n🎶 Welcome to VibeSync!")
    print("💡 Controls: Press 'n' to play next song | Press 'q' to quit\n")

    while True:
        user_input = input("\n🎤 Enter a mood or song name ('n' for next, 'q' to quit): ").strip().lower()
        
        if user_input == "q":
            print("👋 Exiting program...")
            break
        elif user_input == "n" and current_songs:
            skip_to_next()
            continue

        song_path = find_song(user_input)
        if song_path:
            current_songs = [song_path]
            current_index = 0
            current_emotion = None
            play_song(song_path)
            continue

        # Assume it's a mood
        detected_emotion = detect_emotion(user_input) or user_input
        current_emotion = detected_emotion
        current_songs = list_songs(current_emotion)
        
        if not current_songs:
            continue

        while current_songs:
            song_choice = input("\n🔢 Enter song number, song name, 'n' for next, or 'q' to quit: ").strip().lower()
            
            if song_choice == "q":
                print("👋 Exiting program...")
                return
            elif song_choice == "n":
                skip_to_next()
            else:
                try:
                    song_index = int(song_choice) - 1
                    if 0 <= song_index < len(current_songs):
                        current_index = song_index
                        full_path = get_song_path(current_emotion, current_songs[current_index])
                        play_song(full_path)
                    else:
                        print("⚠️ Invalid selection! Try again.")
                except ValueError:
                    song_path = find_song(song_choice)
                    if song_path:
                        current_songs = [song_path]
                        current_index = 0
                        current_emotion = None
                        play_song(song_path)
                    else:
                        print("⚠️ Song not found! Try again.")

if __name__ == "__main__":
    main()
