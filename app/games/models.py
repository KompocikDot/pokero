from django.db import models

from django.contrib.auth.models import User
from tables.models import Table
import rules
from rules.contrib.models import RulesModel


@rules.predicate
def is_game_table_dealer(user, game):
    return user == game.table.dealer

@rules.predicate
def is_table_dealer(user, table):
    return user == table.dealer

class Game(RulesModel):
    class Meta:
        rules_permissions = {
            "change": is_game_table_dealer,
            "delete": is_game_table_dealer,
        }

    table = models.ForeignKey(
        Table,
        on_delete=models.CASCADE,
        related_name='games',
    )
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="won_games")
    players = models.ManyToManyField(User, related_name="games")

