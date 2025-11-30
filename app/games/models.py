from django.db import models

from django.contrib.auth.models import User

# Create your models here.

class Game(models.Model):
    winner = models.OneToOneField(User, on_delete=models.SET_NULL)

