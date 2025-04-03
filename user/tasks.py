# user/tasks.py
from celery import shared_task

@shared_task
def send_welcome_email(user_email):
    # Your logic to send a welcome email
    print(f'Sending welcome email to {user_email}')
