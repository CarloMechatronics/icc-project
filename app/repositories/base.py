from app import db


class BaseRepository:
    def add(self, entity):
        db.session.add(entity)
        return entity

    def delete(self, entity):
        db.session.delete(entity)

    def commit(self):
        db.session.commit()

    def flush(self):  # pragma: no cover - helper
        db.session.flush()

    def refresh(self, entity):  # pragma: no cover - helper
        db.session.refresh(entity)
        return entity
