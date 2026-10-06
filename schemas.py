from pydantic import (
    BaseModel,
    Field,
    field_validator,
)


class UserInput(BaseModel):

    username: str = Field(
        min_length=2,
        max_length=120,
    )

    user_id: str = Field(
        min_length=2,
        max_length=80,
    )

    age: int = Field(
        ge=13,
        le=100,
    )

    weight: float = Field(
        gt=20,
        le=400,
    )

    goal: str = Field(
        min_length=2,
        max_length=100,
    )

    intensity: str

    @field_validator(
        "username",
        "user_id",
        "goal",
    )
    @classmethod
    def clean_text(cls, value):

        value = value.strip()

        if not value:

            raise ValueError(
                "This field cannot be empty."
            )

        return value

    @field_validator("intensity")
    @classmethod
    def validate_intensity(cls, value):

        value = value.strip().lower()

        allowed = {
            "low",
            "medium",
            "high",
        }

        if value not in allowed:

            raise ValueError(
                "Intensity must be low, medium, or high."
            )

        return value


class FeedbackRequest(BaseModel):

    user_id: str = Field(
        min_length=2,
        max_length=80,
    )

    feedback: str = Field(
        min_length=3,
        max_length=2000,
    )