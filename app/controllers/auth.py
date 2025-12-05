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
    session["user_role"] = user.global_role.value if hasattr(user, "global_role") else None
    flash("Bienvenido/a", "success")
    return redirect(url_for("homes.homes_page"))


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

    try:
        user = auth_service.register_user(email=email, name=name, password=password)
    except ValueError:
        flash("El correo ya esta registrado", "error")
        return redirect(url_for("auth.register_form"))

    session["user_id"] = user.id
    session["user_name"] = user.name
    session["user_role"] = user.global_role.value if hasattr(user, "global_role") else None
    flash("Cuenta creada", "success")
    return redirect(url_for("homes.homes_page"))


@auth_bp.get("/forgot-password")
def forgot_password_form():
    return render_template("auth/forgot_password.html")


@auth_bp.post("/forgot-password")
def forgot_password_submit():
    email = request.form.get("email", "").strip().lower()
    # For demo purposes, we don't send emails; just flash a message
    flash("Si el correo existe en el sistema, se enviaron instrucciones.", "info")
    return redirect(url_for("auth.login_form"))


@auth_bp.post("/logout")
def logout():
    session.clear()
    flash("Sesion cerrada", "info")
    return redirect(url_for("auth.login_form"))
