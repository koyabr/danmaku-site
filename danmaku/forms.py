from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from danmaku.models import Post, Comment


class MyUserCreationForm(UserCreationForm):

    username = forms.RegexField(label=_("Username"), max_length=30,
                                regex=ur'^[0-9A-Za-z\u4e00-\u9fa5]+$',
                                help_text=_("Required. 30 characters or fewer. Letters, digits and Hanzi only."),
                                error_messages={
                                    'invalid': _("This value may contain only letters, numbers and Hanzi.")})
    email = forms.EmailField(label=_("Email"), max_length=254,
                             help_text=_("Required. Avatar service is delivered by Gravatar."))


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
    class Meta:
        model = Post
        fields = ['title', 'category', 'text', 'vid', 'img']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']