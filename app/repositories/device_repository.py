from datetime import datetime

from app.models import Device, DeviceState, DeviceType
from .base import BaseRepository


class DeviceRepository(BaseRepository):
    def get_by_name(self, name: str):
        return Device.query.filter_by(name=name).first()

    def list_devices(self):
        return Device.query.order_by(Device.id.asc()).all()

    def create_device(
        self,
        home_id: int,
        controller_id: int,
        name: str,
        description: str,
        model: str,
        pin: int = 0,
        http_path: str | None = None,
        type_: DeviceType = DeviceType.HYBRID,
        state: DeviceState | None = None,
    ):
        now = datetime.utcnow()
        device = Device(
            home_id=home_id,
            controller_id=controller_id,
            name=name,
            description=description,
            model=model,
            pin=pin,
            http_path=http_path,
            type=type_,
            state=state,
            created_at=now,
            updated_at=now,
        )
        self.add(device)
        self.commit()
        return device

    def update_state(self, device: Device, state: DeviceState | None = None, active: bool | None = None):
        if state is not None:
            device.state = state
        if active is not None:
            device.active = active
        return device
