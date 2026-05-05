from src.config.settings import VALID_TASK_STATUSES, VALID_PRIORITIES

class TaskController:
    def __init__(self, task_model):
        self.task_model = task_model

    def list_tasks(self, project_id=None):
        return self.task_model.find_all(project_id)

    def get_task(self, task_id):
        task = self.task_model.find_by_id(task_id)
        if not task:
            raise LookupError("Task not found")
        return task

    def create_task(self, data):
        title = data.get("title", "")
        project_id = data.get("project_id")
        status = data.get("status", "todo")
        priority = data.get("priority", 1)

        if not title or not project_id:
            raise ValueError("title e project_id são obrigatórios")
        if status not in VALID_TASK_STATUSES:
            raise ValueError(f"status deve ser um de: {', '.join(VALID_TASK_STATUSES)}")
        if priority not in VALID_PRIORITIES:
            raise ValueError(f"priority deve estar entre 1 e 5")

        return self.task_model.insert(
            title,
            data.get("description", ""),
            status,
            priority,
            project_id,
            data.get("assignee_id"),
            data.get("due_date")
        )

    def update_task_status(self, task_id, status):
        if status not in VALID_TASK_STATUSES:
            raise ValueError(f"status deve ser um de: {', '.join(VALID_TASK_STATUSES)}")
        self.get_task(task_id)
        return self.task_model.update_status(task_id, status)

    def delete_task(self, task_id):
        self.get_task(task_id)
        self.task_model.delete(task_id)

    def get_project_summary(self, project_id):
        counts = self.task_model.count_by_status(project_id)
        total = sum(counts.values())
        return {
            "total": total,
            "todo": counts.get("todo", 0),
            "in_progress": counts.get("in_progress", 0),
            "done": counts.get("done", 0),
        }
