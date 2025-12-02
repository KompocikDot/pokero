from django.urls import path
from .views import TableObjectView, TablesCreateView, TablesListView

urlpatterns = [
    path('', TablesListView.as_view(), name="tables_list_view"),
    path('<int:pk>/', TableObjectView.as_view(), name="table_object_view"),
    path('create/', TablesCreateView.as_view(), name="table_create_view"),
]
