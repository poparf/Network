from django.forms import ModelForm
from .models import UserPost, Comment

class UserPostForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].widget.attrs['class'] = "form-control mb-2"
        self.fields['content'].label = "New post"

    class Meta:
        model = UserPost
        fields = ["content"]