import bcrypt

class UserModel:
    def __init__(self, db):
        self.db = db

    def find_by_id(self, user_id):
        row = self.db.execute(
            "SELECT id, username, email FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        return dict(row) if row else None

    def find_by_username(self, username):
        row = self.db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        return dict(row) if row else None

    def insert(self, username, email, password_hash):
        try:
            cursor = self.db.execute(
                "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                (username, email, password_hash)
            )
            self.db.commit()
            return self.find_by_id(cursor.lastrowid)
        except Exception:
            return None

    def verify_password(self, plain_password, hashed):
        try:
            return bcrypt.checkpw(plain_password.encode(), hashed.encode())
        except Exception:
            return False
