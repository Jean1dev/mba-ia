import smtplib
import logging
from datetime import datetime
from src.config.settings import Config

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, config=None):
        cfg = config or Config
        self.email_host = cfg.SMTP_HOST
        self.email_port = cfg.SMTP_PORT
        self.email_user = cfg.SMTP_USER
        self.email_password = cfg.SMTP_PASSWORD
        self._log: list[dict] = []

    def send_email(self, to: str, subject: str, body: str) -> bool:
        try:
            server = smtplib.SMTP(self.email_host, self.email_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            server.sendmail(self.email_user, to, f'Subject: {subject}\n\n{body}')
            server.quit()
            return True
        except Exception as exc:
            logger.warning('Email not sent to %s: %s', to, exc)
            return False

    def notify_task_assigned(self, user, task):
        subject = f'Nova task atribuída: {task.title}'
        body = (
            f'Olá {user.name},\n\n'
            f"A task '{task.title}' foi atribuída a você.\n\n"
            f'Prioridade: {task.priority}\nStatus: {task.status}'
        )
        self.send_email(user.email, subject, body)
        self._log.append({
            'type': 'task_assigned',
            'user_id': user.id,
            'task_id': task.id,
            'timestamp': datetime.utcnow(),
        })

    def notify_task_overdue(self, user, task):
        subject = f'Task atrasada: {task.title}'
        body = (
            f'Olá {user.name},\n\n'
            f"A task '{task.title}' está atrasada!\n\n"
            f'Data limite: {task.due_date}'
        )
        self.send_email(user.email, subject, body)

    def get_notifications(self, user_id: int) -> list[dict]:
        return [n for n in self._log if n['user_id'] == user_id]
