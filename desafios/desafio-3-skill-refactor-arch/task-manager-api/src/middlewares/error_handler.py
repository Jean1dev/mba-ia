import logging
from flask import jsonify

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(ValueError)
    def bad_request(err):
        return jsonify({'error': str(err)}), 400

    @app.errorhandler(LookupError)
    def not_found(err):
        return jsonify({'error': str(err)}), 404

    @app.errorhandler(PermissionError)
    def unauthorized(err):
        return jsonify({'error': str(err)}), 401

    @app.errorhandler(404)
    def route_not_found(err):
        return jsonify({'error': 'Rota não encontrada'}), 404

    @app.errorhandler(Exception)
    def internal_error(err):
        logger.exception('Unhandled error: %s', err)
        return jsonify({'error': 'Erro interno do servidor'}), 500
