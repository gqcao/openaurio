# /// script
# dependencies = [
#   "dashscope",
#   "requests",
# ]
# requires-python = ">=3.9"
# ///

import argparse
import json
import os
import sys

import dashscope
import requests


def text_to_speech(text_input, voice="Cherry", language="English", model="qwen3-tts-flash"):
    """Call the Qwen TTS API and return the audio URL."""
    dashscope.base_http_api_url = "https://dashscope.aliyuncs.com/api/v1"
    response = dashscope.MultiModalConversation.call(
        model=model,
        api_key=os.getenv("QWEN_API_KEY"),
        text=text_input,
        voice=voice,
        language_type=language,
        stream=False,
    )
    try:
        return response["output"]["audio"]["url"]
    except (KeyError, TypeError):
        print(f"Error: unexpected API response: {json.dumps(response, indent=2, default=str)}", file=sys.stderr)
        sys.exit(1)

def download_file(url, destination):
    """Download a file from a URL to a local path."""
    response = requests.get(url)
    if response.status_code == 200:
        with open(destination, "wb") as f:
            f.write(response.content)
        print(json.dumps({"status": "success", "file": destination, "size_bytes": len(response.content)}))
    else:
        print(f"Error: failed to download audio. HTTP status: {response.status_code}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Convert text to speech using the Qwen3 TTS API.",
    )
    parser.add_argument("--text", required=True, help="The text to convert to speech.")
    parser.add_argument("--output", required=True, help="Destination file path for the audio (e.g. output.mp3).")
    parser.add_argument("--voice", default="Cherry", help="Voice name (default: Cherry).")
    parser.add_argument("--language", default="English", help="Language of the text (default: English).")
    parser.add_argument(
        "--model",
        default="qwen3-tts-flash",
        help="Model name (default: qwen3-tts-flash). Use qwen3-tts-instruct-flash for instruction control.",
    )
    args = parser.parse_args()

    api_key = os.getenv("QWEN_API_KEY")
    if not api_key:
        print("Error: QWEN_API_KEY environment variable is not set.", file=sys.stderr)
        print("Get an API key at: https://help.aliyun.com/zh/model-studio/get-api-key", file=sys.stderr)
        sys.exit(1)

    audio_url = text_to_speech(args.text, voice=args.voice, language=args.language, model=args.model)
    download_file(audio_url, args.output)

if __name__ == "__main__":
    main()
