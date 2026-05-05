from database import get_db

class TaskModel:
    def get_all(self, project_id=None):
        conn = get_db()
        if project_id:
            tasks = conn.execute(
                "SELECT * FROM tasks WHERE project_id = ?", (project_id,)
            ).fetchall()
        else:
            tasks = conn.execute("SELECT * FROM tasks").fetchall()
        conn.close()
        return [dict(t) for t in tasks]

    def get_by_id(self, task_id):
        conn = get_db()
        # CRITICAL: SQL Injection - interpolação direta
        task = conn.execute(
            f"SELECT * FROM tasks WHERE id = {task_id}"
        ).fetchone()
        conn.close()
        return dict(task) if task else None

    def create(self, data):
        conn = get_db()
        # MEDIUM: sem validação de status válido (qualquer valor aceito)
        conn.execute(
            "INSERT INTO tasks (title, description, status, priority, project_id, assignee_id, due_date) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (data["title"], data.get("description", ""), data.get("status", "todo"),
             data.get("priority", 1), data["project_id"], data.get("assignee_id"), data.get("due_date"))
        )
        conn.commit()
        task_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.close()
        return self.get_by_id(task_id)

    def update_status(self, task_id, status):
        conn = get_db()
        # MEDIUM: sem validação se status é um valor permitido
        conn.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
        conn.commit()
        conn.close()
        return self.get_by_id(task_id)

    def delete(self, task_id):
        conn = get_db()
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
