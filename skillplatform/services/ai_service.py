import random
import re
import json
from google import genai  # Перешли на новый официальный пакет
from django.conf import settings

# Инициализируем клиент. Он автоматически подхватит настройки или ключ
client = genai.Client(api_key=settings.GEMINI_API_KEY)


class AIService:
    def chat(self, message: str) -> str:
        try:
            prompt = (
                "You are a professional AI Learning Tutor for Math, Physics, Chemistry, Biology and Science.\n\n"

                "IMPORTANT RULES:\n"
                "- Respond ONLY in clean Markdown.\n"
                "- NEVER use LaTeX.\n"
                "- NEVER use $, $$, \\( \\), \\[ \\], \\frac, \\sqrt{}, \\sum, \\int or any LaTeX commands.\n"
                "- Use ONLY normal keyboard math symbols.\n"
                "- Write equations exactly like people do in school.\n"
                "- Examples:\n"
                "  5 + 5 = 10\n"
                "  12 - 7 = 5\n"
                "  9 * 8 = 72\n"
                "  20 / 4 = 5\n"
                "  x^2 + 5x + 6 = 0\n"
                "  (a + b) / 2\n"
                "  sqrt(16) = 4\n"
                "- NEVER write math in words like 'five plus five'.\n"
                "- NEVER replace numbers with words.\n"
                "- Be short, clear and educational.\n\n"

                "Always use this structure:\n"
                "### Topic\n"
                "### Explanation\n"
                "### Steps\n"
                "### Final Answer\n\n"

                f"Student question:\n{message}"
            )

            # Новый синтаксис вызова модели через client
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            return self._clean_text(response.text)

        except Exception as e:
            return f"AI Error: {str(e)}"

    def explain_text(self, text: str) -> str:
        try:
            prompt = (
                "Explain this for a student using simple language.\n\n"
                "Do NOT use LaTeX.\n"
                "Use normal math symbols (+ - * / =).\n\n"
                "Format:\n"
                "### Explanation\n"
                "### Key Points\n\n"
                f"Text:\n{text}"
            )

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return self._clean_text(response.text)

        except Exception as e:
            return str(e)

    def summarize_text(self, text: str) -> str:
        try:
            prompt = (
                "Summarize this text clearly.\n\n"
                "Do NOT use LaTeX.\n"
                "Use normal math symbols.\n\n"
                "Format:\n"
                "### Summary\n\n"
                f"Text:\n{text}"
            )

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return self._clean_text(response.text)

        except Exception as e:
            return str(e)

    def generate_test(self, text, subject="general", difficulty="medium"):
        try:
            prompt = (
                "You are a test generator AI.\n\n"
                f"Create a {difficulty} level test for {subject}.\n\n"

                "Return ONLY valid JSON.\n\n"

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
                "- valid JSON only\n\n"

                f"Topic:\n{text}"
            )

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            raw = self._clean_text(response.text)

            parsed = self._safe_json(raw)
            if parsed:
                return parsed

        except Exception:
            pass

        return self._fallback_test(text, subject, difficulty)

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

    def _extract_keywords(self, text):
        words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())
        return list(set(words))[:8] or ["topic", "concept", "idea"]

    def _safe_json(self, text):
        try:
            return json.loads(text)
        except Exception:
            match = re.search(r"\{.*\}", text, re.S)
            if match:
                try:
                    return json.loads(match.group())
                except Exception:
                    return None
        return None

    def _clean_text(self, text: str) -> str:
        if not text:
            return ""

        # Удаляем LaTeX-обертки
        text = text.replace("$$", "")
        text = text.replace("$", "")

        text = re.sub(r"\\\((.*?)\\\)", r"\1", text)
        text = re.sub(r"\\\[(.*?)\\\]", r"\1", text)

        # Заменяем LaTeX-команды на обычные символы
        replacements = {
            r"\\times": "*",
            r"\\cdot": "*",
            r"\\div": "/",
            r"\\pm": "±",
            r"\\mp": "∓",
            r"\\leq": "<=",
            r"\\geq": ">=",
            r"\\neq": "!=",
            r"\\approx": "≈",
            r"\\sim": "~",
            r"\\sqrt": "sqrt",
        }

        for old, new in replacements.items():
            text = re.sub(old, new, text)

        # Удаляем оставшиеся обратные слеши
        text = text.replace("\\", "")

        # Удаляем лишние пустые строки
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()