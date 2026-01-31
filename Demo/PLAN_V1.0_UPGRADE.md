# Project: CARGO - V1.0 Upgrade Plan (Engineering Implementation)

**Status:** Draft
**Target:** Update MVP to match "The Martian" Engineering Spec (V1.0)
**Reference:** `/Users/starryyu/Documents/Cargo/Kimi_Agent_火星协作游戏协议/`

---

## 📅 Phased Execution Roadmap

### Phase 1: Core Simulation & State Machine (The Physics Engine)
**Goal:** Replace the simple placeholder physics with the Hard Sci-Fi simulation engine defined in `cargo_physics_state.md`.

- [ ] **1.1 Define Global State (Single Source of Truth)**
    - Create `MVP/state_schema.py` using Pydantic.
    - Implement the full nested structure:
        - `EnvironmentState` (Atmosphere: ppO2, ppCO2, Pressure; Thermal: Temp, Insulation)
        - `SystemState` (Power: Battery, Output; LifeSupport: Scrubber status)
        - `SurvivorState` (Health, BPM, Stress, Calories)
    - **Constraint:** Must align exactly with `cargo_physics_state.md` JSON structure.

- [ ] **1.2 Implement Physics Subsystems**
    - Refactor `MVP/physics_engine.py` into modular classes:
        - `AtmosphereSystem`: Implement Ideal Gas Law ($PV=nRT$) and gas mixing logic.
        - `ThermalSystem`: Implement Newton's Law of Cooling and heat generation (body heat + equipment).
        - `PowerSystem`: Battery drain/charge curves and critical load management.
    - **Constraint:** Simulation tick rate set to 1Hz (1 second per tick).

- [ ] **1.3 The Game Loop (Tick Manager)**
    - Update `MVP/server.py` to run a background `TickManager`.
    - Logic: `State(t+1) = Physics(State(t)) + PlayerAction(Effect)`.

### Phase 2: The "Jack" Persona & AI Middleware (The Brain)
**Goal:** Upgrade the AI from a generic assistant to the "Blue-collar Survivor" defined in `Jack_System_Prompt.md`.

- [ ] **2.1 System Prompt Injection**
    - Update `MVP/prompts.py` (or `survivor_jack.py`) with the V1.0 System Prompt.
    - Implement the "Dynamic Context Block" injection (inserting current sensor readings into the prompt).

- [ ] **2.2 Intent Analysis Layer (Safety Protocol)**
    - Implement the "Level 1-3" safety check logic in `MVP/ai_middleware.py`.
    - **Logic:** Before Jack executes an action, the AI checks:
        1. Is it physically possible? (e.g., "Open airlock" when pressurized)
        2. Is it suicidal? (Safety Check)
        3. Does Jack understand it? (Knowledge Check)

### Phase 3: Gameplay Scenarios & Puzzles (The Content)
**Goal:** Implement "Puzzle 1: The CO2 Crisis" (MacGyver Moment) as the playable tutorial.

- [ ] **3.1 Scenario Scripting**
    - Initialize `GameState` with the "Crisis Start" values (High ppCO2, Scrubber Broken).
    - Hardcode the success criteria for the CO2 Scrubber fix (e.g., specific item combination: "Tape" + "Filter" + "Hose").

- [ ] **3.2 Item & Inventory System**
    - Define the `Inventory` list in `GameState`.
    - Implement `combine_items(item_a, item_b)` logic in the backend.

### Phase 4: Frontend Synchronization (The Interface)
**Goal:** Update the React frontend to visualize the complex telemetry and new data structures.

- [ ] **4.1 Telemetry Dashboard 2.0**
    - Update `frontend/src/types/game.ts` to match the new Python Pydantic models.
    - Refactor `AdvisorMonitor.tsx` to display:
        - Partial Pressures (ppO2, ppCO2) in kPa.
        - Battery Graph (Amps/Voltage).
        - Stress Level indicator.

- [ ] **4.2 Manual Content Update**
    - Update `frontend/src/data/manualData.ts` with the specific "CO2 Scrubber Repair Guide" (Technical schematics and text).

---

## 🛠️ Tech Stack & Architecture Changes
- **Backend:** Python 3.11+, FastAPI, Pydantic (Strict Types), AsyncIO.
- **Frontend:** React, TypeScript, WebSocket (Native).
- **AI:** Gemini-3-Pro (via Google Generative AI SDK).
