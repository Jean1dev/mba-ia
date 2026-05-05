from database import db
from src.models.task import Task
from src.models.user import User
from src.models.category import Category
from src.config.settings import VALID_STATUSES
from datetime import datetime


class TaskController:
    def get_all(self):
        tasks = Task.find_all_with_relations()
        return [t.to_dict(include_relations=True) for t in tasks]

    def get_by_id(self, task_id):
        task = Task.query.get(task_id)
        if not task:
            raise LookupError('Task não encontrada')
        return task.to_dict(include_relations=True)

    def create(self, data):
        title = data.get('title', '').strip()
        if not title:
            raise ValueError('Título é obrigatório')
        if len(title) < 3:
            raise ValueError('Título muito curto')
        if len(title) > 200:
            raise ValueError('Título muito longo')

        status = data.get('status', 'pending')
        if status not in VALID_STATUSES:
            raise ValueError('Status inválido')

        priority = data.get('priority', 3)
        if not (1 <= priority <= 5):
            raise ValueError('Prioridade deve ser entre 1 e 5')

        user_id = data.get('user_id')
        if user_id and not User.query.get(user_id):
            raise LookupError('Usuário não encontrado')

        category_id = data.get('category_id')
        if category_id and not Category.query.get(category_id):
            raise LookupError('Categoria não encontrada')

        task = Task(
            title=title,
            description=data.get('description', ''),
            status=status,
            priority=priority,
            user_id=user_id,
            category_id=category_id,
        )

        due_date = data.get('due_date')
        if due_date:
            try:
                task.due_date = datetime.strptime(due_date, '%Y-%m-%d')
            except ValueError:
                raise ValueError('Formato de data inválido. Use YYYY-MM-DD')

        tags = data.get('tags')
        if tags:
            task.tags = ','.join(tags) if isinstance(tags, list) else tags

        db.session.add(task)
        db.session.commit()
        return task.to_dict()

    def update(self, task_id, data):
        task = Task.query.get(task_id)
        if not task:
            raise LookupError('Task não encontrada')

        if 'title' in data:
            title = data['title']
            if len(title) < 3:
                raise ValueError('Título muito curto')
            if len(title) > 200:
                raise ValueError('Título muito longo')
            task.title = title

        if 'description' in data:
            task.description = data['description']

        if 'status' in data:
            if data['status'] not in VALID_STATUSES:
                raise ValueError('Status inválido')
            task.status = data['status']

        if 'priority' in data:
            if not (1 <= data['priority'] <= 5):
                raise ValueError('Prioridade deve ser entre 1 e 5')
            task.priority = data['priority']

        if 'user_id' in data:
            if data['user_id'] and not User.query.get(data['user_id']):
                raise LookupError('Usuário não encontrado')
            task.user_id = data['user_id']

        if 'category_id' in data:
            if data['category_id'] and not Category.query.get(data['category_id']):
                raise LookupError('Categoria não encontrada')
            task.category_id = data['category_id']

        if 'due_date' in data:
            if data['due_date']:
                try:
                    task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
                except ValueError:
                    raise ValueError('Formato de data inválido')
            else:
                task.due_date = None

        if 'tags' in data:
            tags = data['tags']
            task.tags = ','.join(tags) if isinstance(tags, list) else tags

        task.updated_at = datetime.utcnow()
        db.session.commit()
        return task.to_dict()

    def delete(self, task_id):
        task = Task.query.get(task_id)
        if not task:
            raise LookupError('Task não encontrada')
        db.session.delete(task)
        db.session.commit()

    def search(self, q='', status='', priority='', user_id=''):
        query = Task.query
        if q:
            query = query.filter(
                db.or_(Task.title.like(f'%{q}%'), Task.description.like(f'%{q}%'))
            )
        if status:
            query = query.filter(Task.status == status)
        if priority:
            query = query.filter(Task.priority == int(priority))
        if user_id:
            query = query.filter(Task.user_id == int(user_id))
        return [t.to_dict() for t in query.all()]

    def stats(self):
        from sqlalchemy import func
        counts = db.session.query(
            Task.status, func.count(Task.id)
        ).group_by(Task.status).all()
        by_status = {s: c for s, c in counts}

        total = sum(by_status.values())
        done = by_status.get('done', 0)

        overdue_count = sum(
            1 for t in Task.query.filter(
                Task.due_date.isnot(None),
                Task.status.notin_(['done', 'cancelled'])
            ).all()
            if t.is_overdue()
        )

        return {
            'total': total,
            'pending': by_status.get('pending', 0),
            'in_progress': by_status.get('in_progress', 0),
            'done': done,
            'cancelled': by_status.get('cancelled', 0),
            'overdue': overdue_count,
            'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
        }
