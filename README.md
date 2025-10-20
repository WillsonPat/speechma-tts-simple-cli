# tts-helper-tool

This repository provides a Python program to be used along side speech-to-text tools (STT) to extend their functionality, including by providing TTS as an addon. It currenlty uses the Speechma API to convert text into speech, allows users to select from multiple voices, dialects, and languages, and bypasses the 2000-character limit by splitting the input text into manageable chunks. The program sanitizes the text, handles punctuation for better speech flow, and plays the audio as soon as it is received. Multiple chunks are played sequentially without overlap.

## Features

- **Multiple Voice Options:** The program supports multiple voices, genders, and dialects, offering flexibility in audio output.
- **Text Chunking:** The input text is split into chunks to bypass the 2000-character limit imposed by the Speechma API.
- **Input Sanitization:** Non-ASCII characters are removed from the input to ensure compatibility with the API.
- **Punctuation Handling:** Punctuation marks like full stops and commas are handled properly for clearer, more natural speech.
- **Audio Playback:** The generated audio is played automatically.
- **Retry Logic:** If an error occurs when processing a chunk, the program automatically retries up to three times.

## Installation

### Prerequisites for installation

- Python 3.12 or later
- `requests` library
- `pydub` library
- `pyaudio` library
- `watchdog` library

### Steps to get started

1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/WillsonPat/speechma-tts-simple-cli.git
   cd speechma-tts-simple-cli
   ```

1. Install the required dependencies:

   ```bash
   pip install requests numpy pydub sounddevice watchdog
   ```

1. Ensure that ffmpeg's binaries are available on the command line.

1. Ensure that the `voices.json` file is present in the root directory. If it's missing or corrupted, you will see an error.

1. Run the script:

  ```bash
  python main.py
  ```

## Builing for release

### Prerequisites for building

Prerequistes for running the script:

- `pyinstaller` library

## Building

Building currently targets windows.
To build a release exectuable call `build.bat` from a python prompt on windows.

## Usage

The program supports various command line parameters and further customisation via a settings.json file.

The command line arguments can be listed by passing the `--help` parameter at the command line. For more user-facing instructions refer to the accompanying [user manual](UserManual.md).

## Files

- `tts-helper-tool.py`: The main script that handles text input, API interaction, and audio saving.
- `voices.json`: A JSON file that contains the available voices and their IDs. Example:

  ```json
  {
    "English": {
      "UK": {
        "female": {
          "Sonia": "voice-35",
          "Maisie": "voice-30"
        }
      }
    }
  }
  ```

- `settings_example.json`: A sample JSON file with some of the settings that can be used as a reference for your custom settings.json.

## Thanks

Thanks to:

- [FairyRoot](https://github.com/fairy-root): original author for their initial project

- [Owen Eldridge](https://github.com/oweneldridge) for improvements to original project (via [speechma-tts-cli](https://github.com/oweneldridge/))

## Contributing

If you would like to contribute to this project, feel free to fork the repository and submit pull requests. Ensure that your code follows the existing structure, and test it thoroughly.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
