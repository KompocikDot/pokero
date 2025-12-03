from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, UpdateView

from tables.models import Table
from django.shortcuts import get_object_or_404

from .models import Game

class GameCreateView(CreateView):
    model = Game
    fields = ["players", "winner"]
    template_name_suffix = "_create_form"
    success_url = reverse_lazy('tables_list_view')
    pk_url_kwarg = "game_pk"

    def form_valid(self, form):
        table_pk = self.kwargs['pk']
        
        table = get_object_or_404(Table, pk=table_pk)
        form.instance.table = table

        return super().form_valid(form)

class GameUpdateView(UpdateView):
    model = Game
    fields = ["players", "winner"]
    template_name_suffix = "_update_form"
    pk_url_kwarg = "game_pk"

    def get_success_url(self):
        # pk in that case is a Game.table.pk
        return reverse_lazy('table_object_view', kwargs={"pk": self.kwargs["pk"]})

class GameDeleteView(DeleteView):
    model = Game
    pk_url_kwarg = "game_pk"
    
    def get_success_url(self) -> str:
        # pk in that case is a Game.table.pk
        return reverse_lazy('table_object_view', kwargs={"pk": self.kwargs["pk"]})
