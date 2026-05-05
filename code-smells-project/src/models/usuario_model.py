import bcrypt

class UsuarioModel:
    def __init__(self, db):
        self.db = db

    def find_all(self):
        rows = self.db.execute(
            "SELECT id, nome, email, admin FROM usuarios"
        ).fetchall()
        return [dict(r) for r in rows]

    def find_by_id(self, usuario_id):
        row = self.db.execute(
            "SELECT id, nome, email, admin FROM usuarios WHERE id = ?", (usuario_id,)
        ).fetchone()
        return dict(row) if row else None

    def find_by_email(self, email):
        row = self.db.execute(
            "SELECT * FROM usuarios WHERE email = ?", (email,)
        ).fetchone()
        return dict(row) if row else None

    def insert(self, nome, email, senha_hash):
        try:
            cursor = self.db.execute(
                "INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)",
                (nome, email, senha_hash)
            )
            self.db.commit()
            return self.find_by_id(cursor.lastrowid)
        except Exception:
            return None

    def verify_password(self, senha_plain, senha_hash):
        try:
            return bcrypt.checkpw(senha_plain.encode(), senha_hash.encode())
        except Exception:
            return False
