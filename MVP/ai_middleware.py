"""
@file ai_middleware.py
@description Intent Recognition & Safety Layer (Level 1-3) for Project: CARGO.
@module AIInterpreter
"""

import json
import re
from typing import Dict, Optional, List, Any
from enum import Enum

class ActionType(Enum):
    MOVE = "move"
    INTERACT = "interact"
    USE_ITEM = "use_item"
    EXAMINE = "examine"
    COMMUNICATE = "communicate"
    WAIT = "wait"
    CANCEL = "cancel"
    UNKNOWN = "unknown"

class DangerLevel(Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CommandInterpreter:
    def __init__(self, provider, client, model):
        self.provider = provider
        self.client = client
        self.model = model
        
        # --- Level 1: Syntax Safety Rules ---
        self.DANGER_KEYWORDS = {
            "critical": [
                "explode", "detonate", "suicide", "jump off", "burn", "fire", 
                "short circuit", "lick", "eat", "drink poison", "remove helmet", "open airlock"
            ],
            "high": [
                "break", "smash", "destroy", "steal", "attack", "cut wire"
            ]
        }

    def analyze_intent(self, user_input: str, context: Dict) -> Dict:
        """
        Main Entry Point: Converts natural language to structured intent + safety check.
        """
        # 1. Level 1: Keyword Check (Fast Fail)
        keyword_safety = self._check_dangerous_keywords(user_input)
        if keyword_safety["level"] == DangerLevel.CRITICAL:
            return {
                "is_safe": False,
                "danger_reason": f"CRITICAL SAFETY VIOLATION: {keyword_safety['reason']}",
                "intent": None
            }

        # 2. Level 2: LLM Semantic Analysis
        intent = self._parse_semantic_llm(user_input, context)
        
        # 3. Level 3: Contextual Safety Check
        context_safety = self._check_context_safety(intent, context)
        
        if not context_safety["is_safe"]:
             return {
                "is_safe": False,
                "danger_reason": context_safety["reason"],
                "intent": intent
            }

        return {
            "is_safe": True,
            "danger_reason": None,
            "intent": intent
        }

    def _check_dangerous_keywords(self, text: str) -> Dict:
        text_lower = text.lower()
        for keyword in self.DANGER_KEYWORDS["critical"]:
            if keyword in text_lower:
                return {"level": DangerLevel.CRITICAL, "reason": f"Detected fatal keyword: '{keyword}'"}
        return {"level": DangerLevel.NONE, "reason": None}

    def _parse_semantic_llm(self, text: str, context: Dict) -> Dict:
        """
        Uses LLM to parse intent into structured JSON.
        """
        schema = """
        {
            "action": "move|interact|use_item|examine|communicate|wait|unknown",
            "target": "target_object_name_or_id",
            "parameters": { "type": "press|pull|open|etc", ... }
        }
        """
        
        prompt = f"""
        Analyze the following player command for a Mars Survival Game.
        Context: {json.dumps(context.get('telemetry', {}))}
        Command: "{text}"
        
        Return ONLY a JSON object matching this schema:
        {schema}
        """
        
        try:
            # Call LLM (Synchronous for MVP, should be async in prod)
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "system", "content": "You are a JSON parser."},
                              {"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                content = response.choices[0].message.content
            elif self.provider == "google":
                model_instance = self.client.GenerativeModel(self.model)
                response = model_instance.generate_content(prompt)
                content = response.text
            else:
                return {"action": "unknown"}

            # Clean markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
                
            return json.loads(content)
        except Exception as e:
            print(f"[MIDDLEWARE] LLM Parse Error: {e}")
            return {"action": "unknown"}

    def _check_context_safety(self, intent: Dict, context: Dict) -> Dict:
        """
        Level 3: Checks if the action is safe GIVEN the current state.
        """
        action = intent.get("action")
        target = (intent.get("target") or "").lower()
        telemetry = context.get("telemetry", {})
        
        # Rule 1: High Pressure/Toxic Atmosphere -> Cannot remove suit/helmet
        if target and ("helmet" in target or "suit" in target):
            if action in ["remove", "take off", "open"] or intent.get("parameters", {}).get("type") in ["open", "remove"]:
                if telemetry.get("pressure", 100) < 60:
                    return {"is_safe": False, "reason": "Depressurization risk! Cannot remove suit."}
                if telemetry.get("co2", 0) > 1.0:
                    return {"is_safe": False, "reason": "Toxic atmosphere! Keep helmet on."}

        # Rule 2: Electrical Safety
        if target and ("wire" in target or "panel" in target):
            if action == "interact" and intent.get("parameters", {}).get("type") in ["cut", "touch"]:
                # Assume high voltage for MVP
                return {"is_safe": False, "reason": "High voltage detected! Insulated tools required."}

        # Rule 3: Airlock Safety
        if target and ("airlock" in target or "door" in target):
            if action == "interact" and intent.get("parameters", {}).get("type") == "open":
                 if telemetry.get("pressure", 100) > 10 and "external" in target: # Simplified logic
                     return {"is_safe": False, "reason": "Pressure differential too high to open door."}

        return {"is_safe": True, "reason": None}
