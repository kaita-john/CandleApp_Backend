# urls.py

from django.urls import path

from .views import *

urlpatterns = [
    path('create', CategoryCreateView.as_view(), name="itemimage-create"),
    path('list', CategoryListView.as_view(), name="itemimage-list"),
    path('deleteall', CategoryDeleteAllObjects.as_view(), name="itemimage-deleteall"),
    path('<str:pk>', CategoryDetailView.as_view(), name="itemimage-detail")
]
