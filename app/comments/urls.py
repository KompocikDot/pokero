from django.urls import path
from app.comments.views import CommentCreateView, CommentDeleteView, CommentUpdateView, CommentsListView


urlpatterns = [
    path('', CommentsListView.as_view(), name="comments_list_view"),
    path('create/', CommentCreateView.as_view(), name="comment_create_view"),
    path('<int:pk>/delete/', CommentDeleteView.as_view(), name="comment_delete_view"),
    path('<int:pk>/update/', CommentUpdateView.as_view(), name="comment_update_view"),
]
