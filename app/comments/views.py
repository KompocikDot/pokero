from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DeleteView, ListView, CreateView, UpdateView

from .models import Comment

class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    template_name_suffix = "_create_form"

class CommentsListView(LoginRequiredMixin, ListView):
    model = Comment

class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment

class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    success_url = reverse_lazy('tables_list_view')
