from datetime import datetime

from app.models import Controller
from .base import BaseRepository


class ControllerRepository(BaseRepository):
    def get_by_hardware_id(self, hardware_id: str):
        return Controller.query.filter_by(hardware_id=hardware_id).first()

    def create_controller(self, home_id: int, name: str, hardware_id: str, description: str | None = None, ip_address: str | None = None):
        now = datetime.utcnow()
        controller = Controller(
            home_id=home_id,
            name=name,
            description=description,
            ip_address=ip_address,
            hardware_id=hardware_id,
            created_at=now,
            updated_at=now,
        )
        self.add(controller)
        self.commit()
        return controller
