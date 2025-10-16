import requests as req
from pydub import AudioSegment
import numpy as np
import sounddevice as sd
import json
import sys
import io
import threading
import queue
from typing import Dict


# Function to print colored text
def print_colored(text: str, color: str) -> None:
    """
    Print colored text.

    Args:
        text: Text to be printed.
        color: Color to be applied to the text.
    """
    colors: Dict[str, str] = {
        "green": "\033[92m",
        "red": "\033[91m",
        "blue": "\033[94m",
        "yellow": "\033[93m",
        "cyan": "\033[96m",
        "magenta": "\033[95m"
    }
    color_code: str = colors.get(color.lower(), "\033[0m")
    colored_text: str = f"{color_code}{text}\033[0m"
    print(colored_text)

# Function to get user input with colored prompt
def input_colored(prompt: str, color: str) -> str:
    """
    Get user input with colored prompt.

    Args:
        prompt: Prompt to be displayed to the user.
        color: Color of the prompt.

    Returns:
        User input.
    """
    colors: Dict[str, str] = {
        "green": "\033[92m",
        "red": "\033[91m",
        "blue": "\033[94m",
        "yellow": "\033[93m",
        "cyan": "\033[96m",
        "magenta": "\033[95m"
    }
    color_code: str = colors.get(color.lower(), "\033[0m")
    colored_prompt: str = f"{color_code}{prompt}\033[0m"
    return input(colored_prompt)

def load_voices() -> Dict | None:
    """Load voices from the JSON file"""
    try:
        with open('voices.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print_colored("Error: voices.json file not found.", "red")
        return {}
    except json.JSONDecodeError:
        print_colored("Error: voices.json is not a valid JSON file.", "red")
        return {}

def display_voices(voices: map | None, prefix: str = "") -> int:
    """Recursively display voices in an enumerated format"""
    if not voices:
        print_colored("Error: No voices available.", "red")
        return 0

    index = 0
    for key, value in voices.items():
        if isinstance(value, dict):
            new_prefix = f"{prefix}{key} " if prefix else f"{key} "
            count = display_voices(value, new_prefix)
            index += count
        else:
            index += 1
            print(f"{index}- {prefix}{key}")
    return index

def get_voice_id(voices, choice: int, current_index:int = 0):
    """Recursively get the selected voice ID based on user input"""
    for key, value in voices.items():
        if isinstance(value, dict):
            result, current_index = get_voice_id(value, choice, current_index)
            if result:
                return result, current_index
        else:
            current_index += 1
            if current_index == choice:
                return value, current_index
    return None, current_index

class TtsProducer:
    """Text to speech producer that obtains mp3 in a separate thread and passes them to a consumer"""
    def __init__(self, voice_id, nextConsumer):
        self.session = req.Session()
        self.nextConsumer = nextConsumer
        self.voice_id = voice_id
        self.url = 'https://speechma.com/com.api/tts-api.php'
        self.session.headers = {
            'Host': 'speechma.com',
            'Sec-Ch-Ua-Platform': 'Windows',
            'Accept-Language': 'en-US,en;q=0.9',
            'Sec-Ch-Ua': '"Chromium";v="131", "Not_A Brand";v="24"',
            'Content-Type': 'application/json',
            'Sec-Ch-Ua-Mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.140 Safari/537.36',
            'Accept': '*/*',
            'Origin': 'https://speechma.com',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://speechma.com/',
            'Accept-Encoding': 'gzip, deflate, br',
            'Priority': 'u=1, i'
        }
        self.text_queue = queue.Queue()
        self.consumer_thread = threading.Thread(target=self.text_consumer)
        self.consumer_thread.daemon = True  # Allows thread to exit when the main program does
        self.consumer_thread.start()

    def text_consumer(self):
        """Consume text data from the queue, generate mp3 and pass it next consumer."""

        def get_audio(url: str, data) -> bytes | None:
            """Function to get audio from the server"""
            try:
                json_data = json.dumps(data)
                response = self.session.post(url, data=json_data)
                response.raise_for_status()
                if response.headers.get('Content-Type') == 'audio/mpeg':
                    return response.content
                else:
                    print_colored(f"Unexpected response format: {response.headers.get('Content-Type')}", "red")
                    return None
            except req.exceptions.RequestException as e:
                if e.response:
                    print_colored(f"Server response: {e.response.text}", "red")
                print_colored(f"Request failed: {e}", "red")
                return None
            except Exception as e:
                print_colored(f"An unexpected error occurred: {e}", "red")
                return None

        def split_text(text: str, chunk_size: int = 1000):
            """Function to split text into chunks"""
            if not text:
                print_colored("Error: No text provided to split.", "red")
                return []

            chunks = []
            while len(text) > 0:
                if len(text) <= chunk_size:
                    chunks.append(text)
                    break
                chunk = text[:chunk_size]
                last_full_stop = chunk.rfind('.')
                last_comma = chunk.rfind(',')
                split_index = last_full_stop if last_full_stop != -1 else last_comma
                if split_index == -1:
                    split_index = chunk_size
                else:
                    split_index += 1
                chunks.append(text[:split_index])
                text = text[split_index:].lstrip()
            return chunks

        def validate_text(text: str):
            """Function to validate text"""
            return ''.join(char for char in text if ord(char) < 128)
        
        def get_mp3_data(text_data):
            """Obtains mp3 data from Speechma"""
            text = validate_text(text_data)     
            chunks = split_text(text, chunk_size=1000)
            if not chunks:
                print_colored("\nError: Could not split text into chunks. Skipping text data {text}.", "red")
                return

            for i, chunk in enumerate(chunks, start=1):
                print_colored(f"\nProcessing chunk {i}...", "yellow")
                data = {
                    "text": chunk.replace("'", "").replace('"', '').replace("&", "and"),
                    "voice": self.voice_id
                }

                max_retries = 3
                for retry in range(max_retries):
                    response = get_audio(self.url, data)
                    if response:
                        return response
                    
                    print_colored(f"Retry {retry + 1} for chunk {i}...", "yellow")
                else:
                    print_colored(f"Failed to process chunk {i} after {max_retries} retries.", "red")

        while True:
            try:
                text = self.text_queue.get()
                if text is None:  # Exit signal
                    break
                mp3_data = get_mp3_data(text)
                if mp3_data is not None:
                    self.nextConsumer.put(mp3_data)
                self.text_queue.task_done()
            except Exception as e:
                print_colored(f"Exception while processing TTS data: {e}", "red")

    def put(self, text_data):
        """Add text data to the queue for playback."""
        self.text_queue.put(text_data)

    def wait_for_completion(self):
        """Wait until all text_data is processed and the next consumer is ready"""
        self.text_queue.join()
        self.text_queue.put(None)  # Signal the consumer to exit
        self.consumer_thread.join()  # Wait for consumer thread to finish
        if self.nextConsumer is not None:
            self.nextConsumer.wait_for_completion()

class AudioPlayer:
    """Audio player working on a separate thread"""
    def __init__(self):
        self.audio_queue = queue.Queue()
        self.consumer_thread = threading.Thread(target=self.audio_consumer)
        self.consumer_thread.daemon = True  # Allows thread to exit when the main program does
        self.consumer_thread.start()

    def audio_consumer(self):
        """Consume audio data from the queue and play it."""

        def play_audio(mp3_data):
            """Plays an audio encoded as mp3 data"""
            byte_io = io.BytesIO(mp3_data)
            audio = AudioSegment.from_file(byte_io, format='mp3')
            samples = np.array(audio.get_array_of_samples())
            
            if audio.channels == 2:
                samples = samples.reshape((-1, 2))
            
            # using sounddevice library instead of pydub since the latter
            # uses simple audio which crashes on later python versions
            sd.play(samples, samplerate=audio.frame_rate)
            sd.wait()

        while True:
            try:
                mp3_byte_data = self.audio_queue.get()
                if mp3_byte_data is None:  # Exit signal
                    break
                play_audio(mp3_byte_data)
                self.audio_queue.task_done()
            except Exception as e:
                print_colored(f"Exception while processing mp3 data: {e}", "red")

    def put(self, mp3_byte_data):
        """Add audio data to the queue for playback."""
        self.audio_queue.put(mp3_byte_data)

    def wait_for_completion(self):
        """Wait until all audio tasks are done."""
        self.audio_queue.join()
        self.audio_queue.put(None)  # Signal the consumer to exit
        self.consumer_thread.join()  # Wait for consumer thread to finish

# Main function
def main():
    voices = load_voices()
    if not voices:
        print_colored("Error: No voices available. Exiting.", "red")
        return

    print_colored("Available voices:", "blue")
    total_voices = display_voices(voices)

    try:
        choice = int(input_colored(f"Enter the number of the voice you want to use (1-{total_voices}): ", "green"))
        if choice < 1 or choice > total_voices:
            print_colored("Error: Invalid choice. Please enter a valid number.", "red")
            return
    except ValueError:
        print_colored("Error: Invalid input. Please enter a number.", "red")
        return

    voice_id, _ = get_voice_id(voices, choice)
    if not voice_id:
        print_colored("Error: Invalid voice choice. Exiting.", "red")
        return

    audioPlayer = AudioPlayer()
    ttsProducer = TtsProducer(voice_id, audioPlayer)

    print("\nInteractive input mode:")
    print("  1. Type sentences to speak out loud.")
    print("  2. Each line is processed separately.")
    print("  3. An empty line exits the program.")
    print_colored("\nWaiting for user input...", "green")
    try:
        while True:
            text = input()
            
            if not text:
                print_colored("End of text stream. Exiting gracefully.", "yellow")
                return

            ttsProducer.put(text)
    finally:
        print_colored("Waiting for producers to finish. Press Ctrl + C to abort.", "yellow")
        ttsProducer.wait_for_completion()

# Main execution
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\nExiting gracefully...", "yellow")
        sys.exit(0)