from django.contrib.auth.models import User
from django.db import models

from app.games.models import Game

class Table(models.Model):
    name = models.CharField(max_length=255)
    croupier = models.OneToOneField(User, on_delete=models.DO_NOTHING)
    games = models.ForeignKey(Game, on_delete=models.DO_NOTHING)
    play_date = models.DateTimeField(auto_now_add=True)

