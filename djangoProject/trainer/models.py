from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class TrainerDescription(models.Model):
    name = models.TextField()
    trainer = models.ForeignKey(User, on_delete=models.CASCADE)

class TrainerSchedule(models.Model):
    datetime_start = models.DateTimeField()
    datetime_end = models.DateTimeField()
    trainer = models.ForeignKey(User, on_delete=models.CASCADE)

class Category(models.Model):
    name = models.CharField(max_length=50)

class Service(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    trainer = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    level = models.CharField(max_length=50)
    duration = models.CharField(max_length=50)



