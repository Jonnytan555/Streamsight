import bcrypt
import sqlalchemy as sa


def _hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


class UserService:
    def create_user(self, db, username: str, password: str, email: str) -> dict | None:
        exists = db.execute(
            sa.text("SELECT TOP 1 1 FROM users WHERE username = :u"),
            {"u": username},
        ).fetchone()
        if exists:
            return None

        db.execute(
            sa.text("""
                INSERT INTO users (username, password_hash, name, email)
                VALUES (:username, :password_hash, :username, :email)
            """),
            {"username": username, "password_hash": _hash(password), "email": email},
        )
        return {"username": username}

    def authenticate(self, db, username: str, password: str) -> dict | None:
        row = db.execute(
            sa.text("SELECT username, password_hash, name FROM users WHERE username = :u"),
            {"u": username},
        ).fetchone()
        if not row or not _verify(password, row.password_hash):
            return None
        return {"sub": row.username, "username": row.username, "name": row.name}
