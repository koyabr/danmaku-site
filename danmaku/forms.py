from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from danmaku.models import Post

'''
@author: koyabr
@contact: koyabr@gmail.com

'''


class MyUserCreationForm(UserCreationForm):
    '''
    Extend the UserCreationForm to add email field.
    '''


    email = forms.EmailField(label=_("Email"), max_length=254,
                             help_text=_("Required. Avatar service delivered by Gravatar; comment service powered by Disqus."))


    class Meta:
        model = User
        fields = ("username", "email",)


    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            User._default_manager.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(_('This email has been registered!'))


    def save(self, commit=True):
        user = super(MyUserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class PostForm(forms.ModelForm):
    '''
    ModelForm for a Post.
    '''
    class Meta:
        model = Post
        fields = ['title', 'category', 'vid', 'img', 'text']

