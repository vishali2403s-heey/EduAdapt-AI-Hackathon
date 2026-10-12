
import os
import random
import re
from collections import defaultdict

from openai import OpenAI


def get_ai_client():
    """Return an OpenAI client when an API key is configured."""
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


def answer_question(question, material=""):
    """Answer using uploaded learning material when available."""
    question = question.strip()
    if not question:
        return "Please enter a question."

    client = get_ai_client()
    if client:
        try:
            response = client.responses.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
                instructions=(
                    "You are EduAdapt AI, a patient personal tutor. "
                    "Explain concepts clearly, use examples, and adapt to "
                    "a beginner unless the learner indicates otherwise. "
                    "When source material is supplied, prioritize it and "
                    "say when the answer is not supported by that material."
                ),
                input=(
                    f"LEARNING MATERIAL:\n{material[:18000] or 'No material uploaded.'}"
                    f"\n\nLEARNER QUESTION:\n{question}"
                ),
            )
            return response.output_text
        except Exception:
            pass

    if material:
        return (
            "AI is unavailable right now, so here is a basic study response.\n\n"
            f"Your question: {question}\n\n"
            f"Review this material and look for the sections related to your "
            f"question:\n{material[:2500]}\n\n"
            "Configure OPENAI_API_KEY to enable AI-generated explanations."
        )

    return (
        "I can help you study! Add your learning material and configure "
        "OPENAI_API_KEY for personalized AI explanations. "
        f"Your question was: {question}"
    )


def generate_quiz(material="", topic="General", difficulty="medium", count=5):
    """Generate a quiz with AI, with a small fallback quiz if unavailable."""
    count = max(1, min(int(count), 10))
    difficulty = difficulty if difficulty in {
        "easy", "medium", "hard"
    } else "medium"

    client = get_ai_client()
    if client:
        try:
            response = client.responses.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
                instructions=(
                    "Create educational multiple-choice quizzes. "
                    "Return ONLY valid JSON, no markdown fences. "
                    'Use this schema: {"questions":[{"question":"...",'
                    '"options":["...","...","...","..."],"correct":0,'
                    '"explanation":"...","topic":"..."}]}. '
                    "The correct field must be an integer from 0 to 3. "
                    "Each question must have exactly four options. "
                    "Make distractors plausible and avoid ambiguity."
                ),
                input=(
                    f"Topic: {topic}\nDifficulty: {difficulty}\n"
                    f"Number of questions: {count}\n"
                    f"Study material:\n{material[:14000] or topic}"
                ),
            )
            import json

            raw = response.output_text.strip()
            raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw)
            data = json.loads(raw)
            questions = data.get("questions", [])
            cleaned = []

            for i, q in enumerate(questions[:count]):
                options = q.get("options", [])
                correct = q.get("correct")
                if (
                    not isinstance(q.get("question"), str)
                    or len(options) != 4
                    or not isinstance(correct, int)
                    or isinstance(correct, bool)
                    or correct not in range(4)
                ):
                    continue

                cleaned.append({
                    "id": i + 1,
                    "question": q["question"],
                    "options": options,
                    "correct": correct,
                    "explanation": q.get("explanation", ""),
                    "topic": q.get("topic", topic),
                    "difficulty": difficulty,
                })

            if cleaned:
                return cleaned
        except Exception:
            pass

    # Safe fallback: does not pretend to generate real content-specific questions.
    return [{
        "id": 1,
        "question": (
            f"Which is the best first step when studying {topic}?"
        ),
        "options": [
            "Memorize everything without understanding",
            "Identify key concepts and explain them in your own words",
            "Skip difficult topics",
            "Read once without checking understanding",
        ],
        "correct": 1,
        "explanation": (
            "Identify the key concepts, then test your understanding "
            "with practice questions."
        ),
        "topic": topic,
        "difficulty": difficulty,
    }]


def next_difficulty(current, was_correct):
    """Adjust the next question based on the learner's last answer."""
    levels = ["easy", "medium", "hard"]
    current = current if current in levels else "medium"
    index = levels.index(current)

    if was_correct:
        index = min(index + 1, len(levels) - 1)
    else:
        index = max(index - 1, 0)

    return levels[index]


def build_revision_plan(topic_stats):
    """Create revision suggestions from topic performance."""
    plan = []

    for topic, stats in topic_stats.items():
        total = stats.get("total", 0)
        correct = stats.get("correct", 0)
        accuracy = (correct / total * 100) if total else 0

        if total == 0:
            action = "Start with a short practice quiz."
        elif accuracy < 60:
            action = "Revisit the basics, review examples, then retry an easy quiz."
        elif accuracy < 80:
            action = "Review the mistakes and practise a medium quiz."
        else:
            action = "Try harder questions to strengthen mastery."

        plan.append({
            "topic": topic,
            "accuracy": round(accuracy),
            "action": action,
        })

    return sorted(plan, key=lambda item: item["accuracy"])
