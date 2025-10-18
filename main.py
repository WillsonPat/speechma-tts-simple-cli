from typing import Dict
import numpy as np
import sounddevice as sd
import requests as req
from pydub import AudioSegment
from enum import Enum
import json
import sys
import io
import threading
import queue
import argparse
import os

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

def display_header():
    print_colored("=" * 60, "cyan")
    print_colored("Speechma Text-to-Speech Simple Client", "magenta")
    print_colored("=" * 60, "cyan")

def get_all_voice_ids(data):
    """Recursively get all voice IDs from nested structure"""
    for key, value in data.items():
        if isinstance(value, dict):
            yield from get_all_voice_ids(value)
        else:
            yield value

def count_voices_by_level(voices, level=0):
    """Count voices at different hierarchy levels"""
    counts = {}

    def count_recursive(data, current_level=0):
        for key, value in data.items():
            if isinstance(value, dict):
                if current_level == level:
                    # Count voices under this key
                    voice_count = sum(1 for _ in get_all_voice_ids(value))
                    counts[key] = voice_count
                count_recursive(value, current_level + 1)

    count_recursive(voices)
    return counts

def select_voice_interactive(voices):
    """
    Interactive voice selection with hierarchical filtering.
    Returns: (voice_id, voice_name) tuple or (None, None) if cancelled

    Hierarchy: Language → Country → Gender → Voice Name
    Special commands: 'b' (back), 'r' (restart), 'voice-XXX' (direct ID)
    """

    while True:
        # Step 1: Select Language
        print_colored("\n" + "="*60, "blue")
        print_colored("STEP 1: Select Language", "blue")
        print_colored("="*60, "blue")

        lang_counts = count_voices_by_level(voices, level=0)
        languages = sorted(lang_counts.keys())

        for i, lang in enumerate(languages, 1):
            count = lang_counts[lang]
            print(f"{i}. {lang} ({count} voices)")

        print_colored("\nType 'voice-XXX' to directly enter a voice ID, or 'q' to quit", "yellow")

        lang_input = input_colored(f"\nSelect language (1-{len(languages)}): ", "green").strip()

        # Handle special inputs
        if lang_input.lower() == 'q':
            return None, None
        if lang_input.startswith('voice-'):
            return lang_input, f"Direct ID: {lang_input}"

        try:
            lang_choice = int(lang_input)
            if lang_choice < 1 or lang_choice > len(languages):
                print_colored("Invalid choice. Please try again.", "red")
                continue
        except ValueError:
            print_colored("Invalid input. Please enter a number.", "red")
            continue

        selected_language = languages[lang_choice - 1]

        # Step 2: Select Country
        while True:
            print_colored("\n" + "="*60, "blue")
            print_colored(f"STEP 2: Select Country ({selected_language})", "blue")
            print_colored("="*60, "blue")

            country_data = voices[selected_language]
            country_counts = count_voices_by_level({selected_language: country_data}, level=1)
            countries = sorted(country_counts.keys())

            for i, country in enumerate(countries, 1):
                count = country_counts[country]
                print(f"{i}. {country} ({count} voices)")

            print_colored("\nType 'b' to go back, 'r' to restart, or 'q' to quit", "yellow")

            country_input = input_colored(f"\nSelect country (1-{len(countries)}): ", "green").strip()

            if country_input.lower() == 'b':
                break  # Go back to language selection
            if country_input.lower() == 'r':
                return select_voice_interactive(voices)  # Restart
            if country_input.lower() == 'q':
                return None, None

            try:
                country_choice = int(country_input)
                if country_choice < 1 or country_choice > len(countries):
                    print_colored("Invalid choice. Please try again.", "red")
                    continue
            except ValueError:
                print_colored("Invalid input. Please enter a number.", "red")
                continue

            selected_country = countries[country_choice - 1]

            # Step 3: Select Gender
            while True:
                print_colored("\n" + "="*60, "blue")
                print_colored(f"STEP 3: Select Gender ({selected_language} - {selected_country})", "blue")
                print_colored("="*60, "blue")

                gender_data = country_data[selected_country]
                genders = sorted(gender_data.keys())

                for i, gender in enumerate(genders, 1):
                    count = len(gender_data[gender])
                    print(f"{i}. {gender.capitalize()} ({count} voices)")

                print_colored("\nType 'b' to go back, 'r' to restart, or 'q' to quit", "yellow")

                gender_input = input_colored(f"\nSelect gender (1-{len(genders)}): ", "green").strip()

                if gender_input.lower() == 'b':
                    break  # Go back to country selection
                if gender_input.lower() == 'r':
                    return select_voice_interactive(voices)  # Restart
                if gender_input.lower() == 'q':
                    return None, None

                try:
                    gender_choice = int(gender_input)
                    if gender_choice < 1 or gender_choice > len(genders):
                        print_colored("Invalid choice. Please try again.", "red")
                        continue
                except ValueError:
                    print_colored("Invalid input. Please enter a number.", "red")
                    continue

                selected_gender = genders[gender_choice - 1]

                # Step 4: Select Voice Name
                while True:
                    print_colored("\n" + "="*60, "blue")
                    print_colored(f"STEP 4: Select Voice", "blue")
                    print_colored(f"{selected_language} - {selected_country} - {selected_gender.capitalize()}", "cyan")
                    print_colored("="*60, "blue")

                    voice_names = gender_data[selected_gender]
                    sorted_names = sorted(voice_names.keys())

                    # Ask if user wants to see voice IDs
                    show_ids_input = input_colored("\nShow voice IDs? (y/n, default: n): ", "blue").lower().strip()

                    # Handle navigation commands at the ID prompt
                    if show_ids_input == 'b':
                        break  # Go back to gender selection
                    if show_ids_input == 'r':
                        return select_voice_interactive(voices)  # Restart
                    if show_ids_input == 'q':
                        return None, None

                    show_ids = show_ids_input == 'y'

                    print()
                    for i, name in enumerate(sorted_names, 1):
                        voice_id = voice_names[name]
                        if show_ids:
                            print(f"{i}. {name} \033[90m({voice_id})\033[0m")
                        else:
                            print(f"{i}. {name}")

                    print_colored("\nType 'b' to go back, 'r' to restart, or 'q' to quit", "yellow")

                    voice_input = input_colored(f"\nSelect voice (1-{len(sorted_names)}): ", "green").strip()

                    if voice_input.lower() == 'b':
                        break  # Go back to gender selection
                    if voice_input.lower() == 'r':
                        return select_voice_interactive(voices)  # Restart
                    if voice_input.lower() == 'q':
                        return None, None

                    try:
                        voice_choice = int(voice_input)
                        if voice_choice < 1 or voice_choice > len(sorted_names):
                            print_colored("Invalid choice. Please try again.", "red")
                            continue
                    except ValueError:
                        print_colored("Invalid input. Please enter a number.", "red")
                        continue

                    selected_name = sorted_names[voice_choice - 1]
                    selected_voice_id = voice_names[selected_name]

                    # Show final selection
                    print_colored("\n" + "="*60, "green")
                    print_colored("✓ Voice Selected!", "green")
                    print_colored("="*60, "green")
                    print(f"Language: {selected_language}")
                    print(f"Country: {selected_country}")
                    print(f"Gender: {selected_gender.capitalize()}")
                    print(f"Voice: {selected_name}")
                    print(f"Voice ID: {selected_voice_id}")
                    print_colored("="*60, "green")

                    return selected_voice_id, selected_name

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
        
        def attempt_get_audio(data, chunk_id: int, max_retries: int = 3):
            """Attempts to get audio data with retries"""
            for retry in range(max_retries):
                response = get_audio(self.url, data)
                if response:
                    return response

                print_colored(f"Retry {retry + 1} for chunk {chunk_id}...", "yellow")
            else:
                print_colored(f"Failed to process chunk {chunk_id} after {max_retries} retries.", "red")

        def get_mp3_data_chunks(text_data):
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

                yield attempt_get_audio(data, i, max_retries = 3)

        while True:
            try:
                text = self.text_queue.get()
                if text is None:  # Exit signal
                    break
                for mp3_data in get_mp3_data_chunks(text):
                    self.nextConsumer.put(mp3_data)
            except Exception as e:
                print_colored(f"Exception while processing TTS data: {e}", "red")
            finally:
                self.text_queue.task_done()

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
            except Exception as e:
                print_colored(f"Exception while processing mp3 data: {e}", "red")
            finally:
                self.audio_queue.task_done()

    def put(self, mp3_byte_data):
        """Add audio data to the queue for playback."""
        self.audio_queue.put(mp3_byte_data)

    def wait_for_completion(self):
        """Wait until all audio tasks are done."""
        self.audio_queue.join()
        self.audio_queue.put(None)  # Signal the consumer to exit
        self.consumer_thread.join()  # Wait for consumer thread to finish

class VoiceManager:
    """Manager for audio voices that can be used with speechma"""
    def __init__(self):
        self.voices = {}
        self.voices_path = "voices.json"

    def load_voices(self) -> bool:
        """Load voices from the JSON file"""
        try:
            with open(self.voices_path, 'r') as f:
                voices = json.load(f)
                if not voices:
                    return False
                self.voices = voices
                return True
        except FileNotFoundError:
            print_colored(f"Error: {self.voices_path} file not found.", "red")
        except json.JSONDecodeError:
            print_colored(f"Error: {self.voices_path} is not a valid JSON file.", "red")
        return False

    def is_valid_voice(self, voice_id: str) -> bool:
        """
        Validate whether a given voice_id exists in the loaded voices.

        Returns True if voice_id was found among the leaf voice IDs, False otherwise.
        """
        if not voice_id or not self.voices:
            return False
        # get_all_voice_ids yields all leaf voice ids from the nested structure
        return any(voice_id == vid for vid in get_all_voice_ids(self.voices))
    
    def get_voice_description_for_id(self, voice_id: str) -> str | None:
        """Get the voice language, country, name, and gender for a given voice ID"""

        def find_name_recursive(data):
            for key, value in data.items():
                if isinstance(value, dict):
                    result = find_name_recursive(value)
                    if result:
                        # Prepend the current key to the deeper result to build a hierarchical description
                        return f"{result}, {key}"
                else:
                    if value == voice_id:
                        return key
            return None

        return find_name_recursive(self.voices)
    
    def count_voice_stats(self):
        """Function to count voices in the hierarchical structure"""
        stats = {
            'total': 0,
            'languages': set(),
            'countries': set(),
            'genders': set()
        }

        def count_recursive(data, level=0):
            for key, value in data.items():
                if isinstance(value, dict):
                    if level == 0:  # Language level
                        stats['languages'].add(key)
                    elif level == 1:  # Country level
                        stats['countries'].add(key)
                    elif level == 2:  # Gender level
                        stats['genders'].add(key)
                    count_recursive(value, level + 1)
                else:
                    stats['total'] += 1

        count_recursive(self.voices)
        return stats
    
    def display_stats(self):
        # Display statistics
        stats = self.count_voice_stats()
        print_colored(f"Voice Library: {stats['total']} voices", "yellow")
        print(f"   • {len(stats['languages'])} languages")
        print(f"   • {len(stats['countries'])} countries")
        print_colored("=" * 60, "cyan")

class FileMonitorOption(Enum):
    ONCE = "once"
    UPDATES = "updates"
    DEFAULT = ONCE

class Settings:
    """Manager for application settings loaded from a JSON file and/or command line arguments"""

    def load(self) -> Dict:
        def convertToFileMonitorOption(file_monitor_string):
            """
            Convert string to FileMonitorOption enum, with default fallback.
            Args:
                file_monitor_string: String representation of the file monitor option.
            Returns:
                FileMonitorOption enum value.
            """
            try:
                return FileMonitorOption(file_monitor_string)
            except ValueError:
                print_colored(f"Invalid value for --fileMonitor: {file_monitor_string}. Using default value '{FileMonitorOption.DEFAULT.value}'.", "yellow")
                return FileMonitorOption.DEFAULT

        def parse_args() -> argparse.Namespace:
            """
            Parse command line arguments.
            Returns:
                parsed arguments.
            """
            parser = argparse.ArgumentParser(description="Speechma Text-to-Speech Simple Client")
            parser.add_argument("--settings", "-s", help="Path to JSON settings file (default: settings.json)", default="settings.json")
            parser.add_argument("--voice", "-v", help="Voice ID to use (e.g. voice-XXX). If omitted, interactive selection is used.")
            parser.add_argument("--text", "-t", help="Text to speak (single utterance).")
            parser.add_argument("--file", "-f", help="Read text from file and send as single utterance.")
            parser.add_argument("--voices", help="Path to voices.json (default: voices.json)")
            parser.add_argument('--fileMonitor',
                                choices=[option.value for option in FileMonitorOption],
                                help="Specify 'once' to read the file once, or 'updates' to monitor for updates.")
            args = parser.parse_args()
            return args

        def load_settings_from_file(path: str = "settings.json") -> Dict:
            """
            Load settings from a JSON file. Returns a dict (empty if not found/invalid).
            Args:
                path: Path to the settings file.
            Returns:
                Dictionary with settings.
            """
            if not path:
                return {}
            try:
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as sh:
                        loaded = json.load(sh)
                    if isinstance(loaded, dict):
                        print_colored(f"Loaded settings from {path}", "cyan")
                        return loaded
                    print_colored(f"Settings file {path} does not contain a JSON object; ignoring.", "yellow")
                return {}
            except json.JSONDecodeError as e:
                print_colored(f"Settings file {path} is not valid JSON: {e}", "red")
            except Exception as e:
                print_colored(f"Failed to read settings file {path}: {e}", "red")
            return {}
        
        args = parse_args()
        settings_file = load_settings_from_file(args.settings)
        
        # Load settings (CLI takes precedence over settings values)
        self.voice_id = args.voice if args.voice is not None else settings_file.get("voice")
        self.text = args.text if args.text is not None else settings_file.get("text")
        self.file = args.file if args.file is not None else settings_file.get("file")
        self.voices_path = args.voices if args.voices is not None else settings_file.get("voices", "voices.json")
        file_monitor_string = args.fileMonitor if args.fileMonitor is not None else settings_file.get("fileMonitor", FileMonitorOption.DEFAULT.value)
        self.file_monitor = convertToFileMonitorOption(file_monitor_string)
        self.display_stats = not (self.text or self.file)

    def display_settings(self):
        """
        Display current settings.
        """
        print_colored("Current Settings:", "cyan")
        print(f"  Voice ID: {self.voice_id if self.voice_id else 'None (interactive selection)'}")
        print(f"  Text: {'Provided' if self.text else 'None'}")
        print(f"  File: '{self.file if self.file else 'None'}'")
        print(f"  File Monitor: {self.file_monitor.value}")
        print(f"  Voices Path: '{self.voices_path}'")
        print_colored("=" * 60, "cyan")

def get_file_content(file_path: str) -> str | None:
    """
    Read and return the content of a file.
    Args:
        file_path: Path to the file.
    Returns:
        Content of the file as a string.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as fh:
            return fh.read()
    except Exception as e:
        print_colored(f"Failed to read file {file_path}: {e}", "red")
        return

def process_file_oneshot(file_path: str, consumer: any) -> None:
    print_colored(f"Processing file '{file_path}' once", "yellow")
    content = get_file_content(file_path)
    if content:
        consumer.put(content)

def monitor_file_for_input(file_path: str, consumer: any) -> None:
    """
    Monitor a file for changes and process its content when modified.
    Args:
        file_path: Path to the file to monitor.
        consumer: Consumer to process the file content.
    """

    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    from time import sleep

    class FileChangeHandler(FileSystemEventHandler):
        old_content: str = ""

        def on_modified(self, event):
            if event.src_path == file_path:
                content = get_file_content(file_path)
                if content and content != self.old_content:
                    print_colored(f"Processing change in '{file_path}'", "yellow")
                    self.old_content = content
                    consumer.put(content)

    observer = Observer()
    event_handler = FileChangeHandler()
    file_path = os.path.abspath(file_path)
    dir_path = os.path.dirname(file_path)
    observer.schedule(event_handler, path=dir_path, recursive=False)

    try:
        print_colored(f"Monitoring '{file_path}' for changes. Press Ctrl + C to stop", "green")
        observer.start()
        while True:
            sleep(1)
    except KeyboardInterrupt:
        print_colored("File monitoring ended by user.", "yellow")
    finally:
        print_colored("Waiting for file monitor to finish. Press Ctrl + C to abort.", "yellow")
        observer.stop()
        observer.join()

# Main function
def main():
    display_header()

    settings = Settings()
    settings.load()
    settings.display_settings()
    
    voiceManager = VoiceManager()
    voiceManager.voices_path = settings.voices_path
    if not voiceManager.load_voices():
        print_colored("Error: No voices available. Exiting.", "red")
        return

    if settings.display_stats:
        voiceManager.display_stats()

    # Determine voice id (use CLI or interactive)
    voice_id = settings.voice_id
    if voice_id:
        voice_name = voiceManager.get_voice_description_for_id(voice_id)
        if voice_name:
            print_colored(f"Using voice ID from command line: {voice_name} ({voice_id})", "green")
        else:
            print_colored(f"Error: Invalid voice ID '{voice_id}' provided. Exiting.", "red")
            return
    else:
        voice_id, _ = select_voice_interactive(voiceManager.voices)
        if not voice_id:
            print_colored("Voice selection cancelled. Exiting.", "yellow")
            return

    audioPlayer = AudioPlayer()
    ttsProducer = TtsProducer(voice_id, audioPlayer)

    try:
        if settings.text:
            ttsProducer.put(settings.text)
            return
        
        if settings.file:
            if settings.file_monitor == FileMonitorOption.UPDATES:
                monitor_file_for_input(settings.file, ttsProducer)
            else:
                process_file_oneshot(settings.file, ttsProducer)
            return

        # Interactive input mode (fallback)
        print("\nInteractive input mode:")
        print("  1. Type sentences to speak out loud.")
        print("  2. Each line is processed separately.")
        print("  3. An empty line exits the program.")
        print_colored("\nWaiting for user input...", "green")
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
    except EOFError:
        print_colored("\nEnd of input detected. Exiting gracefully...", "yellow")
        sys.exit(0)
