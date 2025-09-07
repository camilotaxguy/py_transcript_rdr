# TransAIscriber

A Python 3.10 tool to transcribe audio files (e.g., iPhone voice memos) and summarize them with action items, attendees, time, and date using OpenAI GPT.

## Features
- Transcribe audio using local Whisper (openai/whisper or faster-whisper) or OpenAI Whisper API
- Summarize transcript with GPT (cost-efficient, default: gpt-3.5-turbo)
- Extract action items, attendees, time, and date
- Configurable via CLI or `.env` config file

## Setup (with Anaconda)

1. **Clone the repo and create a new Anaconda environment:**
   ```bash
   conda create -n transaiscriber python=3.10
   conda activate transaiscriber
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Copy and edit the config file:**
   ```bash
   cp config.example.env .env
   # Edit .env to add your OpenAI API key and preferences
   ```

## Usage

```bash
python transaiscriber.py path/to/audio.m4a --method local_whisper --output_dir output
```

- You can also set options in `.env` instead of CLI.
- Supported methods: `local_whisper`, `faster_whisper`, `openai_api`

## Extending
- Modular code for easy addition of cloud storage or other features.

## Requirements
- Python 3.10+
- See `requirements.txt`
