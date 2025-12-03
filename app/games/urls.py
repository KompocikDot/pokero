from django.urls import path

from games.views import GameCreateView, GameDeleteView, GameUpdateView

urlpatterns = [
    path('create/', GameCreateView.as_view(), name="game_create_view"),
    path('<int:game_pk>/update/', GameUpdateView.as_view(), name="game_update_view"),
    path('<int:game_pk>/delete/', GameDeleteView.as_view(), name="game_delete_view"),
]
