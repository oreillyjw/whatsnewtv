from django.urls import path, re_path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("account", views.account_index, name="account"),
    path("search", views.search, name="search"),
    path("favorite", views.favorite, name="favorite"),
    path("followers", views.get_followers, name="followers"),
    path("notifications", views.get_notifications, name="notifications"),
    path("notifications-count", views.get_notifications_count, name="notifications-count"),
    re_path(r'^(?P<type>movie|tv)/(?P<id>\d+)/?$', views.details, name="details"),
]
