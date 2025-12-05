from flask import Flask


def register_blueprints(app: Flask) -> None:
    """Register all blueprints for the application."""

    from .auth import auth_bp
    from .homes import homes_bp
    from .devices import devices_bp
    from .metrics import metrics_bp
    from .ia import ia_bp
    from .pages import pages_bp
    from .users import users_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(homes_bp)
    app.register_blueprint(devices_bp)
    app.register_blueprint(metrics_bp)
    app.register_blueprint(ia_bp)
    app.register_blueprint(pages_bp)
    app.register_blueprint(users_bp)


__all__ = ["register_blueprints"]
