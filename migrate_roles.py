from sqlalchemy import text

from app.database import engine


def migrate():
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS role VARCHAR
                NOT NULL DEFAULT 'user'
                """
            )
        )

        connection.execute(
            text(
                """
                UPDATE users
                SET role = 'mentor'
                WHERE id IN (
                    SELECT owner_id
                    FROM mentors
                    WHERE owner_id IS NOT NULL
                )
                AND role = 'user'
                """
            )
        )

    print("User role migration completed.")


if __name__ == "__main__":
    migrate()
