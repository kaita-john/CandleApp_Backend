# urls.py

from django.urls import path

from .views import *


urlpatterns = [
    path('create', ItemCreateView.as_view(), name="item-create"),
    path('list', ItemListView.as_view(), name="item-list"),
    path('deleteall', ItemDeleteAllObjects.as_view(), name="item-deleteall"),
    path('out/<int:id>', OutOfStockView.as_view(), name='mark_out_of_stock'),
    path('restock/<int:id>', RestockView.as_view(), name='restock'),
    path('notify-out-of-stock', NotifyOutOfStockView.as_view(), name="item-detail"),
    path('<str:pk>', ItemDetailView.as_view(), name="item-detail")

]
