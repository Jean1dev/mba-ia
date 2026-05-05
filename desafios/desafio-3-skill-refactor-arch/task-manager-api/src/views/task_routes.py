from flask import Blueprint, request, jsonify


def create_task_blueprint(ctrl):
    bp = Blueprint('tasks', __name__)

    @bp.route('/tasks', methods=['GET'])
    def get_tasks():
        return jsonify(ctrl.get_all()), 200

    @bp.route('/tasks/search', methods=['GET'])
    def search_tasks():
        return jsonify(ctrl.search(
            q=request.args.get('q', ''),
            status=request.args.get('status', ''),
            priority=request.args.get('priority', ''),
            user_id=request.args.get('user_id', ''),
        )), 200

    @bp.route('/tasks/stats', methods=['GET'])
    def task_stats():
        return jsonify(ctrl.stats()), 200

    @bp.route('/tasks/<int:task_id>', methods=['GET'])
    def get_task(task_id):
        return jsonify(ctrl.get_by_id(task_id)), 200

    @bp.route('/tasks', methods=['POST'])
    def create_task():
        data = request.get_json()
        if not data:
            raise ValueError('Dados inválidos')
        return jsonify(ctrl.create(data)), 201

    @bp.route('/tasks/<int:task_id>', methods=['PUT'])
    def update_task(task_id):
        data = request.get_json()
        if not data:
            raise ValueError('Dados inválidos')
        return jsonify(ctrl.update(task_id, data)), 200

    @bp.route('/tasks/<int:task_id>', methods=['DELETE'])
    def delete_task(task_id):
        ctrl.delete(task_id)
        return jsonify({'message': 'Task deletada com sucesso'}), 200

    return bp
