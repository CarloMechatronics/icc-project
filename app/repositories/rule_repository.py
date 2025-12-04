from app.models import Rule
from .base import BaseRepository


class RuleRepository(BaseRepository):
    def list_by_home(self, home_id: int):
        return Rule.query.filter_by(home_id=home_id).order_by(Rule.id.asc()).all()
