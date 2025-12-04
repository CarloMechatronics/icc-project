from app.models import DeviceState, DeviceType
from app.repositories import ControllerRepository, DeviceRepository, HomeRepository


class DeviceService:
    def __init__(
        self,
        device_repo: DeviceRepository | None = None,
        home_repo: HomeRepository | None = None,
        controller_repo: ControllerRepository | None = None,
    ):
        self.device_repo = device_repo or DeviceRepository()
        self.home_repo = home_repo or HomeRepository()
        self.controller_repo = controller_repo or ControllerRepository()

    def ensure_device(
        self,
        name: str,
        description: str,
        model: str,
        pin: int = 0,
        type_: DeviceType = DeviceType.HYBRID,
    ):
        device = self.device_repo.get_by_name(name)
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
            name=name,
            description=description,
            model=model,
            pin=pin,
            type_=type_,
            state=DeviceState.OFF,
        )

    def list_devices(self):
        return self.device_repo.list_devices()

    def to_dict(self, device):
        return {
            "id": device.id,
            "name": device.name,
            "description": device.description,
            "model": device.model,
            "type": device.type.value if device.type else None,
            "state": device.state.value if device.state else None,
            "active": bool(device.active),
            "home_id": device.home_id,
            "controller_id": device.controller_id,
        }
