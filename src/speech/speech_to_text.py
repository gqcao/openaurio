# /// script
# dependencies = [
#   "elevenlabs",
# ]
# ///

import os
import sys
from io import BytesIO
from elevenlabs.client import ElevenLabs


def speech_to_text(audio_file_path, language=None, model_id="scribe_v2", diarize=True, tag_events=True):
    """Transcribe audio file to text using ElevenLabs Scribe v2.
    
    Args:
        audio_file_path: Path to the audio file to transcribe
        language: Language code (default: None for auto-detection). e.g., "eng", "swe"
        model_id: Model ID (default: scribe_v2)
        diarize: Enable speaker diarization (default: True)
        tag_events: Tag audio events like laughter, applause (default: True)
    
    Returns:
        dict with transcription text and metadata
    """
    api_key = os.getenv("ELEVEN_API_KEY")
    if not api_key:
        raise ValueError("ELEVEN_API_KEY environment variable is not set. Set it with: export ELEVEN_API_KEY=your_key_here")

    if not os.path.isfile(audio_file_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

    client = ElevenLabs(api_key=api_key)

    with open(audio_file_path, "rb") as audio_file:
        audio_data = BytesIO(audio_file.read())

    transcription = client.speech_to_text.convert(
        file=audio_data,
        model_id=model_id,
        tag_audio_events=tag_events,
        language_code=language,
        diarize=diarize,
    )

    return {
        "text": transcription.text,
        "language": transcription.language_code if hasattr(transcription, 'language_code') else language,
        "diarization": diarize,
    }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Transcribe audio files using ElevenLabs Scribe v2."
    )
    parser.add_argument("--file", required=True, help="Path to the audio file to transcribe")
    parser.add_argument("--language", default=None, help="Language code (default: None for auto-detect). e.g., eng, swe")
    parser.add_argument("--model", default="scribe_v2", help="Model ID (default: scribe_v2)")
    parser.add_argument("--diarize", action=argparse.BooleanOptionalAction, default=True, help="Annotate who is speaking")
    parser.add_argument("--tag-events", action=argparse.BooleanOptionalAction, default=True, help="Tag audio events like laughter, applause")
    args = parser.parse_args()

    try:
        result = speech_to_text(
            audio_file_path=args.file,
            language=args.language,
            model_id=args.model,
            diarize=args.diarize,
            tag_events=args.tag_events,
        )
        print(result["text"])
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
