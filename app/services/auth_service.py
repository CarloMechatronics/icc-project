from werkzeug.security import check_password_hash, generate_password_hash

from app.repositories import UserRepository


class AuthService:
    def __init__(self, user_repo: UserRepository | None = None):
        self.user_repo = user_repo or UserRepository()

    def register_user(self, email: str, name: str, password: str):
        existing = self.user_repo.get_by_email(email)
        if existing:
            raise ValueError("email_exists")
        password_hash = generate_password_hash(password)
        return self.user_repo.create_user(email=email, name=name, password_hash=password_hash)

    def authenticate(self, email: str, password: str):
        user = self.user_repo.get_by_email(email)
        if not user:
            return None
        if not check_password_hash(user.password, password):
            return None
        return user
