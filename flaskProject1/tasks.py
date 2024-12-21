import os
import smtplib
from email.mime.text import MIMEText
from celery import Celery

app = Celery('tasks', broker=f'pyamqp://guest@{os.environ.get("RABBIT_HOST", "localhost")}/')

@app.task
def add(a, b):
    return a+b

@app.task
def send_email(contract_number):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = 'mykyta.glushko@gmail.com'
    to_email = 'mykyta.glushko@gmail.com'
    sender_password = ""

    msg = MIMEText('text about contract', 'plain')
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = f'contact {contract_number} signed'

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, to_email, msg.as_string())
    server.quit()

    return f"Email sent"

