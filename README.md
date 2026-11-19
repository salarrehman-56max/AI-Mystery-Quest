# AI Mystery Quest – Interactive Detective Game

A Flask-based detective game. Investigate fictional cases, interview the case facts with Detective Quinn, collect evidence, solve puzzles, request hints, and submit your accusation.

## Features
- Three built-in cases across Easy, Medium, and Hard difficulty.
- Suspect profiles with background, motive, and alibi.
- Evidence collection and an investigation board.
- Puzzle challenges with score rewards and penalties.
- Progressive hints (10 points each).
- Detective Quinn chatbot, powered by Groq when configured.
- Optional AI-generated mystery cases.
- Demo Mode automatically works without a Groq API key.
- JSON-based case and investigation history storage.
- Responsive dark detective-themed interface.

## Requirements
- Python 3.9 or newer
- Internet connection only for installing packages and Groq AI features

## Windows PowerShell setup

```powershell
cd path\to\AI_Mystery_Quest
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

If PowerShell blocks activation, run this once for the current terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
venv\Scripts\Activate.ps1
```

Open **http://127.0.0.1:5000** in your browser.

## Enable Groq AI
1. Create an API key in your Groq account.
2. Open `.env` and set `GROQ_API_KEY=your_real_key`.
3. Optionally change `GROQ_MODEL` to a model available to your account.
4. Restart the app.

The API key is only read by the Python backend. Never commit `.env` to GitHub.

## Demo Mode
If `GROQ_API_KEY` is empty, the Groq package is unavailable, or an API request fails, the game continues using built-in cases and safe fallback hints/chat responses. AI case generation requires a working Groq API key; the prepared cases remain playable without it.

## Data files
- `data/cases.json`: built-in and generated cases. The app initializes default cases on first run if this file is empty.
- `data/history.json`: completed investigation history.

## Troubleshooting
- **`python` not found:** install Python and enable “Add Python to PATH”, then reopen PowerShell.
- **Activation blocked:** use the process-scoped execution policy command above, or run `venv\\Scripts\\python.exe app.py`.
- **`ModuleNotFoundError`:** activate the virtual environment and run `pip install -r requirements.txt`.
- **Port 5000 is busy:** set a different port before running, e.g. `$env:PORT=5001; python app.py`.
- **Groq not working:** verify the key in `.env`, check your account's model access and internet connection. The game should still work in Demo Mode.

## Project structure

```text
AI_Mystery_Quest/
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
├── data/
│   ├── cases.json
│   └── history.json
├── models/
│   ├── __init__.py
│   ├── case.py
│   ├── suspect.py
│   └── player.py
├── services/
│   ├── __init__.py
│   ├── ai_service.py
│   └── game_service.py
├── templates/
│   └── index.html
└── static/
    ├── css/style.css
    └── js/script.js
```
