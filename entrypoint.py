from flask import Flask
from extensions import db, ma
from config.local import LocalConfig

def create_app():
    app = Flask(__name__)
    app.config.from_object(LocalConfig)

    db.init_app(app)
    ma.init_app(app)

    from routes.auth_routes import auth_bp
    from routes.task_routes import task_bp

    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(task_bp, url_prefix="/api")

    return app

app = create_app()