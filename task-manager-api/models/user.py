from database import get_db
import hashlib

class UserModel:
    # CRITICAL: senha em texto plano no banco (sem hash seguro)
    def authenticate(self, username, password):
        conn = get_db()
        # LOW: comparação direta de senha sem hash
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password)
        ).fetchone()
        conn.close()
        return dict(user) if user else None

    def get_by_id(self, user_id):
        conn = get_db()
        user = conn.execute("SELECT id, username, email FROM users WHERE id = ?", (user_id,)).fetchone()
        conn.close()
        return dict(user) if user else None

    def create(self, data):
        conn = get_db()
        # CRITICAL: senha armazenada em texto plano
        try:
            conn.execute(
                "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                (data["username"], data["password"], data["email"])
            )
            conn.commit()
            user_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            conn.close()
            return self.get_by_id(user_id)
        except Exception as e:
            conn.close()
            return {"error": str(e)}
