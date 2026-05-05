from flask import jsonify

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"erro": "Recurso não encontrado", "sucesso": False}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"erro": "Método não permitido", "sucesso": False}), 405

    @app.errorhandler(500)
    def server_error(e):
        app.logger.error(f"Internal error: {e}")
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500

    @app.errorhandler(ValueError)
    def validation_error(e):
        return jsonify({"erro": str(e), "sucesso": False}), 400

    @app.errorhandler(LookupError)
    def not_found_error(e):
        return jsonify({"erro": str(e), "sucesso": False}), 404

    @app.errorhandler(PermissionError)
    def permission_error(e):
        return jsonify({"erro": str(e), "sucesso": False}), 401
