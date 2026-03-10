# /// script
# dependencies = [
#   "elevenlabs>=1.0",
# ]
# ///

import argparse
import os
import sys


def text_to_speech(text_input, voice_id="JBFqnCBsd6RMkjVDRZzb", model_id="eleven_multilingual_v2", output_file=None):
    """Convert text to speech using ElevenLabs API.
    
    Args:
        text_input: The text to convert to speech
        voice_id: ElevenLabs voice ID (default: JBFqnCBsd6RMkjVDRZzb - Rachel)
        model_id: ElevenLabs model ID (default: eleven_multilingual_v2)
        output_file: Optional output file path. If None, returns audio bytes.
    
    Returns:
        If output_file is provided: dict with status and output path
        If output_file is None: bytes of the audio data
    """
    api_key = os.getenv("ELEVEN_API_KEY")
    if not api_key:
        raise ValueError("ELEVEN_API_KEY environment variable is not set. Set it with: export ELEVEN_API_KEY=your_key_here")

    from elevenlabs.client import ElevenLabs

    client = ElevenLabs(api_key=api_key)

    audio = client.text_to_speech.convert(
        text=text_input,
        voice_id=voice_id,
        model_id=model_id,
        output_format="mp3_44100_128",
    )

    if output_file:
        with open(output_file, "wb") as f:
            for chunk in audio:
                if chunk:
                    f.write(chunk)
        return {"status": "success", "output": output_file}
    else:
        audio_bytes = b""
        for chunk in audio:
            if chunk:
                audio_bytes += chunk
        return audio_bytes


def main():
    parser = argparse.ArgumentParser(
        description="Convert text to speech using the ElevenLabs API."
    )
    parser.add_argument("--text", required=True, help="The text to convert to speech.")
    parser.add_argument("--output", required=True, help="Output MP3 file path.")
    parser.add_argument(
        "--voice-id", default="JBFqnCBsd6RMkjVDRZzb", help="ElevenLabs voice ID."
    )
    parser.add_argument(
        "--model-id", default="eleven_multilingual_v2", help="ElevenLabs model ID."
    )
    args = parser.parse_args()

    result = text_to_speech(
        text_input=args.text,
        voice_id=args.voice_id,
        model_id=args.model_id,
        output_file=args.output
    )
    
    print(f'{{"status": "{result["status"]}", "output": "{result["output"]}"}}')


if __name__ == "__main__":
    main()
