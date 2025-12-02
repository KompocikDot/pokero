from django.db import models

from django.contrib.auth.models import User
from tables.models import Table

class Game(models.Model):
    table = models.ForeignKey(
        Table,
        on_delete=models.CASCADE,
        related_name='games',
    )
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="won_games")
    players = models.ManyToManyField(User, related_name="games")

