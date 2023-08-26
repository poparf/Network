from django.contrib import admin
from .models import User, UserFollowing, UserPost, PostLike

# Register your models here.
admin.site.register(User)
admin.site.register(UserFollowing)
admin.site.register(UserPost)
admin.site.register(PostLike)