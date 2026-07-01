import random
import re
import json
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
            prompt = (
                "You are a professional AI Learning Tutor (Math, Physics, Science).\n\n"
                "VERY IMPORTANT RULES:\n"
                "- Respond ONLY in clean Markdown text\n"
                "- DO NOT use LaTeX, $, {}, or special math symbols\n"
                "- Write math in simple words (example: x squared, a/b)\n"
                "- Use structure:\n"
                "### Topic\n"
                "### Explanation\n"
                "### Steps (numbered)\n"
                "### Final Answer\n"
                "- Be short, clear, educational\n\n"
                f"User question:\n{message}"
            )

            response = model.generate_content(prompt)

            return self._clean_text(response.text)

        except Exception as e:
            return f"AI Error: {str(e)}"

    # =========================
    # EXPLAIN TEXT
    # =========================
    def explain_text(self, text: str) -> str:
        try:
            prompt = (
                "Explain this for a student in simple terms.\n\n"
                "Format:\n"
                "### Explanation\n"
                "### Key Points\n\n"
                f"Text:\n{text}"
            )

            response = model.generate_content(prompt)
            return self._clean_text(response.text)

        except Exception as e:
            return str(e)

    # =========================
    # SUMMARIZE
    # =========================
    def summarize_text(self, text: str) -> str:
        try:
            prompt = (
                "Summarize this text clearly.\n\n"
                "Format:\n"
                "### Summary\n\n"
                f"Text:\n{text}"
            )

            response = model.generate_content(prompt)
            return self._clean_text(response.text)

        except Exception as e:
            return str(e)

    # =========================
    # TEST GENERATOR
    # =========================
    def generate_test(self, text, subject="general", difficulty="medium"):
        try:
            prompt = (
                "You are a test generator AI.\n\n"
                f"Create a {difficulty} level test for {subject}.\n\n"
                "VERY IMPORTANT:\n"
                "Return ONLY valid JSON in this format:\n\n"
                "{\n"
                '  "title": "string",\n'
                '  "questions": [\n'
                "    {\n"
                '      "text": "string",\n'
                '      "options": ["A", "B", "C", "D"],\n'
                '      "correct_index": 0\n'
                "    }\n"
                "  ]\n"
                "}\n\n"
                "Rules:\n"
                "- exactly 5 questions\n"
                "- no explanations\n"
                "- JSON only\n\n"
                f"Topic:\n{text}"
            )

            response = model.generate_content(prompt)
            raw = self._clean_text(response.text)

            parsed = self._safe_json(raw)
            if parsed:
                return parsed

        except Exception:
            pass

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

            correct = f"{kw} is correct"

            options = [
                correct,
                f"Wrong about {kw}",
                f"Unrelated {kw}",
                f"Partially correct {kw}"
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
    # KEYWORDS
    # =========================
    def _extract_keywords(self, text):
        words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())
        return list(set(words))[:8] or ["topic", "concept", "idea"]

    # =========================
    # SAFE JSON PARSER
    # =========================
    def _safe_json(self, text):
        try:
            return json.loads(text)
        except:
            match = re.search(r"\{.*\}", text, re.S)
            if match:
                try:
                    return json.loads(match.group())
                except:
                    return None
        return None

    # =========================
    # CLEAN OUTPUT
    # =========================
    def _clean_text(self, text: str) -> str:
        if not text:
            return ""

        # убираем LaTeX и мусор
        text = text.replace("$", "")
        text = text.replace("{", "")
        text = text.replace("}", "")

        # убираем лишние пробелы
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()