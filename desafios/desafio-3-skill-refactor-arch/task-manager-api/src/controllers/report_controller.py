from database import db
from src.models.task import Task
from src.models.user import User
from src.models.category import Category
from datetime import datetime, timedelta
from sqlalchemy import func


class ReportController:
    def summary(self):
        total_tasks = Task.query.count()
        total_users = User.query.count()
        total_categories = Category.query.count()

        status_counts = dict(
            db.session.query(Task.status, func.count(Task.id)).group_by(Task.status).all()
        )

        priority_labels = {1: 'critical', 2: 'high', 3: 'medium', 4: 'low', 5: 'minimal'}
        priority_counts = dict(
            db.session.query(Task.priority, func.count(Task.id)).group_by(Task.priority).all()
        )

        overdue_tasks = [
            t for t in Task.query.filter(
                Task.due_date.isnot(None),
                Task.status.notin_(['done', 'cancelled'])
            ).all()
            if t.is_overdue()
        ]
        overdue_list = [
            {
                'id': t.id,
                'title': t.title,
                'due_date': str(t.due_date),
                'days_overdue': (datetime.utcnow() - t.due_date).days,
            }
            for t in overdue_tasks
        ]

        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_tasks = Task.query.filter(Task.created_at >= seven_days_ago).count()
        recent_done = Task.query.filter(
            Task.status == 'done', Task.updated_at >= seven_days_ago
        ).count()

        user_stats_raw = (
            db.session.query(
                User.id,
                User.name,
                func.count(Task.id).label('total'),
                func.sum(func.case((Task.status == 'done', 1), else_=0)).label('completed'),
            )
            .outerjoin(Task, Task.user_id == User.id)
            .group_by(User.id)
            .all()
        )
        user_stats = [
            {
                'user_id': row.id,
                'user_name': row.name,
                'total_tasks': row.total or 0,
                'completed_tasks': row.completed or 0,
                'completion_rate': round((row.completed / row.total) * 100, 2)
                if row.total else 0,
            }
            for row in user_stats_raw
        ]

        return {
            'generated_at': str(datetime.utcnow()),
            'overview': {
                'total_tasks': total_tasks,
                'total_users': total_users,
                'total_categories': total_categories,
            },
            'tasks_by_status': {
                'pending': status_counts.get('pending', 0),
                'in_progress': status_counts.get('in_progress', 0),
                'done': status_counts.get('done', 0),
                'cancelled': status_counts.get('cancelled', 0),
            },
            'tasks_by_priority': {
                priority_labels.get(k, str(k)): v for k, v in priority_counts.items()
            },
            'overdue': {'count': len(overdue_list), 'tasks': overdue_list},
            'recent_activity': {
                'tasks_created_last_7_days': recent_tasks,
                'tasks_completed_last_7_days': recent_done,
            },
            'user_productivity': user_stats,
        }

    def user_report(self, user_id):
        user = User.query.get(user_id)
        if not user:
            raise LookupError('Usuário não encontrado')

        tasks = Task.query.filter_by(user_id=user_id).all()
        by_status = {}
        overdue = 0
        high_priority = 0
        for t in tasks:
            by_status[t.status] = by_status.get(t.status, 0) + 1
            if t.priority <= 2:
                high_priority += 1
            if t.is_overdue():
                overdue += 1

        total = len(tasks)
        done = by_status.get('done', 0)
        return {
            'user': {'id': user.id, 'name': user.name, 'email': user.email},
            'statistics': {
                'total_tasks': total,
                'done': done,
                'pending': by_status.get('pending', 0),
                'in_progress': by_status.get('in_progress', 0),
                'cancelled': by_status.get('cancelled', 0),
                'overdue': overdue,
                'high_priority': high_priority,
                'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
            },
        }

    def get_categories(self):
        categories = Category.query.all()
        counts = dict(
            db.session.query(Task.category_id, func.count(Task.id))
            .group_by(Task.category_id)
            .all()
        )
        result = []
        for c in categories:
            data = c.to_dict()
            data['task_count'] = counts.get(c.id, 0)
            result.append(data)
        return result

    def create_category(self, data):
        name = data.get('name', '').strip()
        if not name:
            raise ValueError('Nome é obrigatório')
        cat = Category(
            name=name,
            description=data.get('description', ''),
            color=data.get('color', '#000000'),
        )
        db.session.add(cat)
        db.session.commit()
        return cat.to_dict()

    def update_category(self, cat_id, data):
        cat = Category.query.get(cat_id)
        if not cat:
            raise LookupError('Categoria não encontrada')
        if 'name' in data:
            cat.name = data['name']
        if 'description' in data:
            cat.description = data['description']
        if 'color' in data:
            cat.color = data['color']
        db.session.commit()
        return cat.to_dict()

    def delete_category(self, cat_id):
        cat = Category.query.get(cat_id)
        if not cat:
            raise LookupError('Categoria não encontrada')
        db.session.delete(cat)
        db.session.commit()
