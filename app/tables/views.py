from django.urls import reverse_lazy
from django.views.generic import DeleteView, ListView, DetailView, CreateView, UpdateView
from .models import Table
from django.contrib.auth.mixins import LoginRequiredMixin

class TablesListView(LoginRequiredMixin, ListView):
    model = Table

class TableObjectView(LoginRequiredMixin, DetailView):
    model = Table

class TablesCreateView(LoginRequiredMixin, CreateView):
    model = Table
    fields = "__all__"
    template_name_suffix = "_create_form"

class TableDeleteView(LoginRequiredMixin, DeleteView):
    model = Table
    success_url = reverse_lazy('tables_list_view')

class TableUpdateView(LoginRequiredMixin, UpdateView):
    model = Table
    fields = "__all__"
    template_name_suffix = "_update_form"

