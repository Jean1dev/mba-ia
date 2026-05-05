from flask import Blueprint, request, jsonify
from database import db
from models.task import Task
from models.user import User
from models.category import Category
from datetime import datetime
import json, os, sys, time

task_bp = Blueprint('tasks', __name__)

@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    try:
        tasks = Task.query.all()
        result = []
        for t in tasks:
            task_data = {}
            task_data['id'] = t.id
            task_data['title'] = t.title
            task_data['description'] = t.description
            task_data['status'] = t.status
            task_data['priority'] = t.priority
            task_data['user_id'] = t.user_id
            task_data['category_id'] = t.category_id
            task_data['created_at'] = str(t.created_at)
            task_data['updated_at'] = str(t.updated_at)
            task_data['due_date'] = str(t.due_date) if t.due_date else None
            task_data['tags'] = t.tags.split(',') if t.tags else []

            if t.due_date:
                if t.due_date < datetime.utcnow():
                    if t.status != 'done' and t.status != 'cancelled':
                        task_data['overdue'] = True
                    else:
                        task_data['overdue'] = False
                else:
                    task_data['overdue'] = False
            else:
                task_data['overdue'] = False

            if t.user_id:
                user = User.query.get(t.user_id)
                if user:
                    task_data['user_name'] = user.name
                else:
                    task_data['user_name'] = None
            else:
                task_data['user_name'] = None

            if t.category_id:
                cat = Category.query.get(t.category_id)
                if cat:
                    task_data['category_name'] = cat.name
                else:
                    task_data['category_name'] = None
            else:
                task_data['category_name'] = None

            result.append(task_data)

        return jsonify(result), 200
    except:
        return jsonify({'error': 'Erro interno'}), 500

@task_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = Task.query.get(task_id)
    if task:
        data = task.to_dict()

        if task.due_date:
            if task.due_date < datetime.utcnow():
                if task.status != 'done' and task.status != 'cancelled':
                    data['overdue'] = True
                else:
                    data['overdue'] = False
            else:
                data['overdue'] = False
        else:
            data['overdue'] = False
        return jsonify(data), 200
    else:
        return jsonify({'error': 'Task não encontrada'}), 404

@task_bp.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400

    title = data.get('title')
    if not title:
        return jsonify({'error': 'Título é obrigatório'}), 400

    if len(title) < 3:
        return jsonify({'error': 'Título muito curto'}), 400

    if len(title) > 200:
        return jsonify({'error': 'Título muito longo'}), 400

    description = data.get('description', '')
    status = data.get('status', 'pending')
    priority = data.get('priority', 3)
    user_id = data.get('user_id')
    category_id = data.get('category_id')
    due_date = data.get('due_date')
    tags = data.get('tags')

    if status not in ['pending', 'in_progress', 'done', 'cancelled']:
        return jsonify({'error': 'Status inválido'}), 400

    if priority < 1 or priority > 5:
        return jsonify({'error': 'Prioridade deve ser entre 1 e 5'}), 400

    if user_id:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404

    if category_id:
        cat = Category.query.get(category_id)
        if not cat:
            return jsonify({'error': 'Categoria não encontrada'}), 404

    task = Task()
    task.title = title
    task.description = description
    task.status = status
    task.priority = priority
    task.user_id = user_id
    task.category_id = category_id

    if due_date:
        try:
            task.due_date = datetime.strptime(due_date, '%Y-%m-%d')
        except:
            return jsonify({'error': 'Formato de data inválido. Use YYYY-MM-DD'}), 400

    if tags:
        if type(tags) == list:
            task.tags = ','.join(tags)
        else:
            task.tags = tags

    try:
        db.session.add(task)
        db.session.commit()
        print(f"Task criada: {task.id} - {task.title}")
        return jsonify(task.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao criar task: {str(e)}")
        return jsonify({'error': 'Erro ao criar task'}), 500

@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({'error': 'Task não encontrada'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400

    if 'title' in data:
        if len(data['title']) < 3:
            return jsonify({'error': 'Título muito curto'}), 400
        if len(data['title']) > 200:
            return jsonify({'error': 'Título muito longo'}), 400
        task.title = data['title']

    if 'description' in data:
        task.description = data['description']

    if 'status' in data:
        if data['status'] not in ['pending', 'in_progress', 'done', 'cancelled']:
            return jsonify({'error': 'Status inválido'}), 400
        task.status = data['status']

    if 'priority' in data:
        if data['priority'] < 1 or data['priority'] > 5:
            return jsonify({'error': 'Prioridade deve ser entre 1 e 5'}), 400
        task.priority = data['priority']

    if 'user_id' in data:
        if data['user_id']:
            user = User.query.get(data['user_id'])
            if not user:
                return jsonify({'error': 'Usuário não encontrado'}), 404
        task.user_id = data['user_id']

    if 'category_id' in data:
        if data['category_id']:
            cat = Category.query.get(data['category_id'])
            if not cat:
                return jsonify({'error': 'Categoria não encontrada'}), 404
        task.category_id = data['category_id']

    if 'due_date' in data:
        if data['due_date']:
            try:
                task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
            except:
                return jsonify({'error': 'Formato de data inválido'}), 400
        else:
            task.due_date = None

    if 'tags' in data:
        if type(data['tags']) == list:
            task.tags = ','.join(data['tags'])
        else:
            task.tags = data['tags']

    task.updated_at = datetime.utcnow()

    try:
        db.session.commit()
        print(f"Task atualizada: {task.id}")
        return jsonify(task.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao atualizar'}), 500

@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({'error': 'Task não encontrada'}), 404

    try:
        db.session.delete(task)
        db.session.commit()
        print(f"Task deletada: {task_id}")
        return jsonify({'message': 'Task deletada com sucesso'}), 200
    except:
        db.session.rollback()
        return jsonify({'error': 'Erro ao deletar'}), 500

@task_bp.route('/tasks/search', methods=['GET'])
def search_tasks():
    query = request.args.get('q', '')
    status = request.args.get('status', '')
    priority = request.args.get('priority', '')
    user_id = request.args.get('user_id', '')

    tasks = Task.query

    if query:
        tasks = tasks.filter(
            db.or_(
                Task.title.like(f'%{query}%'),
                Task.description.like(f'%{query}%')
            )
        )

    if status:
        tasks = tasks.filter(Task.status == status)

    if priority:
        tasks = tasks.filter(Task.priority == int(priority))

    if user_id:
        tasks = tasks.filter(Task.user_id == int(user_id))

    results = tasks.all()
    output = []
    for t in results:
        output.append(t.to_dict())

    return jsonify(output), 200

@task_bp.route('/tasks/stats', methods=['GET'])
def task_stats():
    total = Task.query.count()
    pending = Task.query.filter_by(status='pending').count()
    in_progress = Task.query.filter_by(status='in_progress').count()
    done = Task.query.filter_by(status='done').count()
    cancelled = Task.query.filter_by(status='cancelled').count()

    all_tasks = Task.query.all()
    overdue_count = 0
    for t in all_tasks:
        if t.due_date:
            if t.due_date < datetime.utcnow():
                if t.status != 'done' and t.status != 'cancelled':
                    overdue_count = overdue_count + 1

    stats = {
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'done': done,
        'cancelled': cancelled,
        'overdue': overdue_count,
        'completion_rate': round((done / total) * 100, 2) if total > 0 else 0
    }

    return jsonify(stats), 200
