import os
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

models = [
    "qwen/qwen-2-vl-72b-instruct",
    "google/gemini-2.0-flash-001",
    "google/gemini-2.0-flash-lite-preview-02-05:free",
    "meta-llama/llama-3.2-90b-vision-instruct",
    "openrouter/auto",
    "openai/gpt-4o-mini",
]

tiny_png_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
data_uri = f"data:image/png;base64,{tiny_png_b64}"

working = []
for m in models:
    try:
        res = client.chat.completions.create(
            model=m,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe this image in 5 words."},
                        {"type": "image_url", "image_url": {"url": data_uri}}
                    ]
                }
            ],
            max_tokens=30,
        )
        ans = res.choices[0].message.content.strip()
        print(f"✅ {m}: {ans}")
        working.append(m)
    except Exception as e:
        print(f"❌ {m}: {e}")

print(f"\nWorking models: {working}")
