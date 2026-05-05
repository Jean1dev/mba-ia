from datetime import datetime
import re
import os
import json
import sys
import math
import hashlib

def format_date(date_obj):
    if date_obj:
        return str(date_obj)
    return None

def calculate_percentage(part, total):
    if total == 0:
        return 0
    return round((part / total) * 100, 2)

def validate_email(email):

    if re.match(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$', email):
        return True
    return False

def sanitize_string(s):

    if s:
        return s.strip()
    return s

def generate_id():

    import uuid
    return str(uuid.uuid4())

def log_action(action, details=None):

    timestamp = datetime.utcnow()
    print(f"[{timestamp}] ACTION: {action}")
    if details:
        print(f"  DETAILS: {details}")

def parse_date(date_string):
    try:
        return datetime.strptime(date_string, '%Y-%m-%d')
    except:
        try:
            return datetime.strptime(date_string, '%d/%m/%Y')
        except:
            return None

def is_valid_color(color):
    if color and len(color) == 7 and color[0] == '#':
        return True
    return False

def process_task_data(data, existing_task=None):
    result = {}

    if 'title' in data:
        title = data['title']
        if title:
            title = title.strip()
            if len(title) >= 3 and len(title) <= 200:
                result['title'] = title
            else:
                return None, 'Título deve ter entre 3 e 200 caracteres'
        else:
            return None, 'Título não pode ser vazio'

    if 'description' in data:
        result['description'] = data['description']

    if 'status' in data:
        valid_statuses = ['pending', 'in_progress', 'done', 'cancelled']
        if data['status'] in valid_statuses:
            result['status'] = data['status']
        else:
            return None, 'Status inválido'

    if 'priority' in data:
        try:
            p = int(data['priority'])
            if p >= 1 and p <= 5:
                result['priority'] = p
            else:
                return None, 'Prioridade deve ser entre 1 e 5'
        except:
            return None, 'Prioridade inválida'

    if 'due_date' in data:
        if data['due_date']:
            parsed = parse_date(data['due_date'])
            if parsed:
                result['due_date'] = parsed
            else:
                return None, 'Data inválida'
        else:
            result['due_date'] = None

    if 'tags' in data:
        tags = data['tags']
        if type(tags) == list:
            result['tags'] = ','.join(tags)
        else:
            result['tags'] = tags

    return result, None

VALID_STATUSES = ['pending', 'in_progress', 'done', 'cancelled']
VALID_ROLES = ['user', 'admin', 'manager']
MAX_TITLE_LENGTH = 200
MIN_TITLE_LENGTH = 3
MIN_PASSWORD_LENGTH = 4
DEFAULT_PRIORITY = 3
DEFAULT_COLOR = '#000000'
