from flask import Blueprint, jsonify

from app.services.metrics_service import MetricsService

metrics_bp = Blueprint("metrics", __name__, url_prefix="/api/metrics")
metrics_service = MetricsService()


@metrics_bp.get("/summary")
def summary():
    return jsonify(metrics_service.summary())
