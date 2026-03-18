# /// script
# dependencies = [
#   "google-genai",
# ]
# ///

"""
Speech-to-Text using Google Gemini 2.5 Flash Native Audio

Gemini 2.5 Flash supports native audio input, allowing direct transcription
without needing a separate ASR service.
"""

import os
import sys
import wave
import tempfile
from pathlib import Path
from google import genai
from google.genai import types


def convert_to_wav(audio_file_path: str) -> str:
    """Convert audio file to WAV format if needed.
    
    Gemini expects audio in specific formats. This converts to WAV
    using ffmpeg if available.
    """
    # Check if already WAV
    if audio_file_path.lower().endswith('.wav'):
        return audio_file_path
    
    # Convert using ffmpeg
    import subprocess
    wav_path = audio_file_path.rsplit('.', 1)[0] + '_converted.wav'
    
    try:
        subprocess.run([
            'ffmpeg', '-y', '-i', audio_file_path,
            '-ar', '16000',  # 16kHz sample rate
            '-ac', '1',      # Mono
            wav_path
        ], check=True, capture_output=True)
        return wav_path
    except subprocess.CalledProcessError:
        # If ffmpeg fails, return original and hope Gemini can handle it
        return audio_file_path
    except FileNotFoundError:
        # ffmpeg not installed, try with original file
        return audio_file_path


def speech_to_text(
    audio_file_path: str,
    language: str = "sv",
    model_id: str = "gemini-3.1-flash-lite-preview",
) -> dict:
    """Transcribe audio file to text using Google Gemini.
    
    Args:
        audio_file_path: Path to the audio file to transcribe
        language: Language code (default: "sv" for Swedish)
        model_id: Gemini model ID (default: gemini-2.5-flash)
    
    Returns:
        dict with transcription text and metadata
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable is not set. "
            "Get your key at: https://aistudio.google.com/apikeys"
        )

    if not os.path.isfile(audio_file_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

    # Initialize Gemini client
    client = genai.Client(api_key=api_key)

    # Read audio file
    audio_path = Path(audio_file_path)
    
    # Determine MIME type based on file extension
    mime_types = {
        '.wav': 'audio/wav',
        '.mp3': 'audio/mpeg',
        '.ogg': 'audio/ogg',
        '.oga': 'audio/ogg',
        '.m4a': 'audio/mp4',
        '.webm': 'audio/webm',
        '.flac': 'audio/flac',
    }
    
    ext = audio_path.suffix.lower()
    mime_type = mime_types.get(ext, 'audio/wav')
    
    # Upload audio file to Gemini
    uploaded_file = client.files.upload(file=audio_path)
    
    # Create prompt for transcription
    language_names = {
        'sv': 'Swedish',
        'en': 'English',
        'es': 'Spanish',
        'de': 'German',
        'fr': 'French',
        'zh': 'Chinese',
        'ja': 'Japanese',
        'ko': 'Korean',
    }
    language_name = language_names.get(language, language)

    prompt = f"""Transcribe the following audio file.
The audio is in {language_name}.
Return ONLY the transcribed text, nothing else.
Do not include any explanations or notes.
If the audio is unclear or empty, return an empty string."""

    try:
        # Use uploaded file reference (more reliable for larger files)
        response = client.models.generate_content(
            model=model_id,
            contents=[
                prompt,
                uploaded_file,
            ],
            config=types.GenerateContentConfig(
                temperature=0.1,  # Low temperature for accurate transcription
            )
        )
        
        transcription_text = response.text.strip()
        
        return {
            "text": transcription_text,
            "language": language,
            "model": model_id,
        }
        
    except Exception as e:
        raise RuntimeError(f"Transcription failed: {e}")
    finally:
        # Clean up uploaded file
        try:
            if uploaded_file:
                client.files.delete(name=uploaded_file.name)
        except:
            pass


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Transcribe audio files using Google Gemini."
    )
    parser.add_argument("--file", required=True, help="Path to the audio file to transcribe")
    parser.add_argument("--language", default="sv", help="Language code (default: sv for Swedish)")
    parser.add_argument("--model", default="gemini-3.1-flash-lite-preview", help="Gemini model ID")
    args = parser.parse_args()

    try:
        result = speech_to_text(
            audio_file_path=args.file,
            language=args.language,
            model_id=args.model,
        )
        print(result["text"])
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()