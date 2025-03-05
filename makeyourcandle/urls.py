# urls.py

from django.urls import path

from .views import *

urlpatterns = [
    path('create', MakeYourCandleCreateView.as_view(), name="makeYourCandle-create"),
    path('list', MakeYourCandleListView.as_view(), name="makeYourCandle-list"),
    path('deleteall', MakeYourCandleDeleteAllObjects.as_view(), name="makeYourCandle-deleteall"),
    path('<str:pk>', MakeYourCandleDetailView.as_view(), name="makeYourCandle-detail")
]
