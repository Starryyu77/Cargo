"""
@file state_schema.py
@description Pydantic models defining the complete GameState for Project: CARGO V1.0.
@module PhysicsSimulation
"""

from typing import List, Optional, Dict, Literal
from pydantic import BaseModel, Field

# --- Sub-models ---

class Breach(BaseModel):
    id: str
    location: str
    size_mm: float
    is_sealed: bool

class EnvironmentState(BaseModel):
    oxygen_level: float = Field(21.0, description="Percentage 0-100")
    temperature: float = Field(22.0, description="Celsius")
    pressure: float = Field(101.325, description="kPa")
    co2_level: float = Field(0.04, description="Percentage")
    radiation: float = Field(0.0, description="mSv/h")
    humidity: float = Field(50.0, description="Percentage")
    volume: float = Field(500.0, description="m3")
    hull_integrity: float = Field(100.0, description="Percentage")
    breaches: List[Breach] = []

class MainBus(BaseModel):
    online: bool = True
    voltage: float = 28.0
    current_draw: float = 0.0
    max_capacity: float = 5000.0

class BackupBattery(BaseModel):
    charge_percent: float = 100.0
    capacity_wh: float = 2000.0
    health: float = 100.0
    discharge_rate: float = 0.0
    temperature: float = 25.0

class SolarPanels(BaseModel):
    online: bool = True
    efficiency: float = 85.0
    angle_degrees: float = 45.0
    output_watts: float = 3500.0
    dust_coverage: float = 15.0

class CircuitBreakers(BaseModel):
    life_support: bool = True
    communications: bool = True
    lighting: bool = True
    auxiliary: bool = True

class PowerSystemState(BaseModel):
    main_bus: MainBus = MainBus()
    backup_battery: BackupBattery = BackupBattery()
    solar_panels: SolarPanels = SolarPanels()
    circuit_breakers: CircuitBreakers = CircuitBreakers()
    total_load: float = 0.0

class ComponentStatus(BaseModel):
    status: str # on, off, broken, maintenance, auto
    power_draw: float = 0.0

class CO2Scrubber(ComponentStatus):
    status: Literal["on", "off", "broken", "maintenance"] = "on"
    filter_life_percent: float = 100.0
    scrub_rate: float = 0.5 # %CO2/min
    power_draw: float = 200.0

class O2Generator(ComponentStatus):
    status: Literal["on", "off", "broken"] = "on"
    output_rate: float = 0.3 # %O2/min
    reservoir_pressure: float = 2000.0 # kPa
    power_draw: float = 150.0

class Heater(ComponentStatus):
    status: bool = False
    target_temp: float = 22.0
    output_watts: float = 2000.0
    power_draw: float = 0.0

class AirCirculation(ComponentStatus):
    status: bool = True
    fan_speed: float = 50.0
    power_draw: float = 100.0

class HumidityControl(ComponentStatus):
    status: Literal["on", "off", "auto"] = "auto"
    target_humidity: float = 50.0
    power_draw: float = 50.0

class LifeSupportState(BaseModel):
    co2_scrubber: CO2Scrubber = CO2Scrubber()
    o2_generator: O2Generator = O2Generator()
    heater: Heater = Heater()
    air_circulation: AirCirculation = AirCirculation()
    humidity_control: HumidityControl = HumidityControl()

class Vitals(BaseModel):
    heart_rate: int = 75
    oxygen_saturation: float = 98.0
    body_temperature: float = 37.0
    blood_pressure: str = "120/80"
    respiration_rate: int = 16

class InventoryItem(BaseModel):
    item_id: str
    name: str
    quantity: int
    charges: Optional[int] = None

class SuitState(BaseModel):
    wearing: bool = False
    oxygen_supply: float = 0.0
    integrity: float = 100.0

class JackState(BaseModel):
    location: str = "command_module"
    health: float = 100.0
    status: Literal["conscious", "dizzy", "unconscious", "dead"] = "conscious"
    vitals: Vitals = Vitals()
    stress_level: float = 15.0
    fatigue: float = 20.0
    hydration: float = 85.0
    calories_remaining: float = 2000.0
    inventory: List[InventoryItem] = []
    active_effects: List[str] = []
    suit: SuitState = SuitState()

class AntennaAngle(BaseModel):
    azimuth: float = 180.0
    elevation: float = 45.0

class Transmitter(BaseModel):
    status: Literal["on", "off"] = "on"
    frequency: float = 145.8
    power_watts: float = 10.0

class Receiver(BaseModel):
    status: Literal["on", "off"] = "on"
    squelch: float = 0.3

class CommunicationsState(BaseModel):
    signal_strength: float = 85.0
    antenna_angle: AntennaAngle = AntennaAngle()
    transmitter: Transmitter = Transmitter()
    receiver: Receiver = Receiver()
    noise_level: float = 0.2
    last_contact_timestamp: str = ""

class CargoBayState(BaseModel):
    door_status: Literal["sealed", "unsealed", "open"] = "sealed"
    pressure_equalized: bool = True
    cargo_items: List[str] = []
    structural_damage: float = 0.0

class EventsState(BaseModel):
    active: List[str] = []
    history: List[str] = []
    pending_triggers: List[str] = []

class GameMetadata(BaseModel):
    simulation_tick: int = 0
    game_time_seconds: float = 0.0
    last_update_timestamp: str = ""
    scenario_id: str = "default"

# --- Root State ---

class GameState(BaseModel):
    metadata: GameMetadata = GameMetadata()
    environment: EnvironmentState = EnvironmentState()
    power_system: PowerSystemState = PowerSystemState()
    life_support: LifeSupportState = LifeSupportState()
    jack: JackState = JackState()
    communications: CommunicationsState = CommunicationsState()
    cargo_bay: CargoBayState = CargoBayState()
    events: EventsState = EventsState()
