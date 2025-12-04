from datetime import datetime

from app.models import MeasureType, Reading
from .base import BaseRepository


class ReadingRepository(BaseRepository):
    def add_reading(self, device_id: int, home_id: int, measure: MeasureType, value: float, unit: str):
        reading = Reading(
            device_id=device_id,
            home_id=home_id,
            measure=measure,
            value=value,
            unit=unit,
            timestamp=datetime.utcnow(),
        )
        self.add(reading)
        return reading

    def latest_by_device(self, device_id: int):
        return (
            Reading.query.filter_by(device_id=device_id)
            .order_by(Reading.timestamp.desc())
            .first()
        )

    def latest_by_home(self, home_id: int, limit: int = 50):
        return (
            Reading.query.filter_by(home_id=home_id)
            .order_by(Reading.timestamp.desc())
            .limit(limit)
            .all()
        )
