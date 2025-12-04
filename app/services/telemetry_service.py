from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from app import db
from app.models import DeviceState, DeviceType, MeasureType
from app.repositories import (
    ControllerRepository,
    DeviceRepository,
    HomeRepository,
    ReadingRepository,
)


class TelemetryService:
    def __init__(
        self,
        device_repo: DeviceRepository | None = None,
        home_repo: HomeRepository | None = None,
        controller_repo: ControllerRepository | None = None,
        reading_repo: ReadingRepository | None = None,
    ):
        self.device_repo = device_repo or DeviceRepository()
        self.home_repo = home_repo or HomeRepository()
        self.controller_repo = controller_repo or ControllerRepository()
        self.reading_repo = reading_repo or ReadingRepository()
        self._latest_cache: Dict[str, Dict[str, Any]] = {}

    def _ensure_device_graph(self, device_name: str):
        device = self.device_repo.get_by_name(device_name)
        if device:
            return device
        home = self.home_repo.get_first() or self.home_repo.create_home(
            name="Demo Home", timezone="UTC"
        )
        controller = self.controller_repo.get_by_hardware_id("esp32-gw")
        if not controller:
            controller = self.controller_repo.create_controller(
                home_id=home.id,
                name="ESP32 Gateway",
                hardware_id="esp32-gw",
                description="Auto-registrado",
            )
        return self.device_repo.create_device(
            home_id=home.id,
            controller_id=controller.id,
            name=device_name,
            description="Dispositivo IoT",
            model=device_name,
            type_=DeviceType.HYBRID,
        )

    def ingest(self, payload: Dict[str, Any]):
        device_name = payload.get("device", "esp32-1")
        device = self._ensure_device_graph(device_name)

        metrics: Dict[str, Any] = {}
        now = datetime.utcnow()

        temp = payload.get("temp")
        hum = payload.get("hum")
        motion = payload.get("motion")

        if temp is not None:
            self.reading_repo.add_reading(
                device_id=device.id,
                home_id=device.home_id,
                measure=MeasureType.TEMPERATURE,
                value=float(temp),
                unit="C",
            )
            metrics["temp"] = float(temp)

        if hum is not None:
            self.reading_repo.add_reading(
                device_id=device.id,
                home_id=device.home_id,
                measure=MeasureType.HUMIDITY,
                value=float(hum),
                unit="%",
            )
            metrics["hum"] = float(hum)

        if motion is not None:
            self.reading_repo.add_reading(
                device_id=device.id,
                home_id=device.home_id,
                measure=MeasureType.MOTION,
                value=1.0 if motion else 0.0,
                unit="bool",
            )
            metrics["motion"] = bool(motion)

        # Device state updates
        door_open = payload.get("door_open")
        door_angle = payload.get("door_angle")
        led1 = payload.get("led1")
        led2 = payload.get("led2")

        if door_open is not None:
            device.state = DeviceState.OPEN if door_open else DeviceState.CLOSED
        if led1 is True or led2 is True:
            device.state = DeviceState.ON
        if led1 is False and led2 is False and door_open is False:
            device.state = DeviceState.OFF

        db.session.commit()

        self._latest_cache[device_name] = {
            "device": device_name,
            "timestamp": now.isoformat(),
            "metrics": metrics,
            "motion": bool(motion) if motion is not None else None,
            "door_open": door_open,
            "door_angle": door_angle,
            "led1": led1,
            "led2": led2,
        }

        return {"status": "ingested", "device": device_name, "metrics": metrics}

    def get_latest(self, device_name: str):
        cached = self._latest_cache.get(device_name)
        if cached:
            return cached

        device = self.device_repo.get_by_name(device_name)
        if not device:
            return {
                "device": device_name,
                "metrics": {},
                "timestamp": None,
                "message": "sin datos",
            }

        readings = self.reading_repo.latest_by_home(device.home_id, limit=10)
        metrics: Dict[str, Any] = {}
        timestamp = None
        for r in readings:
            # Normalizamos a las mismas claves usadas en ingest: temp, hum, motion
            if r.measure is MeasureType.TEMPERATURE and "temp" not in metrics:
                metrics["temp"] = r.value
                timestamp = timestamp or r.timestamp.isoformat()
            elif r.measure is MeasureType.HUMIDITY and "hum" not in metrics:
                metrics["hum"] = r.value
                timestamp = timestamp or r.timestamp.isoformat()
            elif r.measure is MeasureType.MOTION and "motion" not in metrics:
                metrics["motion"] = bool(r.value)
                timestamp = timestamp or r.timestamp.isoformat()

        return {
            "device": device_name,
            "metrics": metrics,
            "timestamp": timestamp,
        }
