from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from werkzeug.security import generate_password_hash

from app.models import GlobalRole
from app.repositories import UserRepository

users_bp = Blueprint("users", __name__, url_prefix="/users")
user_repo = UserRepository()


def _require_admin():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login_form"))
    user = user_repo.get_by_id(user_id)
    if not user or user.global_role != GlobalRole.SYSTEM_ADMIN:
        flash("Acceso solo para administradores", "error")
        return redirect(url_for("homes.homes_page"))
    return user


@users_bp.get("")
def users_page():
    admin = _require_admin()
    if not getattr(admin, "id", None):
        return admin
    users = user_repo.list_users()
    return render_template("users.html", users=users, GlobalRole=GlobalRole)


@users_bp.post("")
def create_user():
    admin = _require_admin()
    if not getattr(admin, "id", None):
        return admin

    email = request.form.get("email", "").strip().lower()
    name = request.form.get("name", "").strip()
    password = request.form.get("password", "")
    role_str = request.form.get("role", GlobalRole.USER.value)
    role = GlobalRole(role_str) if role_str in [r.value for r in GlobalRole] else GlobalRole.USER

    if not email or not name or not password:
        flash("Completa todos los campos", "error")
        return redirect(url_for("users.users_page"))

    if user_repo.get_by_email(email):
        flash("El correo ya existe", "error")
        return redirect(url_for("users.users_page"))

    pwd_hash = generate_password_hash(password)
    user_repo.create_user(email=email, name=name, password_hash=pwd_hash)
    # Actualizar rol si no es USER
    new_user = user_repo.get_by_email(email)
    if new_user and role != GlobalRole.USER:
        user_repo.update_user(new_user, role=role)
    flash("Usuario creado", "success")
    return redirect(url_for("users.users_page"))


@users_bp.post("/<int:user_id>/update")
def update_user(user_id: int):
    admin = _require_admin()
    if not getattr(admin, "id", None):
        return admin

    user = user_repo.get_by_id(user_id)
    if not user:
        flash("Usuario no encontrado", "error")
        return redirect(url_for("users.users_page"))

    email = request.form.get("email", "").strip().lower()
    name = request.form.get("name", "").strip()
    password = request.form.get("password", "")
    role_str = request.form.get("role", user.global_role.value)
    role = GlobalRole(role_str) if role_str in [r.value for r in GlobalRole] else user.global_role

    if not email or not name:
        flash("Email y nombre son obligatorios", "error")
        return redirect(url_for("users.users_page"))

    existing = user_repo.get_by_email(email)
    if existing and existing.id != user_id:
        flash("El correo ya existe en otro usuario", "error")
        return redirect(url_for("users.users_page"))

    pwd_hash = generate_password_hash(password) if password else None
    user_repo.update_user(user, email=email, name=name, password_hash=pwd_hash, role=role)
    flash("Usuario actualizado", "success")
    return redirect(url_for("users.users_page"))


@users_bp.post("/<int:user_id>/delete")
def delete_user(user_id: int):
    admin = _require_admin()
    if not getattr(admin, "id", None):
        return admin

    if user_id == session.get("user_id"):
        flash("No puedes eliminar tu propio usuario", "error")
        return redirect(url_for("users.users_page"))

    user = user_repo.get_by_id(user_id)
    if not user:
        flash("Usuario no encontrado", "error")
        return redirect(url_for("users.users_page"))

    user_repo.delete_user(user)
    flash("Usuario eliminado", "success")
    return redirect(url_for("users.users_page"))
