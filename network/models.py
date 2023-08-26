from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass


class UserPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.CharField(max_length=512)
    likes = models.IntegerField(default=0)


    def serialize(self):
        return {
            "id": self.id,
            "user": self.user.username,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "content": self.content,
            "likes":self.likes
        }

    def __str__(self):
        return f'{self.user.username} posted at {self.timestamp} with the description: {self.content}'

class PostLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(UserPost, on_delete=models.CASCADE)

    def serialize(self):
        return {
            'user': self.user.username,
            'post': self.post.id
        }
    def __str__(self):
        return f'{self.user.username} likes post {self.post.id}'


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(UserPost, on_delete=models.CASCADE, related_name='comments')
    content = models.CharField(max_length=512)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} commented on {self.post.user.username}\'s post at {self.timestamp}'
    

class UserFollowing(models.Model):
    user_id = models.ForeignKey(User, related_name="following", on_delete=models.CASCADE)
    following_user_id = models.ForeignKey(User, related_name="followers", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user_id} follows {self.following_user_id}"

    class Meta:
        unique_together = ('user_id', 'following_user_id',)