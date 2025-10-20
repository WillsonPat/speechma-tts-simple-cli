# User Manual

This is a user-facing manual for the pre-built release packages available for tts-helper-tool. To run the script from source get the sources from <https://github.com/WillsonPat/tts-helper-tool> and follow the setup and instllation instructions.

## General Usage

- The program has the current working modes:
  - **Interacive mode**: This is the default mode. You will be promped to enter the text that you wish to convert to speech. You can input multiple lines by pressing enter after each line. Each line is processed individually. Pressing enter on an empty line or pressing Ctrl + C exits the program.
  - **Single string mode**: Passing a string via the settings `text` property or `--text` command line argument will acivate this mode. The program will automtically process the provided string and exit.
  - **File mode**: Passing a file via the settings `file` property or `--file` command line argument will activate this mode. In this mode, the program will read the proide file and, by default, process it as a whole before exiting. This can be changed by passing the `--fileMonitor` command line argument or "fileMonitor" property in the settings file. It can have the following values:
    - `once`: Default mode. The file contents are read once and processed. The program will exit right after.
    - `updates`: The file contents are read and processed after every subsequent update. The program will not exit until the user terminates it, such as by pressing "Ctrl+C".
- The voices to use can be selected either:
  - **interactively**: you will be asked for the language, country, and gender before being presented with a list of available voices
  - **automatically**: by setting the`voice` property in the settings file or the `--voice` command line argument, the program will select the desired voice. Voices are selected by internal id which can be identified either when selecting the voide in interacive mode or by inspecting `voices.json` file.
- When processing input text, the program will split it into chunks if needed, and send the chunks to the Speechma API for conversion into speech.
- The resulting audio will, by default, be played directly without hitting the disk (subject to pydub's limitations).

## Command Line Options

Passing `--help` at the command line will show the available command line options, similar to the following.

```text
usage: tts-helper-tool [-h] [--settings SETTINGS] [--voice VOICE] [--text TEXT] [--file FILE] [--voices VOICES] [--fileMonitor {once,updates}]

TTS Helper Tool

options:
  -h, --help            show this help message and exit
  --settings SETTINGS, -s SETTINGS
                        Path to JSON settings file (default: settings.json)
  --voice VOICE, -v VOICE
                        Voice ID to use (e.g. voice-XXX). If omitted, interactive selection is used.
  --text TEXT, -t TEXT  Text to speak (single utterance).
  --file FILE, -f FILE  Read text from file and send as single utterance.
  --voices VOICES       Path to voices.json (default: voices.json)
  --fileMonitor {once,updates}
                        Specify 'once' to read the file once, or 'updates' to monitor for updates.
```

## Settings File

The program supports reading default settings from a settings.json file. A custom path for the settings file can be specified by passing `--settings` command line option.

Most of the command line arguments are availble as properties in the settings file. This allows you to modify the defaults. Passing the same option via a command line argument will take precedence over the property set in the settings file.

The settings file supports the following properties:

- voices: location for the voices json file which maps speechma's voice id to a language, country, gender and voice name. Defaults to 'voices.json'.
- `voice`: the internal id of speechma's voice to use (e.g., "voice-111"). Check the shiped `voices.json` or run the program interactively to find the desired voice id.
- `text`: enables automatic processing of the provided text before exiting.
- `file`: enables automatic processing of file content. Use fileMonitor to specify the operation mode.
- `fileMonitor`:
  - use `once` (default) to read the contents of the whole file, process it and exit
  - use `updates` to monitor for file content changes and process them on change. The user has to press Ctrl + C to exit the program once ready.
- `ffmpegBinPath`: specifies where FFmpeg's bin folder is locationed. Should be used if FFmpeg is not present by default in the system's path envionment variable.
