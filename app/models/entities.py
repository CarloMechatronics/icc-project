from datetime import datetime
from sqlalchemy import text

from app import db
from .base import TimestampMixin
from .enums import (
    DeviceState,
    DeviceType,
    EventOrigin,
    EventType,
    GlobalRole,
    HomeRole,
    MeasureType,
)


class User(db.Model, TimestampMixin):
    __tablename__ = "users"

    id = db.Column(db.BigInteger, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    global_role = db.Column(
        db.Enum(GlobalRole),
        nullable=False,
        default=GlobalRole.USER,
        server_default=GlobalRole.USER.value,
    )

    homes = db.relationship(
        "UserHome",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Home(db.Model, TimestampMixin):
    __tablename__ = "homes"

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(500))
    address = db.Column(db.String(500))
    timezone = db.Column(db.String(64), nullable=False)

    members = db.relationship(
        "UserHome",
        back_populates="home",
        cascade="all, delete-orphan",
    )
    controllers = db.relationship(
        "Controller",
        back_populates="home",
        cascade="all, delete-orphan",
    )
    devices = db.relationship(
        "Device",
        back_populates="home",
        cascade="all, delete-orphan",
    )
    readings = db.relationship(
        "Reading",
        back_populates="home",
        cascade="all, delete-orphan",
    )
    events = db.relationship(
        "Event",
        back_populates="home",
        cascade="all, delete-orphan",
    )
    rules = db.relationship(
        "Rule",
        back_populates="home",
        cascade="all, delete-orphan",
    )


class UserHome(db.Model, TimestampMixin):
    __tablename__ = "user_homes"
    __table_args__ = (
        db.UniqueConstraint(
            "user_id", "home_id", name="uk_user_homes_user_id_home_id"
        ),
    )

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(
        db.BigInteger,
        db.ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    home_id = db.Column(
        db.BigInteger,
        db.ForeignKey("homes.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    home_role = db.Column(db.Enum(HomeRole), nullable=False)
    can_manage_devices = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
        server_default=text("0"),
    )
    can_manage_rules = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
        server_default=text("0"),
    )
    can_view_metrics = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
        server_default=text("1"),
    )
    can_invite_members = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
        server_default=text("0"),
    )

    user = db.relationship("User", back_populates="homes")
    home = db.relationship("Home", back_populates="members")


class Controller(db.Model, TimestampMixin):
    __tablename__ = "controllers"
    __table_args__ = (db.Index("idx_controllers_home_id", "home_id"),)

    id = db.Column(db.BigInteger, primary_key=True)
    home_id = db.Column(
        db.BigInteger,
        db.ForeignKey("homes.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(500))
    ip_address = db.Column(db.String(64))
    hardware_id = db.Column(db.String(255), nullable=False, unique=True)

    home = db.relationship("Home", back_populates="controllers")
    devices = db.relationship(
        "Device", back_populates="controller", cascade="all, delete-orphan"
    )


class Device(db.Model, TimestampMixin):
    __tablename__ = "devices"
    __table_args__ = (
        db.Index("idx_devices_home_id", "home_id"),
        db.Index("idx_devices_controller_id", "controller_id"),
    )

    id = db.Column(db.BigInteger, primary_key=True)
    home_id = db.Column(
        db.BigInteger,
        db.ForeignKey("homes.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    controller_id = db.Column(
        db.BigInteger,
        db.ForeignKey("controllers.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    type = db.Column("type", db.Enum(DeviceType), nullable=False)
    pin = db.Column(db.SmallInteger, nullable=False)
    model = db.Column(db.String(255), nullable=False)
    http_path = db.Column(db.String(255))
    state = db.Column(db.Enum(DeviceState))
    active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
        server_default=text("1"),
        doc="0 inactive, 1 active",
    )

    home = db.relationship("Home", back_populates="devices")
    controller = db.relationship("Controller", back_populates="devices")
    readings = db.relationship(
        "Reading", back_populates="device", cascade="all, delete-orphan"
    )
    events = db.relationship(
        "Event", back_populates="device", cascade="all, delete-orphan"
    )
    rule_actions = db.relationship(
        "RuleAction", back_populates="device", cascade="all, delete-orphan"
    )


class Reading(db.Model):
    __tablename__ = "readings"
    __table_args__ = (
        db.Index("idx_readings_device_id_timestamp", "device_id", "timestamp"),
        db.Index("idx_readings_home_id_timestamp", "home_id", "timestamp"),
    )

    id = db.Column(db.BigInteger, primary_key=True)
    device_id = db.Column(
        db.BigInteger,
        db.ForeignKey("devices.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    home_id = db.Column(
        db.BigInteger,
        db.ForeignKey("homes.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    measure = db.Column(db.Enum(MeasureType), nullable=False)
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(32), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

    device = db.relationship("Device", back_populates="readings")
    home = db.relationship("Home", back_populates="readings")


class Event(db.Model):
    __tablename__ = "events"
    __table_args__ = (
        db.Index("idx_events_device_id_timestamp", "device_id", "timestamp"),
        db.Index("idx_events_home_id_timestamp", "home_id", "timestamp"),
    )

    id = db.Column(db.BigInteger, primary_key=True)
    device_id = db.Column(
        db.BigInteger,
        db.ForeignKey("devices.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    home_id = db.Column(
        db.BigInteger,
        db.ForeignKey("homes.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    type = db.Column("type", db.Enum(EventType), nullable=False)
    origin = db.Column(db.Enum(EventOrigin), nullable=False)
    detail = db.Column(db.String(500), nullable=False)
    prev_value = db.Column(db.Float, nullable=False)
    next_value = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

    device = db.relationship("Device", back_populates="events")
    home = db.relationship("Home", back_populates="events")


class Rule(db.Model):
    __tablename__ = "rules"

    id = db.Column(db.BigInteger, primary_key=True)
    home_id = db.Column(
        db.BigInteger,
        db.ForeignKey("homes.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    condition = db.Column(db.String(500), nullable=False)
    active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
        server_default=text("1"),
    )
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        "update_at",
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    home = db.relationship("Home", back_populates="rules")
    actions = db.relationship(
        "RuleAction", back_populates="rule", cascade="all, delete-orphan"
    )


class RuleAction(db.Model, TimestampMixin):
    __tablename__ = "rule_actions"
    __table_args__ = (db.Index("idx_rule_actions_rule_id", "rule_id"),)

    id = db.Column(db.BigInteger, primary_key=True)
    rule_id = db.Column(
        db.BigInteger,
        db.ForeignKey("rules.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    action_type = db.Column(db.String(50), nullable=False)
    device_id = db.Column(
        db.BigInteger,
        db.ForeignKey("devices.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )

    rule = db.relationship("Rule", back_populates="actions")
    device = db.relationship("Device", back_populates="rule_actions")
