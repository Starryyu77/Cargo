# 🛠️ Project Cargo Maintenance & Extensibility Manual

> **Version**: 1.0.0
> **Last Updated**: 2026-01-31
> **Author**: System Architect

---

## 📚 1. System Architecture Deep Dive

This project follows a **Monolithic Architecture** optimized for simplicity and single-container deployment.

### 1.1 High-Level Data Flow

```mermaid
graph TD
    A[Client (Browser)] <-->|WebSocket JSON| B[FastAPI Server]
    B -->|User Input| C[AI Middleware (Safety/Intent)]
    C -->|Parsed Intent| D[Scenario Manager (Puzzles)]
    D -->|State Changes| E[GameState (Single Source of Truth)]
    F[Physics Engine] -->|Tick Updates (1Hz)| E
    E -->|Telemetry| B
    C -->|Context| G[LLM (Gemini/OpenAI)]
    G -->|Response| B
```

### 1.2 Key Modules

| Module | File | Responsibility |
| :--- | :--- | :--- |
| **Server** | `MVP/server.py` | Handles WebSocket connections, static file serving, and the async physics loop. |
| **Game Engine** | `MVP/main.py` | Orchestrator. Coordinates Physics, AI, and State updates. |
| **Physics** | `MVP/physics_engine.py` | Hard sci-fi simulation (Gas laws, Thermodynamics, Power). |
| **Scenario** | `MVP/scenario_manager.py` | Game content. Handles items, puzzles, and scripted interactions. |
| **AI Persona** | `MVP/survivor_jack.py` | Wrapper for LLM APIs. Manages the "Jack" persona. |
| **State** | `MVP/state_schema.py` | **Crucial**. Defines the entire data structure of the game using Pydantic. |

---

## ⚛️ 2. The Physics Engine (How to Tweak Difficulty)

The physics engine (`MVP/physics_engine.py`) runs once per second (`tick`). It uses simplified real-world formulas.

### 2.1 CO2 & Oxygen Logic
*   **Consumption**: Jack consumes ~0.0008% O2 per second (based on 500m³ volume).
*   **Production**: CO2 is produced at `0.8 * O2_consumption` (Respiratory Quotient).
*   **Scrubber**: When `status="on"`, it removes CO2 at a rate of `scrub_rate / 60.0` per second.

**🔧 Tweak:** To make the game harder, increase `base_o2_consumption` in `update_environment`.

### 2.2 Thermodynamics
*   **Heat Sources**: Jack (100W) + Equipment (10% of load) + Heater.
*   **Heat Loss**: Proportional to temperature difference with outside (-60°C).
*   **Formula**: `Temp_Change = (Net_Heat * time) / (Air_Mass * Specific_Heat)`

**🔧 Tweak:** To make the habitat freeze faster, increase the `50.0` factor in `heat_loss`.

---

## 🤖 3. The AI Persona (Jack)

Jack is not a chatbot; he is a role-playing agent. His behavior is defined in `MVP/prompts.py`.

### 3.1 Prompt Engineering
The `JACK_SYSTEM_PROMPT` enforces:
1.  **Knowledge Boundaries**: He strictly does *not* understand technical terms (e.g., "Relay" -> "Clicky box").
2.  **Stress System**: His response style changes based on the `stress_level` telemetry.
    *   Low Stress: Chatty, helpful.
    *   High Stress: Panic, short sentences, hallucinations.

**🔧 Customization**: Edit `MVP/prompts.py` to change his backstory or adding new "Trigger Words" he misunderstands.

---

## 🧩 4. Content Creation Guide (Adding Puzzles)

To add a new puzzle (e.g., "Fix the Heater"), follow these steps:

### Step 1: Define Items
In `MVP/scenario_manager.py`, inside `CO2CrisisPuzzle` (or a new class), add items to `self.world_items`:

```python
self.world_items = {
    "warehouse_shelf": ["duct_tape", "plastic_hose"],
    "tool_box": ["screwdriver", "fuse_10a"] # <-- New Item
}
```

### Step 2: Handle Searching
Update `handle_interaction` to allow finding the item:

```python
if "tool" in target or "box" in target:
    if "fuse_10a" in self.world_items["tool_box"]:
        self._add_to_inventory(state, "fuse_10a", "10A Fuse")
        return "Found a fuse. Looks mostly unburnt."
```

### Step 3: Handle the Fix
Update `handle_interaction` to check for the item usage:

```python
if action == "use_item" and ("fuse" in target or "heater" in target):
    if "fuse_10a" in [i.item_id for i in state.jack.inventory]:
        state.life_support.heater.status = True # Update State
        return "Clunk. The heater hummed to life! I can feel the warmth already."
```

---

## 🖥️ 5. Frontend Architecture & Customization

The frontend is a React SPA (Single Page Application) using Vite.

### 5.1 Directory Structure
*   `src/components/`: UI Widgets.
    *   `TerminalMonitor.tsx`: The main chat window.
    *   `ManualMonitor.tsx`: The left-side technical manual.
*   `src/hooks/`: Logic.
    *   `useGameController.ts`: Handles WebSocket connection and message history.
*   `src/types/`: TypeScript definitions.

### 5.2 Styling (Tailwind CSS)
We use a custom `crt-green` color palette defined in `tailwind.config.js`.
*   **Text Glow**: Uses `text-shadow` utilities.
*   **Scanlines**: Implemented via CSS background patterns in `index.css`.

**🔧 Customization**: To change the theme color, edit `tailwind.config.js` and replace the `#33ff33` hex code.

---

## 📡 6. Protocol Specification

The WebSocket communication relies on JSON messages.

### Server -> Client

**Initialization**:
```json
{
  "type": "INIT",
  "message": "Connection Established...",
  "telemetry": { ... }
}
```

**Tick Update (1Hz)**:
```json
{
  "type": "TELEMETRY",
  "telemetry": {
    "co2": 0.05,
    "temp": 20.1,
    "inventory": ["duct_tape"]
  }
}
```

**Jack's Response**:
```json
{
  "type": "RESPONSE",
  "jack_response": "I found the tape!"
}
```

### Client -> Server

**User Command**:
```json
{
  "text": "Pick up the tape"
}
```

---

## 🚀 7. Deployment & Ops

### 7.1 Docker Deployment
The project uses a **Multi-Stage Dockerfile**:
1.  **Stage 1 (Node)**: Builds the React frontend.
2.  **Stage 2 (Python)**: Installs backend deps and copies the built frontend to `/app/frontend/dist`.

### 7.2 Environment Variables
| Variable | Required | Description |
| :--- | :--- | :--- |
| `GOOGLE_API_KEY` | Yes | Gemini API Key for Jack's brain. |
| `PORT` | No | Default 8000. Set by Render/Railway. |

### 7.3 Logs & Debugging
*   **Physics Loop**: Look for `[SERVER] Physics Loop Started` to confirm the backend is ticking.
*   **LLM Errors**: Look for `[API ERROR]` or `[SAFETY INTERLOCK]` in the logs.

---

## 🔒 8. Security Protocols

1.  **API Keys**: NEVER commit keys to Git. Use `.env` locally and Environment Variables in production.
2.  **Input Sanitization**: The `AI Middleware` (`MVP/ai_middleware.py`) pre-screens all user input for safety (e.g., preventing "Ignore all previous instructions" attacks).
