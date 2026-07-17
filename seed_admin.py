from app.database import SessionLocal
from app.models import User
from app.security import hash_password


ADMIN_EMAIL = "admin@mentormind.az"
ADMIN_PASSWORD = "Admin123!"


def seed_admin():
    db = SessionLocal()

    try:
        admin = (
            db.query(User)
            .filter(User.email == ADMIN_EMAIL)
            .first()
        )

        if admin is None:
            admin = User(
                full_name="MentorMind Admin",
                email=ADMIN_EMAIL,
                password=hash_password(ADMIN_PASSWORD),
                role="admin"
            )
            db.add(admin)
        else:
            admin.full_name = "MentorMind Admin"
            admin.password = hash_password(ADMIN_PASSWORD)
            admin.role = "admin"

        db.commit()

        print("Admin hesabı hazırdır.")
        print(f"Email: {ADMIN_EMAIL}")
        print(f"Password: {ADMIN_PASSWORD}")

    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()
