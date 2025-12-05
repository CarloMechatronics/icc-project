from flask import Blueprint, render_template, redirect, url_for, session

from app.services.home_service import HomeService

pages_bp = Blueprint("pages", __name__)
home_service = HomeService()


@pages_bp.route("/")
def root():
    # Base route redirects to auth login
    return redirect(url_for("auth.login_form"))


@pages_bp.route("/dashboard")
def dashboard_list():
    # Redirigimos al listado de hogares unificado
    return redirect(url_for("homes.homes_page"))


@pages_bp.route("/dashboard/<int:home_id>")
def dashboard(home_id: int):
    if not session.get("user_id"):
        return redirect(url_for("auth.login_form"))

    home = home_service.home_repo.get_by_id(home_id)
    if not home:
        return redirect(url_for("pages.dashboard_list"))
    return render_template("dashboard.html", home=home)


@pages_bp.route("/home/<int:home_id>/dashboard")
def legacy_home_dashboard(home_id: int):
    # compatibilidad: redirige al nuevo path
    return redirect(url_for("pages.dashboard", home_id=home_id))
