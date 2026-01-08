from django.urls import reverse_lazy
from django.views.generic import DeleteView, ListView, DetailView, CreateView, UpdateView
from .models import Table
from django.contrib.auth.mixins import LoginRequiredMixin
from rules.contrib.views import PermissionRequiredMixin

class TablesListView(LoginRequiredMixin, ListView):
    model = Table

class TableObjectView(LoginRequiredMixin, DetailView):
    model = Table

class TablesCreateView(LoginRequiredMixin, CreateView):
    model = Table
    fields = "__all__"
    template_name_suffix = "_create_form"

class TableDeleteView(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Table
    success_url = reverse_lazy('tables_list_view')
    permission_required = "tables.delete_table"

class TableUpdateView(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Table
    fields = "__all__"
    template_name_suffix = "_update_form"
    permission_required = "tables.change_table"

