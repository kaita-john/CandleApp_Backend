# urls.py

from django.urls import path

from .views import ServiceListView, ServiceDetailView, ServiceCreateView, CurrentServiceView

urlpatterns = [
    path('create', ServiceCreateView.as_view(), name="term-create"),
    path('list', ServiceListView.as_view(), name="term-list"),
    path('current', CurrentServiceView.as_view(), name="current-term"),
    path('<str:pk>', ServiceDetailView.as_view(), name="term-detail")
]
