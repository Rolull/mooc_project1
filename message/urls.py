from django.urls import path
from .views import message_list, register
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("", message_list, name="home"),
    path("register/", register, name="register"),
    path("accounts/logout/", LogoutView.as_view(next_page='home'), name='logout'),
]