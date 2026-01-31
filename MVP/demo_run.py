import sys
from io import StringIO
from main import GameEngine

# Mocking input
class MockInput:
    def __init__(self, inputs):
        self.inputs = inputs
        self.index = 0

    def __call__(self, prompt=""):
        if self.index < len(self.inputs):
            val = self.inputs[self.index]
            self.index += 1
            print(f"{prompt}{val}") # Echo input to look like real interaction
            return val
        return "exit"

def run_demo():
    # Define the scenario script
    script = [
        "Hello?",                 # Chatty start
        "Open the box",           # Action 1
        "Connect red wire to A",  # Action 2
        "Connect blue wire to B", # Action 3 (Should trigger Win)
    ]
    
    # Hijack stdin
    original_input = __builtins__.input
    __builtins__.input = MockInput(script)
    
    try:
        engine = GameEngine()
        engine.run()
    finally:
        # Restore stdin
        __builtins__.input = original_input

if __name__ == "__main__":
    run_demo()
