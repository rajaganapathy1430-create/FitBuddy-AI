from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Request,
)

from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
)

from fastapi.templating import (
    Jinja2Templates,
)

from pydantic import ValidationError

from sqlalchemy import select

from sqlalchemy.orm import Session

from .database import get_db

from .gemini_flash_generate import (
    generate_nutrition_tip_with_flash,
)

from .gemini_generator import (
    generate_workout_gemini,
)

from .models import User

from .schemas import (
    FeedbackRequest,
    UserInput,
)

from .updated_plan import (
    update_workout_plan,
)


BASE_DIR = Path(
    __file__
).resolve().parent.parent


FRONTEND_DIR = BASE_DIR / "frontend"


templates = Jinja2Templates(
    directory=str(FRONTEND_DIR)
)


router = APIRouter()


def get_user(
    db: Session,
    user_id: str,
):

    return db.scalar(
        select(User).where(
            User.user_id == user_id.strip()
        )
    )


def result_context(
    user: User,
    message=None,
):

    return {

        "username": user.username,

        "user_id": user.user_id,

        "age": user.age,

        "weight": user.weight,

        "goal": user.goal,

        "intensity": user.intensity,

        "workout_plan": (
            user.updated_plan
            or user.original_plan
        ),

        "nutrition_tip": user.nutrition_tip,

        "feedback": (
            user.feedback
            or ""
        ),

        "message": message,
    }


@router.get(
    "/",
    response_class=HTMLResponse,
)
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
        },
    )


@router.post(
    "/generate-workout",
    response_class=HTMLResponse,
)
def generate_workout(

    request: Request,

    username: str = Form(...),

    user_id: str = Form(...),

    age: int = Form(...),

    weight: float = Form(...),

    goal: str = Form(...),

    intensity: str = Form(...),

    db: Session = Depends(get_db),

):

    try:

        data = UserInput(
            username=username,
            user_id=user_id,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )

    except ValidationError as exc:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "request": request,
                "error": str(exc),
            },
            status_code=422,
        )

    try:

        workout = generate_workout_gemini(
            data.username,
            data.age,
            data.weight,
            data.goal,
            data.intensity,
        )

        nutrition = (
            generate_nutrition_tip_with_flash(
                data.goal
            )
        )

    except RuntimeError as exc:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "request": request,
                "error": str(exc),
            },
            status_code=502,
        )

    user = get_user(
        db,
        data.user_id,
    )

    if user is None:

        user = User(

            user_id=data.user_id,

            username=data.username,

            age=data.age,

            weight=data.weight,

            goal=data.goal,

            intensity=data.intensity,

            original_plan=workout,

            nutrition_tip=nutrition,

        )

        db.add(user)

    else:

        user.username = data.username

        user.age = data.age

        user.weight = data.weight

        user.goal = data.goal

        user.intensity = data.intensity

        user.original_plan = workout

        user.updated_plan = None

        user.feedback = None

        user.nutrition_tip = nutrition

    db.commit()

    db.refresh(user)

    return templates.TemplateResponse(

        request=request,

        name="result.html",

        context=result_context(user),

    )


@router.post(
    "/submit-feedback",
    response_class=HTMLResponse,
)
def submit_feedback(

    request: Request,

    user_id: str = Form(...),

    feedback: str = Form(...),

    db: Session = Depends(get_db),

):

    try:

        data = FeedbackRequest(
            user_id=user_id,
            feedback=feedback,
        )

    except ValidationError as exc:

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )

    user = get_user(
        db,
        data.user_id,
    )

    if user is None:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "request": request,
                "error": "User ID not found.",
            },
            status_code=404,
        )

    try:

        revised = update_workout_plan(
            user.original_plan,
            data.feedback,
        )

        nutrition = (
            generate_nutrition_tip_with_flash(
                user.goal
            )
        )

    except RuntimeError as exc:

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                **result_context(user),
                "message": str(exc),
            },
            status_code=502,
        )

    user.updated_plan = revised

    user.feedback = data.feedback

    user.nutrition_tip = nutrition

    db.commit()

    db.refresh(user)

    return templates.TemplateResponse(

        request=request,

        name="result.html",

        context=result_context(
            user,
            "Your fitness plan has been updated.",
        ),

    )


@router.get(
    "/view-all-users",
    response_class=HTMLResponse,
)
def view_all_users(

    request: Request,

    db: Session = Depends(get_db),

):

    users = db.scalars(

        select(User).order_by(
            User.created_at.desc()
        )

    ).all()

    return templates.TemplateResponse(

        request=request,

        name="all_users.html",

        context={
            "request": request,
            "users": users,
        },

    )


@router.post(
    "/delete-user/{user_id}"
)
def delete_user(

    user_id: str,

    db: Session = Depends(get_db),

):

    user = get_user(
        db,
        user_id,
    )

    if user is None:

        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    db.delete(user)

    db.commit()

    return RedirectResponse(
        url="/view-all-users",
        status_code=303,
    )


@router.get("/health")
def health():

    return {
        "status": "ok",
        "application": "FitBuddy",
    }


@router.get("/api/users")
def api_users(
    db: Session = Depends(get_db),
):

    users = db.scalars(
        select(User).order_by(
            User.created_at.desc()
        )
    ).all()

    return [

        {
            "user_id": user.user_id,
            "username": user.username,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity,
            "updated": bool(
                user.updated_plan
            ),
        }

        for user in users

    ]


@router.get(
    "/api/users/{user_id}"
)
def api_user(

    user_id: str,

    db: Session = Depends(get_db),

):

    user = get_user(
        db,
        user_id,
    )

    if user is None:

        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    return {

        "user_id": user.user_id,

        "username": user.username,

        "age": user.age,

        "weight": user.weight,

        "goal": user.goal,

        "intensity": user.intensity,

        "original_plan":
            user.original_plan,

        "updated_plan":
            user.updated_plan,

        "nutrition_tip":
            user.nutrition_tip,

        "feedback":
            user.feedback,

    }