# /// script
# dependencies = [
#   "google-genai",
# ]
# ///

"""
Text-to-Speech using Google Gemini TTS

Gemini 2.5 Flash Preview TTS provides high-quality, controllable speech synthesis
with support for multiple voices and languages including Swedish.
"""

import argparse
import os
import sys
import wave
from google import genai
from google.genai import types


# Available voices for Gemini TTS
AVAILABLE_VOICES = [
    "Kore",      # Warm, friendly
    "Puck",      # Cheerful, upbeat
    "Charon",    # Calm, measured
    "Fenrir",    # Deep, authoritative
    "Aoede",     # Bright, clear
    "Leda",      # Soft, gentle
    "Orus",      # Strong, confident
    "Sulafat",   # Smooth, professional
    "Algieba",   # Warm, conversational
    "Despina",   # Friendly, approachable
    "Enceladus", # Energetic, dynamic
    "Erinome",   # Calm, soothing
    "Iapetus",   # Clear, articulate
    "Laomedeia", # Gentle, warm
    "Pulcherrima", # Elegant, refined
    "Umbriel",   # Deep, resonant
    "Zubenelgenubi", # Friendly, casual
]


def text_to_speech(
    text_input: str,
    voice_name: str = "Leda",
    model_id: str = "gemini-2.5-flash-preview-tts",
    output_file: str = None,
    style_instruction: str = None,
) -> dict:
    """Convert text to speech using Google Gemini TTS.
    
    Args:
        text_input: The text to convert to speech
        voice_name: Voice name from AVAILABLE_VOICES (default: Leda - soft, gentle)
        model_id: Gemini TTS model ID (default: gemini-2.5-flash-preview-tts)
        output_file: Output WAV file path. If None, returns audio bytes.
        style_instruction: Optional style instruction (e.g., "Say cheerfully")
    
    Returns:
        dict with status, output path (if file), or audio bytes
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable is not set. "
            "Get your key at: https://aistudio.google.com/apikeys"
        )

    # Initialize Gemini client
    client = genai.Client(api_key=api_key)

    # TTS model expects just the text to speak
    # Note: Short conversational phrases (<30 chars) may fail as the model
    # interprets them as text prompts. Use TTS only for longer responses.
    prompt = text_input

    try:
        response = client.models.generate_content(
            model=model_id,
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice_name,
                        )
                    )
                ),
            )
        )

        # Extract audio data
        audio_data = response.candidates[0].content.parts[0].inline_data.data

        if output_file:
            # Save as WAV file (Gemini outputs PCM at 24kHz)
            save_wav_file(output_file, audio_data)
            return {"status": "success", "output": output_file}
        else:
            return {"status": "success", "audio_data": audio_data}

    except Exception as e:
        raise RuntimeError(f"TTS generation failed: {e}")


def save_wav_file(filename: str, pcm_data: bytes, channels: int = 1, rate: int = 24000, sample_width: int = 2):
    """Save PCM audio data as a WAV file.
    
    Args:
        filename: Output file path
        pcm_data: Raw PCM audio data
        channels: Number of audio channels (default: 1 for mono)
        rate: Sample rate in Hz (default: 24000 for Gemini TTS)
        sample_width: Sample width in bytes (default: 2 for 16-bit)
    """
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm_data)


def list_voices():
    """Print available voices."""
    print("Available Gemini TTS voices:")
    print("-" * 40)
    for voice in AVAILABLE_VOICES:
        print(f"  • {voice}")
    print("-" * 40)
    print("\nRecommended for Swedish language learning:")
    print("  • Leda - Soft, gentle (good for Vera)")
    print("  • Aoede - Bright, clear")
    print("  • Sulafat - Smooth, professional")


def main():
    parser = argparse.ArgumentParser(
        description="Convert text to speech using Google Gemini TTS."
    )
    parser.add_argument("--text", required=True, help="The text to convert to speech.")
    parser.add_argument("--output", required=True, help="Output WAV file path.")
    parser.add_argument(
        "--voice", default="Leda",
        help=f"Voice name. Options: {', '.join(AVAILABLE_VOICES)}"
    )
    parser.add_argument(
        "--model", default="gemini-2.5-flash-preview-tts",
        help="Gemini TTS model ID."
    )
    parser.add_argument(
        "--style", default=None,
        help="Style instruction (e.g., 'Say cheerfully', 'Say slowly')"
    )
    parser.add_argument(
        "--list-voices", action="store_true",
        help="List available voices and exit."
    )
    args = parser.parse_args()

    if args.list_voices:
        list_voices()
        return

    try:
        result = text_to_speech(
            text_input=args.text,
            voice_name=args.voice,
            model_id=args.model,
            output_file=args.output,
            style_instruction=args.style,
        )
        print(f'{{"status": "{result["status"]}", "output": "{result["output"]}"}}')
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()