from flask import Blueprint, request, jsonify

def create_task_blueprint(task_ctrl):
    bp = Blueprint("tasks", __name__)

    @bp.route("/api/v1/tasks", methods=["GET"])
    def list_tasks():
        project_id = request.args.get("project_id")
        tasks = task_ctrl.list_tasks(project_id)
        return jsonify(tasks)

    @bp.route("/api/v1/tasks/<int:task_id>", methods=["GET"])
    def get_task(task_id):
        task = task_ctrl.get_task(task_id)
        return jsonify(task)

    @bp.route("/api/v1/tasks", methods=["POST"])
    def create_task():
        task = task_ctrl.create_task(request.json or {})
        return jsonify(task), 201

    @bp.route("/api/v1/tasks/<int:task_id>/status", methods=["PATCH"])
    def update_status(task_id):
        status = (request.json or {}).get("status")
        task = task_ctrl.update_task_status(task_id, status)
        return jsonify(task)

    @bp.route("/api/v1/tasks/<int:task_id>", methods=["DELETE"])
    def delete_task(task_id):
        task_ctrl.delete_task(task_id)
        return jsonify({"message": "Task deleted"})

    @bp.route("/api/v1/projects/<int:project_id>/summary", methods=["GET"])
    def project_summary(project_id):
        summary = task_ctrl.get_project_summary(project_id)
        return jsonify(summary)

    return bp
