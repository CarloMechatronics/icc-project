from app.models import GlobalRole, User
from .base import BaseRepository


class UserRepository(BaseRepository):
    def get_by_email(self, email: str):
        return User.query.filter_by(email=email).first()

    def create_user(self, email: str, name: str, password_hash: str):
        user = User(email=email, name=name, password=password_hash, global_role=GlobalRole.USER)
        self.add(user)
        self.commit()
        return user
