from flask import Blueprint, request, jsonify


def create_report_blueprint(ctrl):
    bp = Blueprint('reports', __name__)

    @bp.route('/reports/summary', methods=['GET'])
    def summary_report():
        return jsonify(ctrl.summary()), 200

    @bp.route('/reports/user/<int:user_id>', methods=['GET'])
    def user_report(user_id):
        return jsonify(ctrl.user_report(user_id)), 200

    @bp.route('/categories', methods=['GET'])
    def get_categories():
        return jsonify(ctrl.get_categories()), 200

    @bp.route('/categories', methods=['POST'])
    def create_category():
        data = request.get_json()
        if not data:
            raise ValueError('Dados inválidos')
        return jsonify(ctrl.create_category(data)), 201

    @bp.route('/categories/<int:cat_id>', methods=['PUT'])
    def update_category(cat_id):
        data = request.get_json()
        if not data:
            raise ValueError('Dados inválidos')
        return jsonify(ctrl.update_category(cat_id, data)), 200

    @bp.route('/categories/<int:cat_id>', methods=['DELETE'])
    def delete_category(cat_id):
        ctrl.delete_category(cat_id)
        return jsonify({'message': 'Categoria deletada'}), 200

    return bp
