# speechma-tts-simple-cli

This repository provides a Python program that uses the Speechma API to convert text into speech. It allows users to select from multiple voices, dialects, and languages, and bypasses the 2000-character limit by splitting the input text into manageable chunks. The program sanitizes the text, handles punctuation for better speech flow, and plays the audio as soon as it is received. Multiple chunks are played sequentially without overlap.

## Features

- **Multiple Voice Options:** The program supports multiple voices, genders, and dialects, offering flexibility in audio output.
- **Text Chunking:** The input text is split into chunks to bypass the 2000-character limit imposed by the Speechma API.
- **Input Sanitization:** Non-ASCII characters are removed from the input to ensure compatibility with the API.
- **Punctuation Handling:** Punctuation marks like full stops and commas are handled properly for clearer, more natural speech.
- **Audio Playback:** The generated audio is played automatically.
- **Customizable Voice Selection:** Users can choose from a list of available voices, including gender and regional dialect options.
- **Retry Logic:** If an error occurs when processing a chunk, the program automatically retries up to three times.

## Installation

### Prerequisites

- Python 3.x
- `requests` library
- `pydub` library
- `numpy` library
- `sounddevice` library

### Steps to Install

1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/WillsonPat/speechma-tts-simple-cli.git
   cd speechma-tts-simple-cli
   ```

1. Install the required dependencies:

   ```bash
   pip install requests numpy pydub sounddevice
   ```

1. Ensure that ffmpeg's binaries are available on the command line.

1. Ensure that the `voices.json` file is present in the root directory. If it's missing or corrupted, you will see an error.

1. Run the script:

   ```bash
   python main.py
   ```

## Usage

- The program will prompt you to enter the text you wish to convert to speech. You can input multiline text by pressing Enter after each line. To finish, type an empty line and press Enter.
- You will then be asked to choose the voice you want to use from the available options.
- The program will process the input text, split it into chunks if needed, and send the chunks to the Speechma API for conversion into speech.
- The resulting audio will, by default, be played directly without hitting the disk.

## Files

- `main.py`: The main script that handles text input, API interaction, and audio saving.
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

## Thanks

Thanks to:
* the original author for their initial project: [FairyRoot](https://github.com/fairy-root)

## Contributing

If you would like to contribute to this project, feel free to fork the repository and submit pull requests. Ensure that your code follows the existing structure, and test it thoroughly.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
