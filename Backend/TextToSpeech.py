# Backend/TextToSpeech.py

import pygame 
import random
import asyncio
import edge_tts
import os
from dotenv import dotenv_values

env_vars = dotenv_values(".env")
assistantVoice = env_vars.get("ASSISTANT_VOICE")

# Asynchronous function to convert text into audio file
async def textToAudioFile(text) -> None:
    filePath = r"Data\speech.mp3" # Define the path where speech file will be saved

    if os.path.exists(filePath): # If the file path already exists then remove it to avoid overwriting errors
        os.remove(filePath)

    # Create the communicate object to generate speech
    communicate = edge_tts.Communicate(text, assistantVoice, pitch='+5Hz', rate='+13%')
    await communicate.save(r'Data\speech.mp3') # Save the generated speech as mp3 file

# Function to manage text to speech functionality
def tts(text, func=lambda r=None: True):
    while True:
        try:
            # Convert text to an audio file asynchronously
            asyncio.run(textToAudioFile(text))
            
            # Initialize Pygame Mixer for audio playback
            pygame.mixer.init()

            # Load generated speech file Into pygame mixture
            pygame.mixer.music.load(r"Data\speech.mp3")
            pygame.mixer.music.play()

            # loop until the audio is done playing or the function stops
            while pygame.mixer.music.get_busy():
                if func() == False: # Checks if the external function returns false
                    break
                pygame.time.Clock().tick(10) # Limit the loop to 10 ticks per second
            
            return True # Return true if the audio played successfully
        
        except Exception as e:
            print(f"Eroor in TTS: {e}")

        finally:
            try:
                func(False)
                pygame.mixer.music.stop()
                pygame.mixer.quit()

            except Exception as e:
                print(f"Error in finally block: {e}")

def textToSpeech(text, func=lambda r=None: True):
    data = str(text).split(".")

    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]

    if len(data) > 4 and len(text) >= 250:
        tts(text.split(".")[0] + ". " + random.choice(responses), func)

    else:
        tts(text, func)

if __name__ == "__main__":
    while True:
        textToSpeech(input("Enter the text: "))
