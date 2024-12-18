import smtplib

from celery import Celery

app = Celery('hello', broker='amqp://guest@localhost//')

@app.task
def add(a, b):
    return a+b

def send_email():
    from email.message import EmailMessage

    msg = EmailMessage()
    msg.set_content('Hello World')

    msg['Subject'] = f'New contract'
    msg['From'] = '<EMAIL>'
    msg['To'] = '<EMAIL>'

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.send_message(msg)
    s.quit()

