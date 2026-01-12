from django.db import models

from ..tables.models import Table

class Comment(models.Model):
    comment = models.TextField()
    creator = models.ForeignKey(Table, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
