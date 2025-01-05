# urls.py

from django.urls import path

from .views import *

urlpatterns = [
    path('create', RequestCreateView.as_view(), name="request-create"),
    path('list', RequestListView.as_view(), name="request-list"),
    path('customer-requests', CustomerRequestsView.as_view(), name="request-list"),
    path('withdraw/<str:pk>', CustomerWithdraw.as_view(), name="withdraw-list"),
    path('current', CurrentRequestView.as_view(), name="current-request"),
    path('flow/checkStatus', CheckRequestStatus.as_view(), name="request-list"),
    path('flow', RequestFlowView.as_view(), name="request-list"),
    path('<str:pk>', RequestDetailView.as_view(), name="request-detail")
]

