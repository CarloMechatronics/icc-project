from datetime import datetime

from app.repositories import HomeRepository, ReadingRepository


class MetricsService:
    def __init__(self, reading_repo: ReadingRepository | None = None, home_repo: HomeRepository | None = None):
        self.reading_repo = reading_repo or ReadingRepository()
        self.home_repo = home_repo or HomeRepository()

    def get_home_and_readings(self, home_id: int | None = None, limit: int = 50):
        home = None
        if home_id:
            home = self.home_repo.get_by_id(home_id)
        if not home:
            home = self.home_repo.get_first()
        if not home:
            return None, []
        readings = self.reading_repo.latest_by_home(home.id, limit=limit)
        return home, readings

    def summary(self):
        home = self.home_repo.get_first()
        if not home:
            return {
                "home": None,
                "counts": {"homes": 0, "readings": 0},
                "last": None,
            }
        readings = self.reading_repo.latest_by_home(home.id, limit=20)
        counts = len(readings)
        last = readings[0] if readings else None
        return {
            "home": {
                "id": home.id,
                "name": home.name,
            },
            "counts": {"homes": 1, "readings": counts},
            "last": {
                "measure": last.measure.value if last else None,
                "value": last.value if last else None,
                "timestamp": last.timestamp.isoformat() if last else None,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
