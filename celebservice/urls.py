# urls.py

from django.urls import path

from .views import *

urlpatterns = [
    path('create', CelebServiceCreateView.as_view(), name="celebservice-create"),
    path('apicreate', CelebServiceUpdateOrCreate.as_view(), name="celebservice-create"),
    path('list', CelebServiceListView.as_view(), name="celebservice-list"),
    path('deleteall', CelebServiceDeleteAllObjects.as_view(), name="celebservice-deleteall"),
    path('<str:pk>', CelebServiceDetailView.as_view(), name="celebservice-detail")
]
