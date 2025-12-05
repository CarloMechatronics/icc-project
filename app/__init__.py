import os
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

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

    def _seed_admin():
        """Crea/actualiza un admin por defecto si no existe."""
        try:
            from app.repositories import UserRepository
            from app.models import GlobalRole

            email = os.getenv("SEED_ADMIN_EMAIL", "carlo.torres@utec.edu.pe").lower()
            name = os.getenv("SEED_ADMIN_NAME", "Carlo Torres")
            password = os.getenv("SEED_ADMIN_PASSWORD", "carlo123")

            repo = UserRepository()
            user = repo.get_by_email(email)
            if not user:
                user = repo.create_user(email=email, name=name, password_hash=generate_password_hash(password))
            if user.global_role != GlobalRole.SYSTEM_ADMIN:
                repo.update_user(user, role=GlobalRole.SYSTEM_ADMIN)
        except Exception as exc:  # pragma: no cover - best effort
            app.logger.warning("Seed admin skipped: %s", exc)

    with app.app_context():
        _seed_admin()

    # Shell context for flask shell
    @app.shell_context_processor
    def _shell_context():  # pragma: no cover - dev helper
        from app import models

        return {"db": db, "models": models}

    return app


__all__ = ["create_app", "db", "migrate"]
