from django.contrib.auth.models import User
from django.db import models
from trainer.models import Service

# Create your models here.

class Booking(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer')
    trainer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trainer')
    datetime_start = models.DateTimeField()
    datetime_end = models.DateTimeField()
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
