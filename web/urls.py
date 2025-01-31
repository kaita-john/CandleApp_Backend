from django.urls import path

import web.views as webviews

urlpatterns = [
    path('homepage/', webviews.homepage_view, name='homepage'),
    path('terms/', webviews.terms_view, name='terms'),
    path('users/', webviews.users_view, name='userspage'),
    path('delete_user/<path:user_id>/', webviews.delete_user, name='delete_user'),
    path('deactivate_user/<path:user_id>/', webviews.deactivate_user, name='deactivate_user'),
    path('approve_celeb/<path:user_id>/', webviews.approve_celeb, name='approve_celeb'),  # Add this line
    path('mark_paid/<path:request_id>/', webviews.mark_paid, name='mark_paid'),
    path("requests/refund/<path:request_id>/", webviews.refund_request, name="refund_request"),
    path("logout/", webviews.custom_logout_view, name="logout"),
    path('requests/', webviews.requests_view, name='requestspage'),
    path('', webviews.login_view, name='loginpage'),
]
