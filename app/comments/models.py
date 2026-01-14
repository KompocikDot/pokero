from django.contrib.auth.forms import User
from django.db import models
import rules
from rules.contrib.models import RulesModel


from tables.models import Table

@rules.predicate
def is_comment_creator(user, comment):
    return user == comment.creator

class Comment(RulesModel):
    class Meta:
        rules_permissions = {
            "change": is_comment_creator,
            "delete": is_comment_creator,
        }

    comment = models.TextField()
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name="comments")
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now=True)


