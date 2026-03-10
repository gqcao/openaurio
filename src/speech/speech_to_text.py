# /// script
# dependencies = [
#   "dashscope",
# ]
# ///

import os
import sys
import dashscope

dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'

def speech_to_text(audio_file_path):
    messages = [
        {"role": "user", "content": [{"audio": audio_file_path}]}
    ]
    api_key = os.getenv("QWEN_API_KEY")

    if not api_key:
        return "Error: QWEN_API_KEY environment variable is not set."

    response = dashscope.MultiModalConversation.call(
        api_key=api_key,
        model="qwen3-asr-flash",
        messages=messages,
        result_format="message",
        asr_options={
            "enable_itn": False
        }
    )
    return response["output"]["choices"][0]["message"]["content"][0]["text"]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python speech_to_text.py <audio_file_absolute_path>")
        sys.exit(1)
    result = speech_to_text(sys.argv[1])
    print(result)
