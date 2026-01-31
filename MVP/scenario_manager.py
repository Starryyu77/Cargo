"""
@file scenario_manager.py
@description Manages specific gameplay scenarios, puzzles, and item interactions (MacGyver Moments).
@module ContentEngine
"""

from typing import Dict, List, Optional
from MVP.state_schema import GameState, InventoryItem

class PuzzleLogic:
    """Base class for puzzle logic handlers"""
    def check_trigger(self, state: GameState) -> bool:
        return False
    
    def apply_effect(self, state: GameState, action: str, target: str) -> str:
        return ""

class CO2CrisisPuzzle(PuzzleLogic):
    """
    Puzzle 1: The CO2 Crisis (MacGyver Moment)
    Goal: Fix the broken CO2 Scrubber using Duct Tape + Plastic Hose + Filter.
    """
    def __init__(self):
        self.is_active = False
        self.has_fixed = False
        
        # Initial locations of items (simulated for MVP)
        self.world_items = {
            "warehouse_shelf": ["duct_tape", "plastic_hose"],
            "locker": ["spare_filter_cartridge"]
        }

    def start_scenario(self, state: GameState):
        """Sets up the initial broken state"""
        self.is_active = True
        state.life_support.co2_scrubber.status = "broken"
        state.environment.co2_level = 2.5 # High initial CO2 to create urgency
        state.jack.location = "hab_module"
        state.metadata.scenario_id = "co2_crisis"
        
        # Clear inventory
        state.jack.inventory = []

    def handle_interaction(self, state: GameState, action: str, target: str) -> str:
        if not self.is_active or self.has_fixed:
            return ""

        target = target.lower()
        
        # 1. Searching / Looking
        if action == "search" or action == "examine":
            # General Room Description (Critical for discovery)
            if target == "" or "room" in target or "around" in target:
                return "I'm in the Hab Module storage area. It's a mess. There's a **warehouse shelf** overflowing with junk on the left, and my personal **locker** on the right. The air scrubber is humming... no, wait, it's making a rattling noise."

            if "shelf" in target or "warehouse" in target:
                if "duct_tape" in self.world_items["warehouse_shelf"]:
                    self._add_to_inventory(state, "duct_tape", "Duct Tape")
                    self._add_to_inventory(state, "plastic_hose", "Plastic Hose")
                    self.world_items["warehouse_shelf"] = []
                    return "I found a roll of heavy-duty duct tape and some old plastic tubing."
                else:
                    return "The shelf is empty."
            
            if "locker" in target:
                if "spare_filter_cartridge" in self.world_items["locker"]:
                    self._add_to_inventory(state, "spare_filter_cartridge", "CO2 Filter (Square)")
                    self.world_items["locker"] = []
                    return "Found a spare CO2 filter. But wait... it's square. The slot is round. Damn it."
                else:
                    return "Just some dirty socks in here."

        # 2. Fixing the Scrubber (The MacGyver Moment)
        if action == "use_item" or action == "combine":
            # Check if player is trying to fix the scrubber
            if "scrubber" in target or "filter" in target:
                inv_ids = [i.item_id for i in state.jack.inventory]
                required = ["duct_tape", "plastic_hose", "spare_filter_cartridge"]
                
                if all(req in inv_ids for req in required):
                    self.has_fixed = True
                    state.life_support.co2_scrubber.status = "on"
                    state.life_support.co2_scrubber.scrub_rate = 0.8 # Boosted rate
                    return "Okay, I taped the square filter to the round hole using the hose as a seal. It's ugly, but I hear the fans spinning up! CO2 levels dropping!"
                else:
                    missing = [r for r in required if r not in inv_ids]
                    return f"I can't fix it yet. I have the filter, but it doesn't fit. I need something to seal it. Missing: {missing}"

        return ""

    def _add_to_inventory(self, state: GameState, item_id: str, name: str):
        state.jack.inventory.append(InventoryItem(item_id=item_id, name=name, quantity=1))

class ScenarioManager:
    def __init__(self, state: GameState):
        self.state = state
        self.puzzles = {
            "co2_crisis": CO2CrisisPuzzle()
        }
        self.active_puzzle_id = None

    def load_scenario(self, scenario_id: str):
        if scenario_id in self.puzzles:
            self.puzzles[scenario_id].start_scenario(self.state)
            self.active_puzzle_id = scenario_id
            print(f"[SCENARIO] Loaded {scenario_id}")

    def process_action(self, intent: Dict) -> Optional[str]:
        """
        Passes the intent to the active puzzle to see if it triggers a scripted event.
        Returns a narrative string if handled, else None.
        """
        if not self.active_puzzle_id:
            return None
        
        puzzle = self.puzzles[self.active_puzzle_id]
        action = intent.get("action")
        target = intent.get("target") or ""
        
        return puzzle.handle_interaction(self.state, action, target)
