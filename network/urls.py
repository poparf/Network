
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createpost", views.createpost, name="createpost"),
    path("profile/<str:username>", views.userprofile, name="userprofile"),
    path("follow", views.follow, name="follow"),
    path("unfollow", views.unfollow, name="unfollow"),
    path("following", views.following, name="following"),
    path("edit/<str:postid>", views.editpost, name="editpost"),

    # API ROUTES
    path("postinfo/<str:postid>", views.postinfo, name="postinfo"),
    path('toggle-like/<str:postid>', views.toggle_like_view, name='toggle-like'),
]
