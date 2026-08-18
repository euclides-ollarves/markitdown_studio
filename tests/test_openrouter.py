"""
Test OpenRouter API with Vision Model
"""

import os
import sys
import base64
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY", "")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
    default_headers={
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "MarkItDown Studio",
    }
)

def test_models():
    print("Testing OpenRouter models...")
    # Let's test a simple vision query with a 1x1 test image or small prompt
    test_models_list = [
        "google/gemini-2.0-flash-exp:free",
        "google/gemini-flash-1.5",
        "meta-llama/llama-3.2-11b-vision-instruct:free",
        "meta-llama/llama-3.2-11b-vision-instruct",
        "qwen/qwen-2-vl-72b-instruct",
        "openai/gpt-4o-mini",
    ]
    
    # 1x1 red PNG in base64
    tiny_png_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    data_uri = f"data:image/png;base64,{tiny_png_b64}"

    for model in test_models_list:
        try:
            print(f"Trying model: {model}...")
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "What color is this 1x1 pixel image? Answer in one word."},
                            {"type": "image_url", "image_url": {"url": data_uri}}
                        ]
                    }
                ],
                max_tokens=50,
            )
            content = response.choices[0].message.content
            print(f"✅ SUCCESS with {model} -> {content.strip()}")
            return model
        except Exception as e:
            print(f"❌ Error with {model}: {e}")

    return None

if __name__ == "__main__":
    best_model = test_models()
    print(f"\nRecommended model: {best_model}")
