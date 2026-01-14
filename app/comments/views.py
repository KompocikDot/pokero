from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import DeleteView, CreateView, UpdateView
from django.urls import reverse_lazy
from rules.contrib.views import PermissionRequiredMixin

from tables.models import Table

from .models import Comment

class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    template_name_suffix = "_create_form"
    fields = ["comment"]
    permission_required = "tables.read_table"
    pk_url_kwarg = "comment_pk"

    def form_valid(self, form):
        table_pk = self.kwargs['pk']
        
        table = get_object_or_404(Table, pk=table_pk)
        form.instance.table = table
        form.instance.creator = self.request.user

        return super().form_valid(form)

    def get_success_url(self):
        # pk in that case is a Comment.table.pk
        return reverse_lazy('table_object_view', kwargs={"pk": self.kwargs["pk"]})


class CommentUpdateView(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Comment
    fields = ["comment"]
    permission_required = "comments.change_comment"
    template_name_suffix = "_update_form"
    pk_url_kwarg = "comment_pk"

    def get_success_url(self):
        # pk in that case is a Game.table.pk
        return reverse_lazy('table_object_view', kwargs={"pk": self.kwargs["pk"]})

class CommentDeleteView(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Comment
    permission_required = "comments.delete_comment"
    pk_url_kwarg = "comment_pk"

    def get_success_url(self) -> str:
        # pk in that case is a Comment.table.pk
        return reverse_lazy('table_object_view', kwargs={"pk": self.kwargs["pk"]})
