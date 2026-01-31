"""
@file physics_engine.py
@description Handles the hard sci-fi physics simulation for the habitat environment (O2, Pressure, Temp) using the V1.0 Engineering Spec.
@module PhysicsSimulation
"""

import math
import random
import time
from typing import Dict, List, Optional
from MVP.state_schema import GameState

def lerp(start, end, t):
    return start + (end - start) * t

def clamp(val, min_val, max_val):
    return max(min_val, min(val, max_val))

class SensoryTranslator:
    """
    Translates numerical state into human-readable sensory descriptions.
    """
    def translate(self, state: GameState) -> str:
        descriptions = []
        
        # Environment
        env_desc = self.translate_environment(state)
        if env_desc: descriptions.append(env_desc)
        
        # Jack Physiology
        jack_desc = self.translate_jack_physiology(state)
        if jack_desc: descriptions.append(jack_desc)
        
        # System
        sys_desc = self.translate_system_status(state)
        if sys_desc: descriptions.append(sys_desc)
        
        return self.compile_prompt(descriptions, state)

    def translate_environment(self, state: GameState) -> Optional[str]:
        env = state.environment
        parts = []
        
        # Temp
        if env.temperature > 50:
            parts.append("The air is scorching hot, burning your skin.")
        elif env.temperature > 35:
            parts.append("It's sweltering in here, sweat is pouring down your face.")
        elif env.temperature < -20:
            parts.append("It's freezing cold, your breath turns to ice instantly.")
        elif env.temperature < 5:
            parts.append("You can see your breath, it's getting very cold.")
            
        # Pressure/O2
        o2_pp = env.pressure * (env.oxygen_level / 100.0)
        if o2_pp < 12:
            parts.append("You feel dizzy and lightheaded (Hypoxia).")
        if env.pressure < 70:
            parts.append("Your ears are popping painfully.")
            
        # CO2
        if env.co2_level > 3.0:
            parts.append("You have a splitting headache and feel nauseous (CO2 Poisoning).")
        elif env.co2_level > 1.0:
            parts.append(" The air feels stale and heavy.")
            
        return " ".join(parts) if parts else None

    def translate_jack_physiology(self, state: GameState) -> Optional[str]:
        jack = state.jack
        parts = []
        if jack.stress_level > 80:
            parts.append("Your heart is pounding out of your chest.")
        if jack.fatigue > 80:
            parts.append("You are exhausted, barely able to keep your eyes open.")
        return " ".join(parts) if parts else None

    def translate_system_status(self, state: GameState) -> Optional[str]:
        parts = []
        if not state.power_system.main_bus.online:
            parts.append("Total blackout. Only emergency lights are blinking.")
        elif state.power_system.backup_battery.charge_percent < 20:
            parts.append("Low battery alarm is beeping.")
        if not state.life_support.air_circulation.status:
            parts.append("The ventilation fans have stopped. It's deadly quiet.")
        return " ".join(parts) if parts else None

    def compile_prompt(self, descriptions: List[str], state: GameState) -> str:
        base = "\n".join(descriptions)
        telemetry = (
            f"\n[HUD DATA] "
            f"TEMP: {state.environment.temperature:.1f}C | "
            f"PRESS: {state.environment.pressure:.1f}kPa | "
            f"O2: {state.environment.oxygen_level:.1f}% | "
            f"CO2: {state.environment.co2_level:.2f}% | "
            f"HR: {state.jack.vitals.heart_rate}bpm"
        )
        return base + telemetry

class PhysicsSimulator:
    """
    Project: CARGO Physics Engine V1.0
    Simulation Step: 1 second per tick.
    """
    
    def __init__(self, initial_state: GameState):
        self.state = initial_state
        self.sensory_translator = SensoryTranslator()
        self.previous_temperature = initial_state.environment.temperature

    def simulation_step(self, delta_time: float = 1.0) -> str:
        """
        Advances the simulation by delta_time seconds.
        Returns sensory feedback string.
        """
        # 1. Environment (Gas Laws)
        self.update_environment(delta_time)
        
        # 2. Power System
        self.update_power_system(delta_time)
        
        # 3. Physiology
        self.update_jack_physiology(delta_time)
        
        # Update metadata
        self.state.metadata.simulation_tick += 1
        self.state.metadata.game_time_seconds += delta_time
        
        return self.sensory_translator.translate(self.state)

    def update_environment(self, delta_time: float):
        env = self.state.environment
        ls = self.state.life_support
        
        # --- O2 & CO2 ---
        # Base consumption: ~0.0008% per sec for 500m3 volume
        base_o2_consumption = 0.0008 
        o2_consumption = base_o2_consumption # Could add activity multipliers
        
        co2_production = o2_consumption * 0.8 # RQ = 0.8
        
        # Scrubber
        co2_scrubbing = 0.0
        if ls.co2_scrubber.status == "on" and self.has_power():
            co2_scrubbing = ls.co2_scrubber.scrub_rate / 60.0 # Convert min to sec
            
        # O2 Gen
        o2_replenishment = 0.0
        if ls.o2_generator.status == "on" and self.has_power():
            o2_replenishment = ls.o2_generator.output_rate / 60.0
            
        env.oxygen_level = clamp(env.oxygen_level + (o2_replenishment - o2_consumption) * delta_time, 0.0, 100.0)
        env.co2_level = clamp(env.co2_level + (co2_production - co2_scrubbing) * delta_time, 0.0, 100.0)
        
        # --- Temperature (Newton's Law of Cooling) ---
        # Heat Sources
        jack_heat = 100.0 # Watts
        equip_heat = self.state.power_system.total_load * 0.1
        heater_heat = ls.heater.output_watts if (ls.heater.status and self.has_power()) else 0.0
        
        total_heat_input = jack_heat + equip_heat + heater_heat
        
        # Heat Loss (Simplified Radiation + Conduction)
        # Assuming outside is very cold (-270C space / -60C Mars)
        temp_diff = env.temperature - (-60.0) 
        heat_loss = temp_diff * 50.0 # Arbitrary insulation factor
        
        net_heat = total_heat_input - heat_loss
        
        # Heat Capacity of Air (approx 500m3 ~ 600kg)
        air_mass = 600.0
        specific_heat = 1005.0 # J/kgK
        
        temp_change = (net_heat * delta_time) / (air_mass * specific_heat)
        env.temperature += temp_change
        
        # --- Pressure (Gas Law P ~ T) ---
        # If temp changes, pressure changes (PV=nRT -> P ~ T)
        if env.temperature != self.previous_temperature:
            temp_ratio = (env.temperature + 273.15) / (self.previous_temperature + 273.15)
            env.pressure *= temp_ratio
            self.previous_temperature = env.temperature
            
        # Leaks
        for breach in env.breaches:
            if not breach.is_sealed:
                # Simplified leak rate
                leak_rate = 0.1 * delta_time # kPa per sec per breach (simplified)
                env.pressure = max(0.0, env.pressure - leak_rate)

    def update_power_system(self, delta_time: float):
        power = self.state.power_system
        ls = self.state.life_support
        
        # Calculate Load
        load = 100.0 # Base load
        if ls.co2_scrubber.status == "on": load += ls.co2_scrubber.power_draw
        if ls.o2_generator.status == "on": load += ls.o2_generator.power_draw
        if ls.heater.status: load += ls.heater.power_draw
        if ls.air_circulation.status: load += ls.air_circulation.power_draw
        
        power.total_load = load
        
        # Solar / Battery Logic
        solar_output = power.solar_panels.output_watts if power.solar_panels.online else 0.0
        # Simplified: if solar > load, charge battery; else drain battery
        if solar_output >= load:
            excess = solar_output - load
            # Charge logic here (omitted for brevity)
            power.main_bus.online = True
        else:
            deficit = load - solar_output
            # Drain battery
            drain_wh = (deficit * delta_time) / 3600.0
            power.backup_battery.capacity_wh -= drain_wh
            if power.backup_battery.capacity_wh <= 0:
                power.backup_battery.capacity_wh = 0
                power.main_bus.online = False # Blackout

    def update_jack_physiology(self, delta_time: float):
        jack = self.state.jack
        env = self.state.environment
        
        # Heart Rate
        target_hr = 75
        if jack.stress_level > 50: target_hr += 20
        if env.co2_level > 1.0: target_hr += 30
        if env.oxygen_level < 18.0: target_hr += 20
        
        jack.vitals.heart_rate = int(lerp(jack.vitals.heart_rate, target_hr, 0.1 * delta_time))
        
        # Stress
        stress_inc = 0.0
        if env.co2_level > 1.0: stress_inc += 1.0
        if env.temperature > 35 or env.temperature < 5: stress_inc += 0.5
        
        jack.stress_level = clamp(jack.stress_level + stress_inc * delta_time, 0.0, 100.0)

    def has_power(self) -> bool:
        return self.state.power_system.main_bus.online
