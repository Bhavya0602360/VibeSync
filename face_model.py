import os
import pygame
from deepface import DeepFace
import cv2

# Initialize pygame mixer
pygame.mixer.init()

# Path to your music directory
music_data_dir = r"C:\VibeSync\music"  # Ensure this path is correct

# Ensure music directory exists
if not os.path.exists(music_data_dir):
    print(f"Music directory {music_data_dir} does not exist!")
    exit()

# Function to list songs from a specific mood folder
def list_mood_songs(mood):
    mood_dir = os.path.join(music_data_dir, mood)
    if os.path.exists(mood_dir):
        songs = [os.path.join(mood_dir, f) for f in os.listdir(mood_dir) if f.endswith((".mp3", ".wav"))]
        if songs:
            print(f"\n🎵 Songs available for {mood}:")
            for index, song in enumerate(songs):
                print(f"{index + 1}. {os.path.basename(song)}")
            return songs
        else:
            print(f"⚠ No songs found for {mood}.")
    else:
        print(f"⚠ No music folder found for {mood}.")
    
    return []

# Function to list all songs in the entire music folder
def list_all_songs():
    all_songs = []
    for root, _, files in os.walk(music_data_dir):
        for file in files:
            if file.endswith((".mp3", ".wav")):
                all_songs.append(os.path.join(root, file))

    return all_songs

# Function to play a song
def play_song(song_path):
    pygame.mixer.music.load(song_path)
    pygame.mixer.music.play()
    print(f"\n🎵 Now playing: {os.path.basename(song_path)}")

# Function to detect mood from webcam
def get_mood_from_webcam():
    cap = cv2.VideoCapture(0)
    detected_mood = "neutral"

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        try:
            result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
            detected_mood = result[0]['dominant_emotion']
        except Exception as e:
            print(f"Error detecting emotion: {e}")
            detected_mood = "neutral"
        
        cv2.putText(frame, f"Emotion: {detected_mood}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
        cv2.imshow('Webcam - Press Q to exit', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    return detected_mood

# Main loop
def main():
    while True:
        detected_mood = get_mood_from_webcam()
        print(f"\nDetected Mood: {detected_mood}")

        # List only detected mood songs
        mood_songs = list_mood_songs(detected_mood)
        
        # Get all songs from the entire library
        all_songs = list_all_songs()

        if not mood_songs:
            print("No songs found for this mood. Please select from the full library.")
            mood_songs = all_songs

        if not all_songs:
            print("⚠ No songs found in the library. Exiting...")
            break

        current_index = 0  # Start with the first song of detected mood

        while True:
            user_input = input("\nEnter index number, song name, 'n' for next song, or 'q' to quit: ").strip().lower()

            if user_input == 'q':
                print("👋 Exiting program...")
                pygame.mixer.music.stop()
                return
            
            elif user_input == 'n':
                # Move to the next song in the detected mood list (looping back if at the end)
                current_index = (current_index + 1) % len(mood_songs)
                play_song(mood_songs[current_index])

            elif user_input.isdigit() and 1 <= int(user_input) <= len(mood_songs):
                current_index = int(user_input) - 1  # Set the selected song index
                play_song(mood_songs[current_index])

            else:
                # Check if user entered a valid song name from the entire music library
                matching_songs = [s for s in all_songs if os.path.basename(s).lower() == user_input]
                if matching_songs:
                    play_song(matching_songs[0])  # Play the first matched song
                else:
                    print("⚠ Invalid input. Please try again.")

if __name__ == "__main__":
    main()