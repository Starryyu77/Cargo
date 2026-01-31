import os
import google.generativeai as genai

# Try to find the key
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    key_path = os.path.join(os.path.dirname(__file__), 'api_key.txt')
    if os.path.exists(key_path):
        with open(key_path, 'r') as f:
            for line in f:
                if line.startswith("GOOGLE_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()

if not api_key:
    print("No API Key found")
    exit(1)

genai.configure(api_key=api_key)

print("Available Models:")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")
