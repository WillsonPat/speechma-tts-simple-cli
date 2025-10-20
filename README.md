# speechma-tts-simple-cli

This repository provides a Python program that uses the Speechma API to convert text into speech. It allows users to select from multiple voices, dialects, and languages, and bypasses the 2000-character limit by splitting the input text into manageable chunks. The program sanitizes the text, handles punctuation for better speech flow, and plays the audio as soon as it is received. Multiple chunks are played sequentially without overlap.

## Features

- **Multiple Voice Options:** The program supports multiple voices, genders, and dialects, offering flexibility in audio output.
- **Text Chunking:** The input text is split into chunks to bypass the 2000-character limit imposed by the Speechma API.
- **Input Sanitization:** Non-ASCII characters are removed from the input to ensure compatibility with the API.
- **Punctuation Handling:** Punctuation marks like full stops and commas are handled properly for clearer, more natural speech.
- **Audio Playback:** The generated audio is played automatically.
- **Retry Logic:** If an error occurs when processing a chunk, the program automatically retries up to three times.

## Installation

### Prerequisites

- Python 3.x
- `requests` library
- `pydub` library
- `numpy` library
- `sounddevice` library
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

### Prerequisites

- Prerequistes for running the script
- `pyinstaller` library

## Building

To build a release exectuable call:
```bash
pyinstaller --onefile main.py
```

`build.bat` is provided as shorthand

## Usage

- The program supports various command line parameters and further customisation via a settings.json file.
- The program has the current working modes:
  - Interacive mdoe: This is the default mode. You will be promped to enter the text that you wish to convert to speech. You can input multiple lines by pressing enter after each line. Each line is processed individually. Pressing enter on an empty line or pressing Ctrl + C exits the program.
  - Single string mode: Passing a string via the settings `text` property or `--text` command line argument will acivate this mode. The program will automtically process the provided string and exit.
  - File mode: Passing a file via the settings `file` property or `--file` command line argument will activate this mode. In this mode, the program will read the proide file and, by default, process it as a whole before exiting. This can be changed by passing the `--fileMonitor` command line argument or "fileMonitor" property in the settings file. It can have the following values:
    - `once`: Default mode. The file contents are read once and processed. The program will exit right after.
    - `updates`: The file contents are read and processed after every subsequent update. The program will not exit until the user terminates it, such as by pressing "Ctrl+C".
- The voices to use can be selected either:
  - interactively: you will be asked for the language, country, and gender before being presented with a list of available voices
  - automatically: by setting the`voice` property in the settings file or the `--voice` command line argument, the program will select the desired voice. Voices are selected by internal id which can be identified either when selecting the voide in interacive mode or by inspecting `voices.json` file.
- When processing input text, the program will split it into chunks if needed, and send the chunks to the Speechma API for conversion into speech.
- The resulting audio will, by default, be played directly without hitting the disk (subject to pydub's limitations).

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
  settings_example.json: A sample JSON file with some of the settings that can be used as a reference for your custom settings.json.

## Settings file 

The program supports reading default settings from a settings.json file. A custom path for the settings file can be specified by passing `--settings` command line option.

Most of the command line arguments are availble as properties in the settings file.This allows you to modify the defaults. Passing the same option via a command line argument will take precedence over the property set in the settings file.

The settings file supports the following properties:
- voices: location for the voices json file which maps speechma's voice id to a language, country, gender and voice name. Defaults to 'voices.json'.
- voice: the internal id of speechma's voice to use (e.g., "voice-111"). Check the shiped `voices.json` or run the program interactively to find the desired voice id.
- text: enables automatic processing of the provided text before exiting.
- file: enables automatic processing of file content. Use fileMonitor to specify the operation mode.
- fileMonitor:
  - use `once` (default) to read the contents of the whole file, process it and exit
  - use `updates` to monitor for file content changes and process them on change. The user has to press Ctrl + C to exit the program once ready.
- ffmpegBinPath: specifies where FFmpeg's bin folder is locationed. Should be used if FFmpeg is not present by default in the system's path envionment variable.

## Thanks

Thanks to:
* [FairyRoot](https://github.com/fairy-root): original author for their initial project 
* [Owen Eldridge](https://github.com/oweneldridge) for improvements to original project (via [speechma-tts-cli](https://github.com/oweneldridge/))

## Contributing

If you would like to contribute to this project, feel free to fork the repository and submit pull requests. Ensure that your code follows the existing structure, and test it thoroughly.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
