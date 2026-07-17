from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models
from app.auth import get_current_user
from app.database import get_db


router = APIRouter(
    prefix="/ai",
    tags=["AI Assistant"]
)


class LearningPlanRequest(BaseModel):
    goal: str = Field(..., min_length=3, max_length=500)
    level: str = Field(default="Beginner")
    duration_months: int = Field(default=3, ge=1, le=12)
    weekly_hours: int = Field(default=8, ge=1, le=80)
    budget: float | None = Field(default=None, ge=0)


def detect_track(goal: str):
    text = goal.lower()

    tracks = [
        {
            "keywords": [
                "python",
                "fastapi",
                "backend",
                "api",
                "django"
            ],
            "title": "Python Backend Development",
            "expertise": "Python",
            "skills": [
                "Python əsasları",
                "Git və GitHub",
                "PostgreSQL",
                "FastAPI",
                "REST API",
                "Authentication",
                "Deployment"
            ]
        },
        {
            "keywords": [
                "frontend",
                "react",
                "javascript",
                "html",
                "css"
            ],
            "title": "Frontend Development",
            "expertise": "Frontend",
            "skills": [
                "HTML və CSS",
                "JavaScript",
                "React",
                "API inteqrasiyası",
                "Responsive dizayn",
                "State management",
                "Deployment"
            ]
        },
        {
            "keywords": [
                "design",
                "ui",
                "ux",
                "figma",
                "dizayn"
            ],
            "title": "UI/UX Design",
            "expertise": "UI/UX",
            "skills": [
                "Dizayn prinsipləri",
                "Figma",
                "User research",
                "Wireframe",
                "Design system",
                "Prototype",
                "Portfolio"
            ]
        },
        {
            "keywords": [
                "data",
                "machine learning",
                "ai",
                "süni intellekt",
                "analitika"
            ],
            "title": "Data and Artificial Intelligence",
            "expertise": "Data",
            "skills": [
                "Python",
                "Data analizi",
                "Pandas",
                "SQL",
                "Machine Learning",
                "Model qiymətləndirməsi",
                "Portfolio layihəsi"
            ]
        },
        {
            "keywords": [
                "business",
                "biznes",
                "startup",
                "marketing",
                "satış"
            ],
            "title": "Business and Startup Development",
            "expertise": "Business",
            "skills": [
                "Problem analizi",
                "Bazar araşdırması",
                "Biznes model",
                "Müştəri profili",
                "Satış",
                "Marketinq",
                "Pitch deck"
            ]
        }
    ]

    for track in tracks:
        if any(keyword in text for keyword in track["keywords"]):
            return track

    return {
        "title": "Personal Development Plan",
        "expertise": "",
        "skills": [
            "Məqsədin dəqiqləşdirilməsi",
            "Əsas nəzəri biliklər",
            "Praktik tapşırıqlar",
            "Kiçik layihə",
            "Mentor geribildirimi",
            "Portfolio işi",
            "Nəticələrin qiymətləndirilməsi"
        ]
    }


@router.post("/learning-plan")
def generate_learning_plan(
    request: LearningPlanRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    track = detect_track(request.goal)

    mentors_query = db.query(models.Mentor)

    if track["expertise"]:
        mentors_query = mentors_query.filter(
            models.Mentor.expertise.ilike(
                f"%{track['expertise']}%"
            )
        )

    if request.budget is not None and request.budget > 0:
        mentors_query = mentors_query.filter(
            models.Mentor.hourly_rate <= request.budget
        )

    mentors = (
        mentors_query
        .order_by(models.Mentor.hourly_rate.asc())
        .limit(3)
        .all()
    )

    skills = track["skills"]
    months = []

    for month_number in range(1, request.duration_months + 1):
        start_index = (
            (month_number - 1) * len(skills)
            // request.duration_months
        )

        end_index = (
            month_number * len(skills)
            // request.duration_months
        )

        month_skills = skills[start_index:end_index]

        if not month_skills:
            month_skills = [
                skills[min(month_number - 1, len(skills) - 1)]
            ]

        months.append({
            "month": month_number,
            "title": f"{month_number}-ci ay",
            "topics": month_skills,
            "weekly_hours": request.weekly_hours,
            "task": (
                f"{', '.join(month_skills)} üzrə praktiki "
                "tapşırıq tamamla."
            )
        })

    return {
        "user": current_user.full_name,
        "goal": request.goal,
        "level": request.level,
        "track": track["title"],
        "duration_months": request.duration_months,
        "weekly_hours": request.weekly_hours,
        "summary": (
            f"{request.duration_months} aylıq fərdi inkişaf "
            f"planı hazırlandı. Həftədə təxminən "
            f"{request.weekly_hours} saat ayırmaq tövsiyə olunur."
        ),
        "months": months,
        "recommended_mentors": [
            {
                "id": mentor.id,
                "name": mentor.name,
                "expertise": mentor.expertise,
                "hourly_rate": mentor.hourly_rate,
                "match_score": max(
                    70,
                    96 - index * 7
                )
            }
            for index, mentor in enumerate(mentors)
        ]
    }
