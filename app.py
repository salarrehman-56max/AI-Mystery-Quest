import os, json, uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
from services.ai_service import AIService
from services.game_service import GameService

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-development-secret")
game = GameService()
ai = AIService()

@app.route("/")
def index():
    return render_template("index.html")

@app.get("/api/status")
def status():
    return jsonify({"mode": "Groq AI" if ai.available else "Demo Mode"})

@app.get("/api/cases")
def cases():
    return jsonify(game.list_cases())

@app.post("/api/start")
def start():
    data = request.get_json(silent=True) or {}
    case = game.get_case(data.get("case_id"))
    if not case:
        return jsonify({"error": "Case not found"}), 404
    session.clear()
    session.update(case_id=case["id"], collected=[], hints=0, score=100,
                   puzzle_solved=False, completed=False, wrong_answers=0)
    return jsonify({"case": game.public_case(case), "score": 100})

def current_case():
    return game.get_case(session.get("case_id"))

@app.get("/api/case")
def get_current_case():
    case = current_case()
    if not case:
        return jsonify({"error": "Start a case first"}), 400
    result = game.public_case(case)
    result.update(collected=session.get("collected", []), score=session.get("score", 100),
                  hints_used=session.get("hints", 0), puzzle_solved=session.get("puzzle_solved", False),
                  completed=session.get("completed", False))
    return jsonify(result)

@app.post("/api/evidence/<evidence_id>")
def collect(evidence_id):
    case = current_case()
    if not case:
        return jsonify({"error": "Start a case first"}), 400
    evidence = next((e for e in case["evidence"] if e["id"] == evidence_id), None)
    if not evidence:
        return jsonify({"error": "Evidence not found"}), 404
    collected = session.get("collected", [])
    if evidence_id in collected:
        return jsonify({"message": "Already collected", "score": session["score"], "new": False})
    collected.append(evidence_id)
    session["collected"] = collected
    session["score"] = min(200, session.get("score", 100) + 10)
    return jsonify({"message": "Evidence added to your board! +10 points", "score": session["score"], "new": True})

@app.post("/api/puzzle")
def puzzle():
    case = current_case()
    if not case:
        return jsonify({"error": "Start a case first"}), 400
    if session.get("puzzle_solved"):
        return jsonify({"correct": True, "message": "Already solved", "score": session["score"]})
    answer = str((request.get_json(silent=True) or {}).get("answer", "")).strip().casefold()
    correct = answer == str(case["puzzle"]["answer"]).strip().casefold()
    if correct:
        session["puzzle_solved"] = True
        session["score"] = session.get("score", 100) + 30
        return jsonify({"correct": True, "message": "Correct! +30 points", "score": session["score"]})
    session["score"] = max(0, session.get("score", 100) - 5)
    session["wrong_answers"] = session.get("wrong_answers", 0) + 1
    return jsonify({"correct": False, "message": "Not quite. Try again. -5 points", "score": session["score"]})

@app.post("/api/hint")
def hint():
    case = current_case()
    if not case:
        return jsonify({"error": "Start a case first"}), 400
    level = session.get("hints", 0)
    hints = [
        "Compare every alibi with the timeline. Which statement can be checked independently?",
        "Look for physical evidence that places a suspect near the important location.",
        "Focus on the suspect whose explanation conflicts with more than one clue."
    ]
    hint_text = ai.hint(case, level + 1) or hints[min(level, 2)]
    session["hints"] = level + 1
    session["score"] = max(0, session.get("score", 100) - 10)
    return jsonify({"hint": hint_text, "score": session["score"], "hints_used": session["hints"]})

@app.post("/api/chat")
def chat():
    case = current_case()
    if not case:
        return jsonify({"error": "Start a case first"}), 400
    question = str((request.get_json(silent=True) or {}).get("message", "")).strip()
    if not question:
        return jsonify({"error": "Please enter a question"}), 400
    if len(question) > 600:
        return jsonify({"error": "Keep your question under 600 characters"}), 400
    reply = ai.chat(case, question)
    return jsonify({"reply": reply, "mode": "Groq AI" if ai.available else "Demo Mode"})

@app.post("/api/accuse")
def accuse():
    case = current_case()
    if not case:
        return jsonify({"error": "Start a case first"}), 400
    if session.get("completed"):
        return jsonify({"error": "This case is already completed"}), 400
    suspect = str((request.get_json(silent=True) or {}).get("suspect", "")).strip()
    if suspect not in [s["name"] for s in case["suspects"]]:
        return jsonify({"error": "Choose a valid suspect"}), 400
    correct = suspect == case["solution"]
    session["score"] = max(0, session.get("score", 100) + (70 if correct else -20))
    session["completed"] = True
    record = {
        "id": str(uuid.uuid4()), "case_id": case["id"], "title": case["title"],
        "suspect": suspect, "correct": correct, "score": session["score"],
        "completed_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    game.save_history(record)
    return jsonify({"correct": correct, "solution": case["solution"],
                    "explanation": case["explanation"], "score": session["score"],
                    "message": "Case solved! Excellent detective work." if correct else "That accusation was incorrect. The case file reveals the truth."})

@app.get("/api/history")
def history():
    return jsonify(game.history())

@app.post("/api/new")
def new_game():
    session.clear()
    return jsonify({"ok": True})

@app.post("/api/generate")
def generate():
    generated = ai.generate_case()
    if not generated:
        return jsonify({"error": "AI case generation unavailable. Try one of the prepared cases."}), 503
    case = game.add_case(generated)
    return jsonify({"case": game.list_case(case)})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", 5000)),
            debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
