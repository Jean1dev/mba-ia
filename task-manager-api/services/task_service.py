from models.task import TaskModel
from database import get_db

task_model = TaskModel()

# HIGH: lógica de negócio e acesso ao banco misturados no mesmo service
class TaskService:
    def get_tasks_with_stats(self, project_id=None):
        tasks = task_model.get_all(project_id)
        # MEDIUM: N+1 query - busca assignee para cada task
        conn = get_db()
        result = []
        for task in tasks:
            if task.get("assignee_id"):
                user = conn.execute(
                    "SELECT id, username FROM users WHERE id = ?",
                    (task["assignee_id"],)
                ).fetchone()
                task["assignee"] = dict(user) if user else None
            result.append(task)
        conn.close()
        return result

    def create_task(self, data):
        # MEDIUM: sem validação de prioridade (aceita qualquer inteiro)
        # MEDIUM: sem verificar se project_id existe
        return task_model.create(data)

    def get_project_summary(self, project_id):
        tasks = task_model.get_all(project_id)
        # LOW: magic strings para status sem constante
        todo = len([t for t in tasks if t["status"] == "todo"])
        in_progress = len([t for t in tasks if t["status"] == "in_progress"])
        done = len([t for t in tasks if t["status"] == "done"])
        return {
            "total": len(tasks),
            "todo": todo,
            "in_progress": in_progress,
            "done": done
        }
