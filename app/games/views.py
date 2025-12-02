from django.urls import reverse_lazy
from django.views.generic import CreateView

from tables.models import Table
from django.shortcuts import get_object_or_404

from .models import Game

class GameCreateView(CreateView):
    model = Game
    fields = ["players", "winner"]
    template_name_suffix = "_create_form"
    success_url = reverse_lazy('tables_list_view')

    def form_valid(self, form):
        table_pk = self.kwargs['pk']
        
        table = get_object_or_404(Table, pk=table_pk)
        form.instance.table = table

        return super().form_valid(form)
