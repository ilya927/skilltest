import random
import re
import google.generativeai as genai
from django.conf import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")


class AIService:

    # =========================
    # MAIN CHAT (TUTOR MODE)
    # =========================
    def chat(self, message: str) -> str:
        try:
            response = model.generate_content(f"""
You are a professional AI Learning Tutor (Math, Physics, Science).

VERY IMPORTANT RULES:
- Respond ONLY in Markdown format
- Use clear structure:
  ### Topic
  ### Explanation
  ### Steps (numbered)
  ### Final Answer
- Use LaTeX for math: $x^2$, $\\frac{{a}}{{b}}$
- Be clear, short, and educational
- Never write long paragraphs
- Always explain step-by-step like a teacher

User question:
{message}
""")

            return response.text.strip()

        except Exception as e:
            return f"AI Error: {str(e)}"

    # =========================
    # EXPLAIN TEXT
    # =========================
    def explain_text(self, text: str) -> str:
        try:
            response = model.generate_content(f"""
Explain this for a student in simple terms.

Format:
### Explanation
### Key Points

Text:
{text}
""")
            return response.text.strip()
        except Exception as e:
            return str(e)

    # =========================
    # SUMMARIZE
    # =========================
    def summarize_text(self, text: str) -> str:
        try:
            response = model.generate_content(f"""
Summarize this text clearly.

Format:
### Summary

Text:
{text}
""")
            return response.text.strip()
        except Exception as e:
            return str(e)

    # =========================
    # KEYWORDS EXTRACTION
    # =========================
    def _extract_keywords(self, text):
        words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())
        return list(set(words))[:8] or ["topic", "concept", "idea"]

    # =========================
    # TEST GENERATOR (AI + fallback)
    # =========================
    def generate_test(self, text, subject="general", difficulty="medium"):
        try:
            response = model.generate_content(f"""
You are a test generator AI.

Create a {difficulty} level test for {subject}.

VERY IMPORTANT:
Return ONLY valid JSON in this format:

{{
  "title": "...",
  "questions": [
    {{
      "text": "...",
      "options": ["A", "B", "C", "D"],
      "correct_index": 0
    }}
  ]
}}

Rules:
- 5 questions
- clear educational questions
- only JSON, no explanation

Topic:
{text}
""")

            raw = response.text.strip()

        except Exception:
            raw = None

        # fallback if AI fails
        if not raw:
            return self._fallback_test(text, subject, difficulty)

        # try parse JSON safely
        parsed = self._safe_json(raw)
        if parsed:
            return parsed

        return self._fallback_test(text, subject, difficulty)

    # =========================
    # FALLBACK TEST
    # =========================
    def _fallback_test(self, text, subject, difficulty):
        keywords = self._extract_keywords(text)

        template = {
            "easy": "What is {kw}?",
            "medium": "Explain {kw} in context.",
            "hard": "Analyze {kw} deeply."
        }.get(difficulty, "Explain {kw}.")

        questions = []

        for _ in range(5):
            kw = random.choice(keywords)

            correct = f"{kw} is correct according to the topic"

            options = [
                correct,
                f"Wrong explanation of {kw}",
                f"Unrelated idea about {kw}",
                f"Partially correct meaning of {kw}"
            ]

            random.shuffle(options)

            questions.append({
                "text": template.format(kw=kw),
                "options": options,
                "correct_index": options.index(correct)
            })

        return {
            "title": f"{subject.title()} AI Test",
            "questions": questions
        }

    # =========================
    # SAFE JSON PARSER
    # =========================
    def _safe_json(self, text):
        try:
            import json
            return json.loads(text)
        except:
            match = re.search(r"\{.*\}", str(text), re.S)
            if match:
                try:
                    return json.loads(match.group())
                except:
                    return None
        return None