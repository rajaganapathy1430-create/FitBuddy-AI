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


def demo_update(
    original_plan,
    feedback,
):

    return f"""
{original_plan}


========================================

FITBUDDY UPDATED PLAN

User feedback:

{feedback}


The plan has been adjusted according
to the requested preference.

Continue to prioritize appropriate
workout intensity, recovery, hydration,
and rest.

SAFETY NOTE

This is general wellness guidance,
not medical advice.
"""


def update_workout_plan(
    original_plan,
    feedback,
):

    prompt = f"""
You are FitBuddy's workout revision assistant.

ORIGINAL PLAN:

{original_plan}


USER FEEDBACK:

{feedback}


Create a revised seven-day plan.

Requirements:

1. Keep exactly seven days.

2. Apply the user's feedback meaningfully.

3. Preserve useful parts of the original plan.

4. Include warm-ups.

5. Include exercises.

6. Include sets/repetitions or duration.

7. Include rest guidance.

8. Include cooldown/recovery.

9. Include at least one rest or recovery day.

10. Return plain text.

11. Do not return JSON.

12. Do not use a markdown table.

13. Do not diagnose medical conditions.

14. Do not prescribe medical treatment.

15. End with a safety note.
"""

    client = get_client()

    if client is None:

        if ALLOW_DEMO_FALLBACK:

            return demo_update(
                original_plan,
                feedback,
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
                "Gemini returned an empty updated plan."
            )

        return result

    except Exception as exc:

        if ALLOW_DEMO_FALLBACK:

            return demo_update(
                original_plan,
                feedback,
            )

        raise RuntimeError(
            f"Gemini plan update failed: {exc}"
        )