from flask import Flask
from flask_cors import CORS

from src.config.settings import Config
from src.database import init_db, get_db
from src.models.task_model import TaskModel
from src.models.user_model import UserModel
from src.controllers.auth_controller import AuthController
from src.controllers.task_controller import TaskController
from src.routes.auth_routes import create_auth_blueprint
from src.routes.task_routes import create_task_blueprint
from src.middlewares.error_handler import register_error_handlers


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, origins=Config.CORS_ORIGINS)

    db = get_db()

    user_model = UserModel(db)
    task_model = TaskModel(db)

    auth_ctrl = AuthController(user_model)
    task_ctrl = TaskController(task_model)

    app.register_blueprint(create_auth_blueprint(auth_ctrl))
    app.register_blueprint(create_task_blueprint(task_ctrl))

    register_error_handlers(app)

    return app


if __name__ == "__main__":
    init_db()
    app = create_app()
    app.run(debug=Config.DEBUG, port=Config.PORT)
