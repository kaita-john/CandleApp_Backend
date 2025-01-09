from django.urls import path

import web.views as webviews

urlpatterns = [
    path('', webviews.login_view, name='loginpage'),
    path('homepage/', webviews.homepage_view, name='homepage'),
    path('users/', webviews.users_view, name='userspage'),
    path('requests/', webviews.requests_view, name='requestspage'),
]
