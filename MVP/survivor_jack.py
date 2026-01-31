"""
@file survivor_jack.py
@description Handles the interaction with the 'Survivor' (Jack), wrapping LLM calls.
@module PersonaManagement
"""

import time
import os
from typing import Optional

class SurvivorJack:
    def __init__(self, use_mock: bool = True):
        self.use_mock = use_mock
        self.name = "Jack"
        self.client = None
        self.provider = "mock" # 'openai', 'google', 'mock'
        self.model = "gpt-3.5-turbo" 
        
        if not self.use_mock:
            self._setup_client()

    def _setup_client(self):
        """Initializes the LLM client based on api_key.txt or env vars"""
        try:
            api_key = None
            base_url = None
            google_key = os.environ.get("GOOGLE_API_KEY") # Check Env first
            
            key_path = os.path.join(os.path.dirname(__file__), 'api_key.txt')
            if os.path.exists(key_path):
                with open(key_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("OPENAI_API_KEY="):
                            api_key = line.split("=", 1)[1]
                        elif line.startswith("OPENAI_BASE_URL="):
                            base_url = line.split("=", 1)[1]
                        elif line.startswith("GOOGLE_API_KEY=") and not google_key:
                            google_key = line.split("=", 1)[1]
            
            # Priority: Google Key (Env/File) > OpenAI Key
            if google_key:
                import google.generativeai as genai
                genai.configure(api_key=google_key)
                self.client = genai
                self.provider = "google"
                self.model = "gemini-3-pro-preview" # Confirmed available via list_models.py
                print(f"[SYSTEM] Using Google Generative AI (Model: {self.model})")
                return

            if api_key:
                from openai import OpenAI
                self.client = OpenAI(api_key=api_key, base_url=base_url)
                self.provider = "openai"
                self.model = "gpt-4o-mini" # Default for OpenAI compatible
                print(f"[SYSTEM] Using OpenAI Compatible API (Model: {self.model})")
                return

            print("[WARNING] No valid API Key found. Falling back to Mock.")
            self.use_mock = True

        except Exception as e:
            # STRICT MODE: Do not fall back to mock silently if initialization fails.
            # We want the user to know if the LLM connection is broken.
            print(f"[ERROR] Failed to initialize LLM client: {e}. Strict Mode: Exiting.")
            raise e

    def speak(self, system_prompt: str, user_prompt: str) -> str:
        if self.use_mock:
            print("[DEBUG] Using Mock Response")
            return self._mock_response(user_prompt)
        
        if self.provider == "google":
            print(f"[DEBUG] Calling Google API ({self.model})...")
            return self._google_call(system_prompt, user_prompt)
        elif self.provider == "openai":
            print(f"[DEBUG] Calling OpenAI API ({self.model})...")
            return self._openai_call(system_prompt, user_prompt)
        else:
            # Should not happen if use_mock is False and setup succeeded
            raise RuntimeError("Provider not configured correctly in Strict Mode")

    def _mock_response(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        time.sleep(0.3)
        if "hummmmm" in prompt_lower:
            return "Whoa... hear that? It's humming. Lights are on! You actually know your stuff, boss."
        if "sparks!" in prompt_lower or "smoking" in prompt_lower:
            return "GAH! *Cough* *Cough* IT BIT ME! The panel is smoking! Did you read the manual upside down?!"
        if "jammed into terminal a" in prompt_lower:
            return "Alright, twisting the red one onto the A terminal... Tight. Don't electrocute me."
        if "blue wire is connected to terminal b" in prompt_lower:
            return "Blue one going to B. This wire feels greasy. Done."
        if "cover is off" in prompt_lower:
            return "Got the cover off. Man, it's a rat's nest in here. I see Red, Blue, and a Switch."
        if "standing in front of a gray metal box" in prompt_lower:
             return "I'm freezing here. The box is just staring at me. What do I do?"
        return "Uh, say again? It's loud in here and I'm freezing. Just tell me what to stick where."

    def _openai_call(self, system_prompt: str, user_prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[COMM ERROR]: Signal interference. ({str(e)})"

    def _google_call(self, system_prompt: str, user_prompt: str) -> str:
        try:
            model = self.client.GenerativeModel(
                model_name=self.model,
                system_instruction=system_prompt
            )
            
            chat = model.start_chat(history=[])
            response = chat.send_message(user_prompt)
            return response.text.strip()
        except Exception as e:
            # Return error directly so user sees it wasn't a mock response
            return f"[API ERROR] {str(e)}"
