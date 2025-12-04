from datetime import datetime

from app.models import Home
from .base import BaseRepository


class HomeRepository(BaseRepository):
    def create_home(self, name: str, timezone: str, description: str | None = None, address: str | None = None):
        now = datetime.utcnow()
        home = Home(
            name=name,
            timezone=timezone,
            description=description,
            address=address,
            created_at=now,
            updated_at=now,
        )
        self.add(home)
        self.commit()
        return home

    def list_homes(self):
        return Home.query.order_by(Home.id.asc()).all()

    def get_first(self):
        return Home.query.first()

    def get_by_id(self, home_id: int):
        return Home.query.get(home_id)
