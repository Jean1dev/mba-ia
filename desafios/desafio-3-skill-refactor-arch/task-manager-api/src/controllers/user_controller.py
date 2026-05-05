import re
from database import db
from src.models.user import User
from src.models.task import Task
from src.config.settings import VALID_ROLES
from sqlalchemy.orm import joinedload


class UserController:
    _EMAIL_RE = re.compile(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$')

    def get_all(self):
        users = User.query.options(joinedload(User.tasks)).all()
        result = []
        for u in users:
            data = u.to_dict()
            data['task_count'] = len(u.tasks)
            result.append(data)
        return result

    def get_by_id(self, user_id):
        user = User.query.options(joinedload(User.tasks)).filter_by(id=user_id).first()
        if not user:
            raise LookupError('Usuário não encontrado')
        data = user.to_dict()
        data['tasks'] = [t.to_dict() for t in user.tasks]
        return data

    def create(self, data):
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        role = data.get('role', 'user')

        if not name:
            raise ValueError('Nome é obrigatório')
        if not email:
            raise ValueError('Email é obrigatório')
        if not password:
            raise ValueError('Senha é obrigatória')
        if not self._EMAIL_RE.match(email):
            raise ValueError('Email inválido')
        if len(password) < 4:
            raise ValueError('Senha deve ter no mínimo 4 caracteres')
        if role not in VALID_ROLES:
            raise ValueError('Role inválido')

        if User.query.filter_by(email=email).first():
            raise ValueError('Email já cadastrado')

        user = User(name=name, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user.to_dict()

    def update(self, user_id, data):
        user = User.query.get(user_id)
        if not user:
            raise LookupError('Usuário não encontrado')

        if 'name' in data:
            user.name = data['name']

        if 'email' in data:
            if not self._EMAIL_RE.match(data['email']):
                raise ValueError('Email inválido')
            existing = User.query.filter_by(email=data['email']).first()
            if existing and existing.id != user_id:
                raise ValueError('Email já cadastrado')
            user.email = data['email']

        if 'password' in data:
            if len(data['password']) < 4:
                raise ValueError('Senha muito curta')
            user.set_password(data['password'])

        if 'role' in data:
            if data['role'] not in VALID_ROLES:
                raise ValueError('Role inválido')
            user.role = data['role']

        if 'active' in data:
            user.active = data['active']

        db.session.commit()
        return user.to_dict()

    def delete(self, user_id):
        user = User.query.get(user_id)
        if not user:
            raise LookupError('Usuário não encontrado')
        Task.query.filter_by(user_id=user_id).delete()
        db.session.delete(user)
        db.session.commit()

    def get_tasks(self, user_id):
        user = User.query.get(user_id)
        if not user:
            raise LookupError('Usuário não encontrado')
        tasks = Task.query.filter_by(user_id=user_id).all()
        return [t.to_dict() for t in tasks]

    def login(self, email, password):
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            raise PermissionError('Credenciais inválidas')
        if not user.active:
            raise PermissionError('Usuário inativo')
        return {
            'message': 'Login realizado com sucesso',
            'user': user.to_dict(),
            'token': f'fake-jwt-token-{user.id}',
        }
