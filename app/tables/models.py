from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Table(models.Model):
    name = models.CharField(max_length=255)
    dealer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='dealing_tables',
    )

    play_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} | {self.play_date}"

    def get_absolute_url(self):
        return reverse('table_object_view', kwargs={"pk": self.pk})
