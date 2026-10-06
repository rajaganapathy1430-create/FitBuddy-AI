import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


MODEL_NAME = os.getenv(
    "GEMINI_WORKOUT_MODEL",
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


def demo_plan(
    username,
    age,
    weight,
    goal,
    intensity,
):

    return f"""
FITBUDDY — PERSONALIZED 7-DAY PLAN

Name: {username}
Age: {age}
Weight: {weight} kg
Goal: {goal.title()}
Intensity: {intensity.title()}


DAY 1 — FULL BODY

Warm-up:
5–10 minutes brisk walking and mobility.

Workout:
• Squats — 3 × 10
• Incline push-ups — 3 × 10
• Glute bridges — 3 × 12
• Resistance rows — 3 × 10

Cooldown:
5 minutes stretching.


DAY 2 — CARDIO + CORE

Warm-up:
5 minutes easy cardio.

Workout:
• Brisk walking — 20–30 minutes
• Plank — 3 × 30 seconds
• Dead bug — 3 × 10 each side

Cooldown:
5 minutes stretching.


DAY 3 — LOWER BODY

Warm-up:
5–10 minutes.

Workout:
• Reverse lunges — 3 × 8 each leg
• Hip hinges — 3 × 10
• Calf raises — 3 × 15
• Side plank — 3 × 20 seconds

Cooldown:
Lower-body stretching.


DAY 4 — RECOVERY

• Easy walking — 20–30 minutes
• Gentle mobility
• Light stretching

Keep the intensity comfortable.


DAY 5 — UPPER BODY

Warm-up:
5–10 minutes.

Workout:
• Push-ups — 3 × 8–12
• Rows — 3 × 10
• Shoulder press — 3 × 10
• Biceps curls — 2 × 12

Cooldown:
5 minutes.


DAY 6 — CARDIO + FULL BODY

Warm-up:
5–7 minutes.

Workout:
• Moderate cardio — 20–30 minutes
• Squats — 2 × 10
• Push-ups — 2 × 8
• Rows — 2 × 10
• Dead bugs — 2 × 10

Cooldown:
5 minutes.


DAY 7 — REST

• Easy walking if desired
• Gentle stretching
• Hydration
• Recovery


SAFETY NOTE

This plan provides general wellness guidance,
not medical advice.

Stop exercising if you experience pain,
dizziness, or unusual symptoms.
"""


def generate_workout_gemini(
    username,
    age,
    weight,
    goal,
    intensity,
):

    prompt = f"""
You are FitBuddy, an AI fitness planning assistant.

Create a personalized seven-day fitness plan.

USER INFORMATION

Name: {username}
Age: {age}
Weight: {weight} kg
Goal: {goal}
Intensity: {intensity}


REQUIREMENTS

Create exactly seven days.

For each workout day include:

• Day name
• Workout focus
• Warm-up
• Exercises
• Sets and repetitions or duration
• Rest guidance
• Cooldown

Include at least one recovery/rest day.

Adapt the difficulty to the requested intensity.

Keep recommendations practical.

Do not diagnose medical conditions.

Do not prescribe medical treatment.

Do not claim the plan is medically prescribed.

Return plain text.

Do not use a markdown table.

End with a short safety note.
"""

    client = get_client()

    if client is None:

        if ALLOW_DEMO_FALLBACK:

            return demo_plan(
                username,
                age,
                weight,
                goal,
                intensity,
            )

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
                "Gemini returned an empty response."
            )

        return result

    except Exception as exc:

        if ALLOW_DEMO_FALLBACK:

            return demo_plan(
                username,
                age,
                weight,
                goal,
                intensity,
            )

        raise RuntimeError(
            f"Gemini workout generation failed: {exc}"
        )