# urls.py

from django.urls import path

from .views import *

urlpatterns = [
    path('create', PurchaseItemCreateView.as_view(), name="purchaseitem-create"),
    path('list', PurchaseItemListView.as_view(), name="purchaseitem-list"),
    path('deleteall', PurchaseItemDeleteAllObjects.as_view(), name="purchaseitem-deleteall"),
    path('<str:pk>', PurchaseItemDetailView.as_view(), name="purchaseitem-detail")
]
