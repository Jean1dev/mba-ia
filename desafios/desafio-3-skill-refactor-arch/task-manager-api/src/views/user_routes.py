from flask import Blueprint, request, jsonify


def create_user_blueprint(ctrl):
    bp = Blueprint('users', __name__)

    @bp.route('/users', methods=['GET'])
    def get_users():
        return jsonify(ctrl.get_all()), 200

    @bp.route('/users/<int:user_id>', methods=['GET'])
    def get_user(user_id):
        return jsonify(ctrl.get_by_id(user_id)), 200

    @bp.route('/users', methods=['POST'])
    def create_user():
        data = request.get_json()
        if not data:
            raise ValueError('Dados inválidos')
        return jsonify(ctrl.create(data)), 201

    @bp.route('/users/<int:user_id>', methods=['PUT'])
    def update_user(user_id):
        data = request.get_json()
        if not data:
            raise ValueError('Dados inválidos')
        return jsonify(ctrl.update(user_id, data)), 200

    @bp.route('/users/<int:user_id>', methods=['DELETE'])
    def delete_user(user_id):
        ctrl.delete(user_id)
        return jsonify({'message': 'Usuário deletado com sucesso'}), 200

    @bp.route('/users/<int:user_id>/tasks', methods=['GET'])
    def get_user_tasks(user_id):
        return jsonify(ctrl.get_tasks(user_id)), 200

    @bp.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        if not data:
            raise ValueError('Dados inválidos')
        email = data.get('email', '')
        password = data.get('password', '')
        if not email or not password:
            raise ValueError('Email e senha são obrigatórios')
        return jsonify(ctrl.login(email, password)), 200

    return bp
