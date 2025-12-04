import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URI",
        "mysql+pymysql://smarthome:smarthome@localhost:3306/smarthome",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    API_TOKEN = os.getenv("API_TOKEN", "")
    DEFAULT_HOME_TZ = os.getenv("DEFAULT_HOME_TZ", "UTC")
    # Si se establece, el frontend consumira este host en lugar del mismo origen
    # Ejemplo: http://44.222.106.109:8000
    API_BASE_URL = os.getenv("API_BASE_URL", "")


class DevConfig(Config):
    DEBUG = True


class ProdConfig(Config):
    DEBUG = False


def get_config(name: str | None = None):
    if name and name.lower().startswith("prod"):
        return ProdConfig
    env = os.getenv("FLASK_ENV", "dev").lower()
    if env.startswith("prod"):
        return ProdConfig
    if env.startswith("dev") or env.startswith("local"):
        return DevConfig
    return Config
