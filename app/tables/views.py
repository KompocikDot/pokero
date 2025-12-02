from django.views.generic import ListView, DetailView, CreateView
from .models import Table

class TablesListView(ListView):
    model = Table

class TableObjectView(DetailView):
    model = Table

class TablesCreateView(CreateView):
    model = Table
    fields = "__all__"

