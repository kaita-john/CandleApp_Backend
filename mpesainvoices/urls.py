# urls.py

from django.urls import path

from .views import *

urlpatterns = [
    path('create', MpesaInvoiceCreateView.as_view(), name="MpesaInvoice-create"),
    path('list', MpesaInvoiceListView.as_view(), name="MpesaInvoice-list"),
    path('deleteall', MpesaInvoiceDeleteAllObjects.as_view(), name="MpesaInvoice-deleteall"),
    path('<str:pk>', MpesaInvoiceDetailView.as_view(), name="MpesaInvoice-detail")
]
