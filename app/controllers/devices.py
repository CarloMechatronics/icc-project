from __future__ import annotations

import os
from typing import Any, Dict

import requests
from flask import Blueprint, current_app, jsonify, request

from app.services.control_service import ControlService
from app.services.device_service import DeviceService
from app.services.telemetry_service import TelemetryService


# Blueprint raiz /api usado por el frontend local.
# Esta capa actua como proxy hacia el backend real que ya tienes en EC2
# (el blueprint de telemetria que expone /api, /api/temp, /api/control, etc.).

REMOTE_API_ROOT = os.getenv("REMOTE_API_ROOT", "http://44.222.106.109:8000")


def _auth_headers() -> Dict[str, str]:
    token = current_app.config.get("API_TOKEN", "")
    headers: Dict[str, str] = {}
    if token:
        headers["X-API-Key"] = token
    return headers


devices_bp = Blueprint("devices", __name__, url_prefix="/api")

# Instancias locales (no se usan para EC2 pero se conservan por si las necesitas)
telemetry_service = TelemetryService()
control_service = ControlService()
device_service = DeviceService()


@devices_bp.get("")
@devices_bp.get("/")
def list_telemetry():
    """Proxy opcional de GET /api hacia el backend remoto.

    El dashboard usa esta ruta para mostrar lecturas sin consultar directo al EC2.
    Si el backend remoto responde con error, devolvemos el error tal cual.
    """

    params: Dict[str, Any] = {}
    if "limit" in request.args:
        params["limit"] = request.args["limit"]
    if "device" in request.args:
        params["device"] = request.args["device"]

    try:
        resp = requests.get(
            f"{REMOTE_API_ROOT}/api",
            params=params,
            headers=_auth_headers(),
            timeout=5,
        )
    except requests.RequestException as exc:  # pragma: no cover - red
        return jsonify({"error": "remote_unreachable", "detail": str(exc)}), 502

    try:
        data = resp.json()
    except ValueError:  # pragma: no cover - formato inesperado
        data = {"error": "invalid_json"}

    return jsonify(data), resp.status_code


@devices_bp.post("")
@devices_bp.post("/")
def ingest_telemetry():
    """Proxy opcional de POST /api hacia el backend remoto.

    En la practica el ESP32 ya habla directo al EC2, por lo que este endpoint
    solo se usa si quieres enviar datos de prueba desde el navegador/local.
    """

    payload = request.get_json(silent=True) or {}
    try:
        resp = requests.post(
            f"{REMOTE_API_ROOT}/api",
            json=payload,
            headers=_auth_headers(),
            timeout=5,
        )
    except requests.RequestException as exc:  # pragma: no cover - red
        return jsonify({"error": "remote_unreachable", "detail": str(exc)}), 502

    return jsonify(resp.json()), resp.status_code


def _proxy_sensor(sensor_name: str):
    """Llama al backend remoto (/api/<sensor>) y normaliza el formato.

    El backend remoto devuelve: {device, sensor, value, ts, time}.
    Aqui lo convertimos a: {device, <sensor_name>: value, timestamp}.
    """

    params: Dict[str, Any] = {}
    if "device" in request.args:
        params["device"] = request.args["device"]

    try:
        resp = requests.get(
            f"{REMOTE_API_ROOT}/api/{sensor_name}",
            params=params,
            headers=_auth_headers(),
            timeout=5,
        )
    except requests.RequestException as exc:  # pragma: no cover - red
        return None, 502, {"error": "remote_unreachable", "detail": str(exc)}

    if resp.status_code != 200:
        # Intentamos propagar un mensaje de error legible
        try:
            data = resp.json()
        except Exception:  # pragma: no cover - formato inesperado
            data = {"error": "remote_error"}
        return None, resp.status_code, data

    data = resp.json()
    device = data.get("device")
    value = data.get("value")
    timestamp = data.get("time")

    norm = {"device": device, "timestamp": timestamp}
    norm[sensor_name] = value
    return norm, 200, None


@devices_bp.get("/telemetry/latest")
def latest_telemetry():
    """Agrega temp/hum/motion desde el backend remoto.

    Esto no es usado directamente por el firmware, solo por el dashboard si se quiere.
    """

    metrics: Dict[str, Any] = {}
    timestamp = None
    for name in ("temp", "hum", "motion"):
        norm, status, err = _proxy_sensor(name)
        if status != 200 or not norm:
            continue
        metrics[name] = norm.get(name)
        timestamp = timestamp or norm.get("timestamp")

    return jsonify({"device": request.args.get("device", "esp32-1"), "metrics": metrics, "timestamp": timestamp})


@devices_bp.get("/temp")
def latest_temp():
    norm, status, err = _proxy_sensor("temp")
    if status != 200 or not norm:
        return jsonify(err or {"error": "no_data"}), status
    return jsonify(norm), 200


@devices_bp.get("/hum")
def latest_humidity():
    norm, status, err = _proxy_sensor("hum")
    if status != 200 or not norm:
        return jsonify(err or {"error": "no_data"}), status
    return jsonify(norm), 200


@devices_bp.get("/motion")
def latest_motion():
    norm, status, err = _proxy_sensor("motion")
    if status != 200 or not norm:
        return jsonify(err or {"error": "no_data"}), status
    # motion se devuelve como booleano
    motion_value = bool(norm.get("motion")) if norm.get("motion") is not None else None
    return jsonify({"device": norm.get("device"), "motion": motion_value, "timestamp": norm.get("timestamp")}), 200


@devices_bp.post("/control")
def set_control():
    """Proxy de POST /api/control hacia el backend remoto."""

    payload = request.get_json(silent=True) or {}
    try:
        resp = requests.post(
            f"{REMOTE_API_ROOT}/api/control",
            json=payload,
            headers=_auth_headers(),
            timeout=5,
        )
    except requests.RequestException as exc:  # pragma: no cover - red
        return jsonify({"error": "remote_unreachable", "detail": str(exc)}), 502

    return jsonify(resp.json()), resp.status_code


@devices_bp.get("/control")
def get_control():
    """Proxy de GET /api/control hacia el backend remoto."""

    params: Dict[str, Any] = {}
    if "device" in request.args:
        params["device"] = request.args["device"]

    try:
        resp = requests.get(
            f"{REMOTE_API_ROOT}/api/control",
            params=params,
            headers=_auth_headers(),
            timeout=5,
        )
    except requests.RequestException as exc:  # pragma: no cover - red
        return jsonify({"error": "remote_unreachable", "detail": str(exc)}), 502

    return jsonify(resp.json()), resp.status_code


@devices_bp.get("/devices")
def list_devices():
    """Endpoint local de conveniencia; no depende del backend remoto."""

    items = device_service.list_devices()
    return jsonify([device_service.to_dict(d) for d in items])
