# urls.py

from django.urls import path

from .views import *

urlpatterns = [
    path('create', ItemCreateView.as_view(), name="item-create"),
    path('list', ItemListView.as_view(), name="item-list"),
    path('deleteall', ItemDeleteAllObjects.as_view(), name="item-deleteall"),
    path('<str:pk>', ItemDetailView.as_view(), name="item-detail")
]
