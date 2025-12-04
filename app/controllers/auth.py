from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
auth_service = AuthService()


@auth_bp.get("/login")
def login_form():
    return render_template("auth/login.html")


@auth_bp.post("/login")
def login_submit():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    user = auth_service.authenticate(email=email, password=password)
    if not user:
        flash("Credenciales invalidas", "error")
        return redirect(url_for("auth.login_form"))

    session["user_id"] = user.id
    session["user_name"] = user.name
    flash("Bienvenido/a", "success")
    return redirect(url_for("pages.dashboard"))


@auth_bp.get("/register")
def register_form():
    return render_template("auth/register.html")


@auth_bp.post("/register")
def register_submit():
    email = request.form.get("email", "").strip().lower()
    name = request.form.get("name", "").strip()
    password = request.form.get("password", "")
    if not email or not name or not password:
        flash("Completa todos los campos", "error")
        return redirect(url_for("auth.register_form"))

    user = auth_service.register_user(email=email, name=name, password=password)
    session["user_id"] = user.id
    session["user_name"] = user.name
    flash("Cuenta creada", "success")
    return redirect(url_for("pages.dashboard"))


@auth_bp.post("/logout")
def logout():
    session.clear()
    flash("Sesion cerrada", "info")
    return redirect(url_for("auth.login_form"))
