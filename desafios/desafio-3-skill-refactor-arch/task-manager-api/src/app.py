import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from flask import Flask
from flask_cors import CORS
from database import db
from src.config.settings import Config
from src.controllers.task_controller import TaskController
from src.controllers.user_controller import UserController
from src.controllers.report_controller import ReportController
from src.views.task_routes import create_task_blueprint
from src.views.user_routes import create_user_blueprint
from src.views.report_routes import create_report_blueprint
from src.middlewares.error_handler import register_error_handlers


def create_app(config=Config):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DEBUG'] = config.DEBUG

    CORS(app, origins=config.CORS_ORIGINS)
    db.init_app(app)

    task_ctrl = TaskController()
    user_ctrl = UserController()
    report_ctrl = ReportController()

    app.register_blueprint(create_task_blueprint(task_ctrl))
    app.register_blueprint(create_user_blueprint(user_ctrl))
    app.register_blueprint(create_report_blueprint(report_ctrl))

    register_error_handlers(app)

    @app.route('/health')
    def health():
        return {'status': 'ok', 'database': 'connected'}

    @app.route('/')
    def index():
        return {'message': 'Task Manager API', 'version': '2.0'}

    with app.app_context():
        db.create_all()

    return app
