from app.repositories import HomeRepository


class HomeService:
    def __init__(self, home_repo: HomeRepository | None = None):
        self.home_repo = home_repo or HomeRepository()

    def create_home(self, name: str, timezone: str, description: str | None = None, address: str | None = None):
        return self.home_repo.create_home(name=name, timezone=timezone, description=description, address=address)

    def list_homes(self):
        return self.home_repo.list_homes()

    def ensure_default(self, name: str = "Demo Home", timezone: str = "UTC"):
        home = self.home_repo.get_first()
        if home:
            return home
        return self.create_home(name=name, timezone=timezone)

    def to_dict(self, home):
        return {
            "id": home.id,
            "name": home.name,
            "description": home.description,
            "address": home.address,
            "timezone": home.timezone,
        }
