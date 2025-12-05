from flask import Blueprint, jsonify, make_response, request
from io import BytesIO
from datetime import datetime

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

from app.models import MeasureType

from app.services.metrics_service import MetricsService

metrics_bp = Blueprint("metrics", __name__, url_prefix="/api/metrics")
metrics_service = MetricsService()


@metrics_bp.get("/summary")
def summary():
    return jsonify(metrics_service.summary())


@metrics_bp.get("/chart.png")
def chart_png():
    """Devuelve un PNG con las metricas mas recientes."""

    home_id = request.args.get("home_id", type=int)
    home, readings = metrics_service.get_home_and_readings(home_id=home_id, limit=60)

    fig, ax = plt.subplots(figsize=(7, 3))
    fig.patch.set_facecolor("#0c1423")
    ax.set_facecolor("#0c1423")

    if not readings:
        ax.text(
            0.5,
            0.5,
            "Sin datos disponibles",
            ha="center",
            va="center",
            color="#9fb1cc",
            fontsize=12,
        )
        ax.axis("off")
    else:
        temps = []
        hums = []
        motions = []
        for r in readings:
            ts = r.timestamp
            if not isinstance(ts, datetime):
                ts = datetime.utcnow()
            if r.measure is MeasureType.TEMPERATURE:
                temps.append((ts, r.value))
            elif r.measure is MeasureType.HUMIDITY:
                hums.append((ts, r.value))
            elif r.measure is MeasureType.MOTION:
                motions.append((ts, r.value))

        for series, color, label in (
            (temps, "#5dd5ff", "Temp (C)"),
            (hums, "#7ef3c3", "Hum (%)"),
        ):
            if series:
                series.sort(key=lambda x: x[0])
                ax.plot(
                    [x[0] for x in series],
                    [x[1] for x in series],
                    color=color,
                    linewidth=2,
                    label=label,
                )
                ax.fill_between(
                    [x[0] for x in series],
                    [x[1] for x in series],
                    alpha=0.08,
                    color=color,
                )

        if motions:
            motions.sort(key=lambda x: x[0])
            ax.scatter(
                [x[0] for x in motions],
                [x[1] * 100 for x in motions],
                color="#ffb347",
                label="Motion",
                s=18,
                alpha=0.8,
            )

        ax.legend(facecolor="#11182a", edgecolor="#1b2538", labelcolor="#f3f6fb")
        ax.grid(color="#1b2538", linestyle="--", linewidth=0.6, alpha=0.6)
        ax.set_xlabel("Tiempo", color="#9fb1cc")
        ax.set_ylabel("Lecturas", color="#9fb1cc")
        ax.tick_params(colors="#9fb1cc")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

    buf = BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", dpi=120, facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)

    resp = make_response(buf.read())
    resp.headers["Content-Type"] = "image/png"
    resp.headers["Cache-Control"] = "no-store"
    return resp
