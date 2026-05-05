from flask import Flask
from flask_cors import CORS
from database import init_db
from routes.tasks import tasks_bp
from routes.auth import auth_bp

app = Flask(__name__)
# HIGH: CORS sem restrição de origem
CORS(app)
# CRITICAL: SECRET_KEY hardcoded
app.config["SECRET_KEY"] = "task-manager-secret-key-123"

app.register_blueprint(tasks_bp)
app.register_blueprint(auth_bp)

if __name__ == "__main__":
    init_db()
    # LOW: debug=True em produção
    app.run(debug=True, port=5001)
