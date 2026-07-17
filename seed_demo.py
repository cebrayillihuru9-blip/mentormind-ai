from app.database import SessionLocal
from app.models import Mentor, User
from app.security import hash_password


DEMO_MENTORS = [
    {
        "full_name": "Ali Məmmədov",
        "email": "ali.mentor@mentormind.az",
        "password": "Mentor123!",
        "expertise": "Python Backend",
        "bio": (
            "6 illik Python və FastAPI təcrübəsi. "
            "Yeni başlayanlara real API layihələri üzərindən "
            "backend development öyrədir."
        ),
        "hourly_rate": 25
    },
    {
        "full_name": "Aysel Əliyeva",
        "email": "aysel.mentor@mentormind.az",
        "password": "Mentor123!",
        "expertise": "Frontend React",
        "bio": (
            "React, JavaScript və responsive frontend üzrə "
            "5 illik təcrübəyə malik mentor. Portfolio "
            "layihələrinin hazırlanmasına dəstək verir."
        ),
        "hourly_rate": 30
    },
    {
        "full_name": "Murad Həsənov",
        "email": "murad.mentor@mentormind.az",
        "password": "Mentor123!",
        "expertise": "UI/UX Design",
        "bio": (
            "Figma, UX research və design system sahəsində "
            "təcrübəli məhsul dizayneri. Junior dizaynerlərə "
            "portfolio hazırlamaqda kömək edir."
        ),
        "hourly_rate": 22
    },
    {
        "full_name": "Nigar Rzayeva",
        "email": "nigar.mentor@mentormind.az",
        "password": "Mentor123!",
        "expertise": "Data AI",
        "bio": (
            "Data analizi, Python, SQL və machine learning "
            "üzrə mentor. Fərdi öyrənmə planları və praktiki "
            "data layihələri hazırlayır."
        ),
        "hourly_rate": 35
    }
]


def seed():
    db = SessionLocal()

    try:
        created = 0

        for item in DEMO_MENTORS:
            user = (
                db.query(User)
                .filter(User.email == item["email"])
                .first()
            )

            if user is None:
                user = User(
                    full_name=item["full_name"],
                    email=item["email"],
                    password=hash_password(item["password"])
                )

                db.add(user)
                db.flush()

            mentor = (
                db.query(Mentor)
                .filter(Mentor.owner_id == user.id)
                .first()
            )

            if mentor is None:
                mentor = Mentor(
                    name=item["full_name"],
                    expertise=item["expertise"],
                    bio=item["bio"],
                    hourly_rate=item["hourly_rate"],
                    owner_id=user.id
                )

                db.add(mentor)
                created += 1

        db.commit()

        print(
            f"Demo mentor seed completed. "
            f"New mentors created: {created}"
        )

    finally:
        db.close()


if __name__ == "__main__":
    seed()
