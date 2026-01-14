from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
import rules
from rules.contrib.models import RulesModel

@rules.predicate
def is_table_dealer(user, table):
    return user == table.dealer or user == table.creator

@rules.predicate
def is_table_dealer_or_game_player(user, table):
    return user == table.dealer or user == table.creator or table.games.filter(players__pk=user.pk).exists()

class Table(RulesModel):
    class Meta:
        rules_permissions = {
            "read": is_table_dealer_or_game_player,
            "change": is_table_dealer,
            "delete": is_table_dealer,
        }

    name = models.CharField(max_length=255)
    dealer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='dealing_tables',
    )
    
    creator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
    )

    play_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} | {self.play_date}"

    def get_absolute_url(self):
        return reverse('table_object_view', kwargs={"pk": self.pk})
