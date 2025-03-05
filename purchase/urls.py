# urls.py

from django.urls import path

from .views import *

urlpatterns = [
    path('create', PurchaseCreateView.as_view(), name="purchase-create"),
    path('list', PurchaseListView.as_view(), name="purchase-list"),
    path('deleteall', PurchaseDeleteAllObjects.as_view(), name="purchase-deleteall"),
    path('<str:pk>', PurchaseDetailView.as_view(), name="purchase-detail")
]