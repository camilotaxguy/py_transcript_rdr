import argparse
import os
from dotenv import load_dotenv
import openai
from typing import Optional
import re
#
# conda create -n transaiscriber python=3.10
#conda activate transaiscriber
#pip install -r requirements.txt
#conda install -c conda-forge ffmpeg
#cp config.example.env .env
#python transaiscriber.py path/to/audio.m4a --method local_whisper --output_dir output


# Whisper imports
try:
    import whisper  # openai/whisper
except ImportError:
    whisper = None
try:
    from faster_whisper import WhisperModel
except ImportError:
    WhisperModel = None

# Load config from .env if present
def load_config(config_path=None):
    if config_path and os.path.exists(config_path):
        load_dotenv(config_path)
    else:
        load_dotenv()
    return {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'TRANSCRIPTION_METHOD': os.getenv('TRANSCRIPTION_METHOD', 'local_whisper'),
        'MODEL': os.getenv('MODEL', 'gpt-3.5-turbo')
    }

def parse_args():
    parser = argparse.ArgumentParser(description='TransAIscriber: Audio transcription and summarization tool')
    parser.add_argument('audio_file', type=str, help='Path to the audio file')
    parser.add_argument('--config', type=str, help='Path to config file (.env)', default=None)
    parser.add_argument('--method', type=str, choices=['local_whisper', 'faster_whisper', 'openai_api'], help='Transcription method')
    parser.add_argument('--model', type=str, help='OpenAI model for summarization')
    parser.add_argument('--output_dir', type=str, default='output', help='Directory to save transcript and summary')
    return parser.parse_args()

def transcribe_local_whisper(audio_file: str) -> str:
    if not whisper:
        raise ImportError('openai/whisper is not installed.')
    model = whisper.load_model('base')
    result = model.transcribe(audio_file, language='en')
    return result['text']

def transcribe_faster_whisper(audio_file: str) -> str:
    if not WhisperModel:
        raise ImportError('faster-whisper is not installed.')
    model = WhisperModel('base')
    segments, _ = model.transcribe(audio_file, language='en')
    return ' '.join([segment.text for segment in segments])

def transcribe_openai_api(audio_file: str, api_key: str) -> str:
    openai.api_key = api_key
    with open(audio_file, 'rb') as f:
        transcript = openai.audio.transcriptions.create(
            model='whisper-1',
            file=f,
            language='en'
        )
    return transcript.text if hasattr(transcript, 'text') else transcript['text']

def extract_meeting_metadata(transcript: str):
    # Simple regex-based extraction for attendees, date, and time
    attendees = re.findall(r'Attendees?:?\s*(.*)', transcript, re.IGNORECASE)
    date = re.findall(r'(?:Date|Dated):?\s*([\w\s,/-]+)', transcript, re.IGNORECASE)
    time = re.findall(r'(?:Time|at):?\s*([\w\s:apmAPM]+)', transcript, re.IGNORECASE)
    return {
        'attendees': attendees[0] if attendees else '',
        'date': date[0] if date else '',
        'time': time[0] if time else ''
    }

def summarize_with_gpt(transcript: str, metadata: dict, api_key: str, model: str = 'gpt-3.5-turbo') -> str:
    openai.api_key = api_key
    prompt = f"""
You are an assistant that summarizes meeting transcripts. Extract and list:
- Action items
- Attendees (if not already provided)
- Date and time (if not already provided)

Transcript:
{transcript}

Known metadata:
Attendees: {metadata['attendees']}
Date: {metadata['date']}
Time: {metadata['time']}

Format your response as:
Attendees: ...
Date: ...
Time: ...
Action Items:
- ...
- ...
Summary:
...
"""
    response = openai.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=600
    )
    # For openai>=1.0.0, response.choices[0].message.content
    return response.choices[0].message.content.strip()

def main():
    print(">>>>>>>>>>Starting TransAIscriber...")
    args = parse_args()
    config = load_config(args.config)
    # CLI args override config
    transcription_method = args.method or config['TRANSCRIPTION_METHOD']
    model = args.model or config['MODEL']
    openai_api_key = config['OPENAI_API_KEY']
    audio_file = args.audio_file
    output_dir = args.output_dir

    if not openai_api_key:
        raise ValueError('OpenAI API key must be provided via config or .env')
    if not os.path.exists(audio_file):
        raise FileNotFoundError(f'Audio file not found: {audio_file}')
    os.makedirs(output_dir, exist_ok=True)

    # --- Transcription ---
    print(">>>>>>>>>>Transcribing...")
    print(f'Transcribing {audio_file} using {transcription_method}...')
    transcript = None
    if transcription_method == 'local_whisper':
        transcript = transcribe_local_whisper(audio_file)
    elif transcription_method == 'faster_whisper':
        transcript = transcribe_faster_whisper(audio_file)
    elif transcription_method == 'openai_api':
        transcript = transcribe_openai_api(audio_file, openai_api_key)
    else:
        raise ValueError(f'Unknown transcription method: {transcription_method}')

    print(">>>>>>>>>>Saving transcript...")
    transcript_path = os.path.join(output_dir, 'transcript.txt')
    with open(transcript_path, 'w') as f:
        f.write(transcript or '')
    print(f'Transcript saved to {transcript_path}')

    # --- Summarization ---
    print('Extracting meeting metadata...')
    metadata = extract_meeting_metadata(transcript)
    print('Summarizing transcript...')
    summary = summarize_with_gpt(transcript, metadata, openai_api_key, model)

    # Save summary
    summary_path = os.path.join(output_dir, 'summary.txt')
    with open(summary_path, 'w') as f:
        f.write(summary or '')
    print(f'Summary saved to {summary_path}')
    print("<<<<<<<<<< TransAIscriber completed successfully.")
if __name__ == '__main__':
    main()
