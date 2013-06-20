from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

import re
from django.core.exceptions import ValidationError
# ---
# Custom Fields with Validation rules
# ---



# ---
# Models
# ---



POST_CATEGORIES = (
    ('t', 'TV'),
    ('m', 'Movie'),
    ('c', 'Cartoon'),
    ('s', 'Course'),
)


class Post(models.Model):
    date = models.DateTimeField(auto_now_add=True, db_index=True)
    author = models.ForeignKey(User)

    title = models.CharField(max_length=255)
    category = models.CharField(max_length=1, choices=POST_CATEGORIES)
    vid = models.CharField(max_length=20, help_text="video ID (sina video)")
    img = models.URLField(help_text="url of the thumbnail")
    text = models.TextField(blank=True, help_text="Notes for the video")

    # statistic info
    play_num = models.IntegerField(default=0)


    def get_absolute_url(self):
        return reverse('post', kwargs={"post_id": self.id})


    def __unicode__(self):
        return self.title

class UserInfo(models.Model):
    user = models.OneToOneField(User, primary_key=True, related_name='userinfo')
    hash = models.CharField(max_length=255)

    follow = models.ManyToManyField(User, related_name='follow')

    favorite = models.ManyToManyField(Post, related_name='favorite')
    like = models.ManyToManyField(Post, related_name='like')
    watch = models.ManyToManyField(Post, related_name='watch')


class Comment(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    body = models.TextField(verbose_name="My comment:")
    author = models.ForeignKey(User)
    post = models.ForeignKey(Post)


class Danmaku(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User)
    post = models.ForeignKey(Post)
    date = models.DateTimeField(auto_now_add=True)

    mode = models.IntegerField(default=1)
    time = models.FloatField()
    color = models.IntegerField(default=0xFFFFFF)
    size = models.IntegerField(default=25)



