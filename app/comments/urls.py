from django.urls import path
from .views import CommentCreateView, CommentDeleteView, CommentUpdateView


urlpatterns = [
    path('create/', CommentCreateView.as_view(), name="comment_create_view"),
    path('<int:comment_pk>/delete/', CommentDeleteView.as_view(), name="comment_delete_view"),
    path('<int:comment_pk>/update/', CommentUpdateView.as_view(), name="comment_update_view"),
]
