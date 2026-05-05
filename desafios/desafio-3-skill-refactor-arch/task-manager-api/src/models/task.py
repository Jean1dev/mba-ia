from database import db
from datetime import datetime
from sqlalchemy.orm import joinedload


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='pending')
    priority = db.Column(db.Integer, default=3)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    tags = db.Column(db.String(500), nullable=True)

    user = db.relationship('User', backref='tasks')
    category = db.relationship('Category', backref='tasks')

    def to_dict(self, include_relations=False):
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'created_at': str(self.created_at),
            'updated_at': str(self.updated_at),
            'due_date': str(self.due_date) if self.due_date else None,
            'tags': self.tags.split(',') if self.tags else [],
            'overdue': self.is_overdue(),
        }
        if include_relations:
            data['user_name'] = self.user.name if self.user else None
            data['category_name'] = self.category.name if self.category else None
        return data

    def is_overdue(self):
        return (
            self.due_date is not None
            and self.due_date < datetime.utcnow()
            and self.status not in ('done', 'cancelled')
        )

    @classmethod
    def find_all_with_relations(cls):
        return cls.query.options(
            joinedload(cls.user),
            joinedload(cls.category),
        ).all()
