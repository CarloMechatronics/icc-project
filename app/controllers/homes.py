from flask import Blueprint, jsonify, render_template, request

from app.services.home_service import HomeService

homes_bp = Blueprint("homes", __name__, url_prefix="/homes")
home_service = HomeService()


@homes_bp.get("")
def homes_page():
    homes = home_service.list_homes()
    return render_template("homes.html", homes=homes)


@homes_bp.get("/api")
def homes_api():
    homes = home_service.list_homes()
    return jsonify([home_service.to_dict(h) for h in homes])


@homes_bp.post("/api")
def create_home_api():
    payload = request.get_json(silent=True) or {}
    name = payload.get("name", "").strip() or "Hogar"
    timezone = payload.get("timezone", "UTC")
    description = payload.get("description")
    address = payload.get("address")
    home = home_service.create_home(name=name, timezone=timezone, description=description, address=address)
    return jsonify(home_service.to_dict(home)), 201
