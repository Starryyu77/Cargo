# PROJECT: CARGO

**"You are Mission Control. He is alone on Mars."**

PROJECT: CARGO is an immersive, text-based survival simulation game powered by LLMs (Large Language Models) and a hard sci-fi physics engine. You play as a mission control operator guiding **Jack**, a blue-collar cargo hauler stranded in a failing habitat on Mars.

Your goal: Interpret real-time telemetry, guide Jack through technical repairs using simple language, and keep him alive against rising CO2 levels, falling temperatures, and his own panic.

![Game Screenshot](./docs/screenshot.png) *(Note: Add a screenshot here after deployment)*

## 🚀 Features

*   **Real-Time Physics Engine**: A background simulation loop calculates gas partial pressures, thermal thermodynamics, and power consumption every second.
*   **LLM-Powered NPC**: Jack is not a scripted bot. He is a persona driven by Google Gemini Pro (or OpenAI), reacting dynamically to your instructions and his physiological state (stress, fatigue, hypoxia).
*   **Immersive Interface**: A retro-futuristic "Mission Control" terminal interface built with React and Tailwind CSS.
*   **"MacGyver" Moments**: Solve engineering puzzles by combining scavenged items (e.g., Duct Tape + Hose + Filter = CO2 Scrubber Fix).
*   **Single-Container Deployment**: Backend (FastAPI) and Frontend (React/Vite) are bundled into a single Docker container for easy deployment on Render/Railway.

## 🛠️ Tech Stack

*   **Backend**: Python 3.10+, FastAPI, Uvicorn, WebSockets.
*   **AI/LLM**: Google Gemini 1.5/2.0 Pro (via `google-generativeai`) or OpenAI API.
*   **Frontend**: React, TypeScript, Vite, Tailwind CSS.
*   **Infrastructure**: Docker, WebSocket for real-time bi-directional communication.

## 📦 Installation & Local Development

### Prerequisites
*   Python 3.10+
*   Node.js 18+
*   Google Gemini API Key (or OpenAI Key)

### 1. Clone the Repository
```bash
git clone https://github.com/Starryyu77/Cargo.git
cd Cargo
```

### 2. Backend Setup
Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Set up your API Key:
Create a file named `MVP/api_key.txt` or set an environment variable `GOOGLE_API_KEY`.
```bash
export GOOGLE_API_KEY="your_api_key_here"
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run build
cd ..
```

### 4. Run the Game
This will start the backend server, which also serves the built frontend files.
```bash
python -m uvicorn MVP.server:app --host 0.0.0.0 --port 8000 --reload
```

Open your browser to `http://localhost:8000`.

## 🐳 Deployment (Docker)

The project includes a `Dockerfile` for single-container deployment.

1.  **Build the Image**:
    ```bash
    docker build -t cargo-game .
    ```
2.  **Run the Container**:
    ```bash
    docker run -p 8000:8000 -e GOOGLE_API_KEY="your_key" cargo-game
    ```

## 🎮 How to Play

1.  **Diagnosis**: Use the terminal to ask Jack about his status (`"Report status"`, `"How do you feel?"`).
2.  **Telemetry**: Monitor the HUD for CO2 levels (Keep below 1.0%!), Temperature, and Heart Rate.
3.  **Exploration**: Guide Jack to search the environment (`"Look around"`, `"Check the warehouse shelf"`).
4.  **Action**: Instruct him to perform repairs. Remember, he's untrained—use simple, clear English.

## 📄 License

MIT License.
