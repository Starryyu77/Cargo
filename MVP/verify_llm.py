from survivor_jack import SurvivorJack
from prompts import JACK_SYSTEM_PROMPT

def verify():
    print("--- VERIFICATION START ---")
    
    # 1. Initialize Jack (Strict Mode)
    # This will FAIL if API keys are missing, proving we aren't mocking implicitly.
    try:
        jack = SurvivorJack(use_mock=False)
    except Exception as e:
        print(f"FAILED TO INIT: {e}")
        return

    # 2. Send a prompt that has NO mock response
    # The mock logic only knows about "box", "red", "blue", "switch".
    # Asking about "singing" or "poetry" will return a default confusion msg in mock mode,
    # but a creative response in LLM mode.
    test_prompt = "Jack, sing a short song about how cold it is."
    
    print(f"\n[PROMPT]: {test_prompt}")
    
    response = jack.speak(JACK_SYSTEM_PROMPT, test_prompt)
    
    print(f"\n[RESPONSE]:\n{response}")
    print("\n--- VERIFICATION END ---")

if __name__ == "__main__":
    verify()
