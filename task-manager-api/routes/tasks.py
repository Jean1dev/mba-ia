from flask import Blueprint, request, jsonify
from services.task_service import TaskService
from models.task import TaskModel

tasks_bp = Blueprint("tasks", __name__)
task_service = TaskService()
task_model = TaskModel()

# HIGH: sem autenticação em nenhuma rota - qualquer um pode criar/deletar tasks
@tasks_bp.route("/tasks", methods=["GET"])
def get_tasks():
    project_id = request.args.get("project_id")
    tasks = task_service.get_tasks_with_stats(project_id)
    return jsonify(tasks)

@tasks_bp.route("/tasks/<task_id>", methods=["GET"])
def get_task(task_id):
    # HIGH: passa task_id diretamente para query SQL sem validação (SQL Injection via model)
    task = task_model.get_by_id(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task)

@tasks_bp.route("/tasks", methods=["POST"])
def create_task():
    data = request.json
    # MEDIUM: sem validação de campos obrigatórios
    if not data or "title" not in data or "project_id" not in data:
        return jsonify({"error": "title and project_id are required"}), 400
    task = task_service.create_task(data)
    return jsonify(task), 201

@tasks_bp.route("/tasks/<int:task_id>/status", methods=["PATCH"])
def update_task_status(task_id):
    data = request.json
    status = data.get("status")
    # MEDIUM: sem validar se status é um valor permitido
    task = task_model.update_status(task_id, status)
    return jsonify(task)

@tasks_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    # HIGH: sem verificar se o usuário tem permissão para deletar
    task_model.delete(task_id)
    return jsonify({"message": "Task deleted"})

@tasks_bp.route("/projects/<int:project_id>/summary", methods=["GET"])
def project_summary(project_id):
    summary = task_service.get_project_summary(project_id)
    return jsonify(summary)
