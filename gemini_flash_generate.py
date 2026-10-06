import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


MODEL_NAME = os.getenv(
    "GEMINI_FLASH_MODEL",
    "gemini-2.5-flash",
)


ALLOW_DEMO_FALLBACK = (
    os.getenv(
        "ALLOW_DEMO_FALLBACK",
        "true",
    ).lower()
    == "true"
)


def get_client():

    api_key = os.getenv(
        "GEMINI_API_KEY"
    )

    if not api_key:
        return None

    return genai.Client(
        api_key=api_key
    )


def demo_tip(goal):

    goal = goal.lower()

    if "muscle" in goal:

        return (
            "Include a protein-rich food in each "
            "main meal, stay hydrated, and prioritize "
            "adequate sleep to support training recovery."
        )

    if "weight" in goal:

        return (
            "Build meals around vegetables, protein, "
            "whole-food carbohydrates and healthy fats. "
            "Avoid extreme calorie restriction."
        )

    if "flexibility" in goal:

        return (
            "Stay well hydrated and include a balanced "
            "diet with enough protein and colorful fruits "
            "and vegetables to support recovery."
        )

    return (
        "Focus on balanced meals containing protein, "
        "vegetables or fruit, whole-food carbohydrates, "
        "and healthy fats. Drink water regularly."
    )


def generate_nutrition_tip_with_flash(goal):

    prompt = f"""
You are FitBuddy's nutrition and recovery assistant.

The user's fitness goal is:

{goal}

Provide one practical nutrition or recovery tip.

Requirements:

• 2–4 sentences
• Practical and easy to follow
• No extreme dieting
• No supplement prescriptions
• No medical treatment
"""

    client = get_client()

    if client is None:

        if ALLOW_DEMO_FALLBACK:

            return demo_tip(goal)

        raise RuntimeError(
            "GEMINI_API_KEY is missing."
        )

    try:

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )

        result = (
            response.text or ""
        ).strip()

        if not result:

            raise RuntimeError(
                "Gemini returned an empty nutrition tip."
            )

        return result

    except Exception as exc:

        if ALLOW_DEMO_FALLBACK:

            return demo_tip(goal)

        raise RuntimeError(
            f"Gemini nutrition generation failed: {exc}"
        )