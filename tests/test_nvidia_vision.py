"""
Test NVIDIA Vision OCR models with an image
"""

import io
import os
import sys
import base64
from PIL import Image, ImageDraw
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("NVIDIA_API_KEY", "")
BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")

client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY
)

# 1. Create a test image
img = Image.new("RGB", (600, 250), color=(255, 255, 255))
draw = ImageDraw.Draw(img)
draw.text((20, 20), "HOSPITAL GENERAL - ROL DE MEDICOS", fill=(0, 0, 0))
draw.text((20, 70), "Fecha: 19 de Agosto 2026", fill=(0, 0, 0))
draw.text((20, 110), "Guardia: Dr. Roberto Gomez | Area: Urgencias", fill=(0, 0, 0))

stream = io.BytesIO()
img.save(stream, format="PNG")
b64 = base64.b64encode(stream.getvalue()).decode("utf-8")
data_uri = f"data:image/png;base64,{b64}"

candidates = [
    "nvidia/nemotron-nano-12b-v2-vl",
    "nvidia/nemotron-parse",
    "nvidia/llama-3.1-nemotron-nano-vl-8b-v1",
    "meta/llama-3.2-11b-vision-instruct",
]

for model in candidates:
    print(f"\n--> Testing model: {model}...")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Transcribe all text from this image into Markdown format."},
                        {"type": "image_url", "image_url": {"url": data_uri}}
                    ]
                }
            ],
            max_tokens=512,
        )
        ans = response.choices[0].message.content
        print(f"✅ SUCCESS with {model}:\n{ans.strip()}\n")
        break
    except Exception as e:
        print(f"❌ Failed with {model}: {e}")
