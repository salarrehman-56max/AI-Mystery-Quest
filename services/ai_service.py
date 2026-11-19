import os, json
from groq import Groq

class AIService:
    def __init__(self):
        self.key = os.getenv("GROQ_API_KEY")
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.client = None
        if self.key:
            try: self.client = Groq(api_key=self.key)
            except Exception: self.client = None
    @property
    def available(self): return self.client is not None

    def _ask(self, system, prompt, temperature=0.4):
        if not self.client: return None
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role":"system","content":system},{"role":"user","content":prompt}],
                temperature=temperature, max_tokens=900)
            return response.choices[0].message.content.strip()
        except Exception:
            return None

    def hint(self, case, level):
        return self._ask(
            "You are a fair mystery-game hint master. Give one concise progressive hint. Never name the culprit or reveal the solution.",
            f"Case: {case['title']}\nStory: {case['story']}\nSuspects: {json.dumps(case['suspects'])}\nEvidence: {json.dumps(case['evidence'])}\nHint level: {level}. Under 45 words.")

    def chat(self, case, question):
        prompt = f"Case data: {json.dumps({k:case[k] for k in ['title','story','suspects','evidence','puzzle']})}\nPlayer question: {question}"
        answer = self._ask(
            "You are Detective Quinn, a helpful assistant in a fictional detective game. Use only supplied case facts. Never invent evidence or reveal the culprit/solution before accusation. Suggest a next investigative step. Keep it concise.",
            prompt)
        if answer: return answer
        return ("Review the evidence alongside each suspect's alibi. Which details can be independently verified, "
                "and which statement conflicts with a physical clue? I can help you reason through the facts without revealing the solution.")

    def generate_case(self):
        raw = self._ask(
            "Create a fair fictional detective case. Output valid JSON only, no markdown.",
            "Return keys title,category,difficulty,location,story,solution,explanation,suspects,evidence,puzzle. "
            "Exactly 3 suspects with name,role,background,motive,alibi. Exactly 3 evidence items with id,title,description,related. "
            "Puzzle has question, options (4 strings), answer, explanation. solution must equal one suspect name.", 0.8)
        if not raw: return None
        try:
            obj = json.loads(raw[raw.find("{"):raw.rfind("}")+1])
            required = ["title","category","difficulty","location","story","solution","explanation","suspects","evidence","puzzle"]
            if not all(k in obj for k in required): return None
            if len(obj["suspects"]) != 3 or len(obj["evidence"]) < 2: return None
            if obj["solution"] not in [s["name"] for s in obj["suspects"]]: return None
            return obj
        except Exception: return None
