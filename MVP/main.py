"""
@file main.py
@description Main Game Engine for Project: CARGO V1.0. Orchestrates Physics, AI, and State.
@module GameEngine
"""

import time
from MVP.state_schema import GameState
from MVP.physics_engine import PhysicsSimulator
from MVP.scenario_manager import ScenarioManager
from MVP.survivor_jack import SurvivorJack
from MVP.ai_middleware import CommandInterpreter
from MVP.prompts import JACK_SYSTEM_PROMPT, get_context_prompt

class GameEngine:
    def __init__(self):
        # 1. Initialize State (Single Source of Truth)
        self.state = GameState()
        
        # 2. Initialize Physics
        self.physics = PhysicsSimulator(self.state)
        
        # 3. Scenario Manager (Content Engine)
        self.scenario_manager = ScenarioManager(self.state)
        self.scenario_manager.load_scenario("co2_crisis")

        # 4. Initialize AI Agents
        self.jack = SurvivorJack(use_mock=False)
        self.middleware = CommandInterpreter(
            provider=self.jack.provider,
            client=self.jack.client,
            model=self.jack.model
        )
        
        # 4. Message History
        self.history = []

    def tick(self, delta_time: float = 1.0) -> dict:
        """
        Advances the game simulation by one tick (real-time).
        Returns telemetry data.
        """
        sensory_feedback = self.physics.simulation_step(delta_time)
        
        # Check for Critical Events (e.g. Death)
        game_over = False
        if self.state.jack.status == "dead":
            game_over = True
            
        return {
            "type": "TICK",
            "telemetry": self.get_telemetry(),
            "sensory": sensory_feedback,
            "game_over": game_over
        }

    def handle_command(self, user_input: str) -> dict:
        """
        Processes a user command (asynchronous to physics).
        """
        # 0. Context for AI
        telemetry = self.get_telemetry()
        context_snapshot = {
            "environment": "Mars Habitat",
            "telemetry": telemetry,
            "jack_status": self.state.jack.status
        }
        
        # 1. Safety Check (Middleware)
        analysis = self.middleware.analyze_intent(user_input, context_snapshot)
        if not analysis["is_safe"]:
            return {
                "type": "INTERCEPT",
                "jack_response": f"[SAFETY INTERLOCK]: {analysis['danger_reason']}",
                "telemetry": telemetry
            }

        # 2. Physics-based Logic (Placeholder for Phase 3 Puzzles)
        # Check if Scenario Manager handles this action (Scripted Event)
        scripted_response = self.scenario_manager.process_action(analysis["intent"])
        
        # 3. Generate Jack's Response
        # We inject the *current* sensory feedback into the prompt
        sensory_feedback = self.physics.sensory_translator.translate(self.state)
        
        # Inject Telemetry into sensory feedback for immersive reporting
        telemetry_report = (
            f"\n[HUD DATA] "
            f"CO2: {telemetry['co2']:.3f}% | "
            f"TEMP: {telemetry['temp']:.1f}C | "
            f"HR: {telemetry['heart_rate']}bpm"
        )
        
        full_prompt = (
            f"{JACK_SYSTEM_PROMPT}\n\n"
            f"--- CURRENT SITUATION ---\n{sensory_feedback}\n{telemetry_report}\n"
        )

        if scripted_response:
             full_prompt += f"\n[ACTION RESULT]: {scripted_response}\n(Explain this result to the player in character)"
        
        full_prompt += f"\n--- USER COMMAND ---\n{user_input}\n"
        
        # Call LLM
        response = self.jack.speak(JACK_SYSTEM_PROMPT, full_prompt)
        
        return {
            "type": "RESPONSE",
            "jack_response": response,
            "telemetry": telemetry
        }

    def get_telemetry(self) -> dict:
        """Helper to extract clean telemetry for Frontend"""
        env = self.state.environment
        jack = self.state.jack
        power = self.state.power_system
        
        # Helper to get inventory names
        inventory_names = [item.name for item in jack.inventory]

        return {
            "co2": round(env.co2_level, 3),
            "temp": round(env.temperature, 1),
            "pressure": round(env.pressure, 1),
            "o2": round(env.oxygen_level, 1),
            "heart_rate": jack.vitals.heart_rate,
            "stress": round(jack.stress_level, 1),
            "battery": round(power.backup_battery.charge_percent, 1),
            "power_draw": round(power.total_load, 1),
            "inventory": inventory_names
        }

if __name__ == "__main__":
    # Simple CLI test
    engine = GameEngine()
    print("Engine Initialized. Running 5 ticks...")
    for _ in range(5):
        print(engine.tick())
        time.sleep(1)
