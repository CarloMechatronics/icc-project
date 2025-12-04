import os
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Global SQLAlchemy and Migrate instances
# Initialized in create_app

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name: str | None = None) -> Flask:
    """Application factory for the Flask app."""

    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates",
    )

    from app.config import get_config

    app.config.from_object(get_config(config_name))

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Blueprints
    from app.controllers import register_blueprints

    register_blueprints(app)

    # Shell context for flask shell
    @app.shell_context_processor
    def _shell_context():  # pragma: no cover - dev helper
        from app import models

        return {"db": db, "models": models}

    return app


__all__ = ["create_app", "db", "migrate"]
