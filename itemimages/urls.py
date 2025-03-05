# urls.py

from django.urls import path

from .views import *

urlpatterns = [
    path('create', ItemImageCreateView.as_view(), name="itemimage-create"),
    path('list', ItemImageListView.as_view(), name="itemimage-list"),
    path('deleteall', ItemImageDeleteAllObjects.as_view(), name="itemimage-deleteall"),
    path('<str:pk>', ItemImageDetailView.as_view(), name="itemimage-detail")
]
