"""
Test NVIDIA NIM API with nemotron-ocr-v2 or vision models
"""

import os
import sys
import base64
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("NVIDIA_API_KEY", "")
BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")

client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY
)

def check_models():
    print("Checking NVIDIA models...")
    headers = {"Authorization": f"Bearer {API_KEY}"}
    try:
        r = requests.get(f"{BASE_URL}/models", headers=headers, timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            models = [m.get("id") for m in data.get("data", [])]
            print(f"Total models available: {len(models)}")
            ocr_models = [m for m in models if "ocr" in m.lower() or "nemotron" in m.lower() or "vision" in m.lower() or "neva" in m.lower() or "vl" in m.lower()]
            print("Relevant models found:", ocr_models)
            return models
        else:
            print("Response:", r.text[:300])
    except Exception as e:
        print("Error checking models:", e)
    return []

if __name__ == "__main__":
    check_models()
