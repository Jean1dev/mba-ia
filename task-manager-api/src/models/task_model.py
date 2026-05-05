class TaskModel:
    def __init__(self, db):
        self.db = db

    def find_all(self, project_id=None):
        if project_id:
            rows = self.db.execute("""
                SELECT t.*, u.username as assignee_name
                FROM tasks t
                LEFT JOIN users u ON u.id = t.assignee_id
                WHERE t.project_id = ?
            """, (project_id,)).fetchall()
        else:
            rows = self.db.execute("""
                SELECT t.*, u.username as assignee_name
                FROM tasks t
                LEFT JOIN users u ON u.id = t.assignee_id
            """).fetchall()
        return [dict(r) for r in rows]

    def find_by_id(self, task_id):
        row = self.db.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        return dict(row) if row else None

    def insert(self, title, description, status, priority, project_id, assignee_id, due_date):
        cursor = self.db.execute(
            "INSERT INTO tasks (title, description, status, priority, project_id, assignee_id, due_date) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (title, description, status, priority, project_id, assignee_id, due_date)
        )
        self.db.commit()
        return self.find_by_id(cursor.lastrowid)

    def update_status(self, task_id, status):
        self.db.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
        self.db.commit()
        return self.find_by_id(task_id)

    def delete(self, task_id):
        self.db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.db.commit()

    def count_by_status(self, project_id):
        rows = self.db.execute("""
            SELECT status, COUNT(*) as count FROM tasks
            WHERE project_id = ? GROUP BY status
        """, (project_id,)).fetchall()
        return {r["status"]: r["count"] for r in rows}
