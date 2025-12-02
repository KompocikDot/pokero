from django.urls import reverse_lazy
from django.views.generic import DeleteView, ListView, DetailView, CreateView, UpdateView
from .models import Table

class TablesListView(ListView):
    model = Table

class TableObjectView(DetailView):
    model = Table

class TablesCreateView(CreateView):
    model = Table
    fields = "__all__"

class TableDeleteView(DeleteView):
    model = Table
    success_url = reverse_lazy('tables_list_view')

class TableUpdateView(UpdateView):
    model = Table
    fields = "__all__"
    template_name_suffix = "_update"

