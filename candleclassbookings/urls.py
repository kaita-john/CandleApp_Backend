# urls.py

from django.urls import path

from .views import *

urlpatterns = [
    path('create', CandleClassBookingCreateView.as_view(), name="candleClassBooking-create"),
    path('list', CandleClassBookingListView.as_view(), name="candleClassBooking-list"),
    path('deleteall', CandleClassBookingDeleteAllObjects.as_view(), name="candleClassBooking-deleteall"),
    path('<str:pk>', CandleClassBookingDetailView.as_view(), name="candleClassBooking-detail")
]
