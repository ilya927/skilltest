import random
import re
import google.generativeai as genai
from django.conf import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")


class AIService:

    def chat(self, message: str) -> str:
        try:
            response = model.generate_content(f"""
You are a learning AI tutor.

Rules:
- Explain simply
- Be short and clear
- Help student understand

User: {message}
""")
            return response.text.strip()

        except Exception as e:
            return f"AI Error: {str(e)}"

    def explain_text(self, text: str) -> str:
        try:
            response = model.generate_content(f"""
Explain this for a student:

{text}
""")
            return response.text.strip()
        except Exception as e:
            return str(e)

    def summarize_text(self, text: str) -> str:
        try:
            response = model.generate_content(f"""
Summarize this text:

{text}
""")
            return response.text.strip()
        except Exception as e:
            return str(e)

    def _extract_keywords(self, text):
        words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())
        return list(set(words))[:8] or ["topic", "concept", "idea"]

    def generate_test(self, text, subject="general", difficulty="medium"):
        keywords = self._extract_keywords(text)

        difficulty_map = {
            "easy": "What is {kw}?",
            "medium": "Explain {kw} in context.",
            "hard": "Analyze {kw} deeply."
        }

        template = difficulty_map.get(difficulty, difficulty_map["medium"])

        questions = []

        for _ in range(5):
            kw = random.choice(keywords)

            correct = f"{kw} is correct according to the text"

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
                "correct_option": options.index(correct) + 1
            })

        return {
            "title": f"{subject.title()} AI Test",
            "questions": questions
        }