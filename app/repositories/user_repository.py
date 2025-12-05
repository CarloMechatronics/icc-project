from app.models import GlobalRole, User
from .base import BaseRepository


class UserRepository(BaseRepository):
    def get_by_email(self, email: str):
        return User.query.filter_by(email=email).first()

    def get_by_id(self, user_id: int):
        return User.query.get(user_id)

    def list_users(self):
        return User.query.order_by(User.id.asc()).all()

    def create_user(self, email: str, name: str, password_hash: str):
        user = User(email=email, name=name, password=password_hash, global_role=GlobalRole.USER)
        self.add(user)
        self.commit()
        return user

    def update_user(self, user: User, *, email: str | None = None, name: str | None = None, password_hash: str | None = None, role: GlobalRole | None = None):
        if email is not None:
            user.email = email
        if name is not None:
            user.name = name
        if password_hash is not None:
            user.password = password_hash
        if role is not None:
            user.global_role = role
        self.commit()
        return user

    def delete_user(self, user: User):
        self.delete(user)
        self.commit()
