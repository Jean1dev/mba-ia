from flask import jsonify

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(500)
    def server_error(e):
        app.logger.error(f"Internal server error: {e}")
        return jsonify({"error": "Internal server error"}), 500

    @app.errorhandler(ValueError)
    def validation_error(e):
        return jsonify({"error": str(e)}), 400

    @app.errorhandler(LookupError)
    def not_found_error(e):
        return jsonify({"error": str(e)}), 404

    @app.errorhandler(PermissionError)
    def permission_error(e):
        return jsonify({"error": str(e)}), 401
