from django.db import models
from django.contrib.auth.models import User

'''
@author: koyabr
@contact: koyabr@gmail.com

'''


POST_CATEGORIES = (
    ('t', 'TV'),
    ('g', 'Game'),
    ('c', 'Cartoon'),
    ('s', 'Course'),
)


class Post(models.Model):
    '''
    A post must contain a video and a thumbnail, then some optional text note.
    '''
    date = models.DateTimeField(auto_now_add=True, db_index=True)
    author = models.ForeignKey(User)

    title = models.CharField(max_length=255)
    category = models.CharField(max_length=1, choices=POST_CATEGORIES)
    vid = models.CharField(max_length=20, help_text="video ID (sina video)")
    img = models.URLField(help_text="url of the thumbnail")
    text = models.TextField(blank=True, help_text="Notes for the video")

    # statistic info
    play_num = models.IntegerField(default=0)


    def __unicode__(self):
        return self.title

class UserInfo(models.Model):
    '''
    Establish One-to-One relationship with auth.models.User,
    also record the email_hash, and all Many-to-Many relationships between user and post.
    '''
    user = models.OneToOneField(User, primary_key=True, related_name='userinfo')
    hash = models.CharField(max_length=255) # for Gravatar service

    follow = models.ManyToManyField(User, related_name='follow')

    favorite = models.ManyToManyField(Post, related_name='favorite')
    like = models.ManyToManyField(Post, related_name='like')
    watch = models.ManyToManyField(Post, related_name='watch') # Current watching post



class Danmaku(models.Model):
    '''
    Store information for a danmaku comment
    '''
    text = models.TextField()
    post = models.ForeignKey(Post)
    date = models.DateTimeField(auto_now_add=True)

    mode = models.IntegerField(default=1) # Plain-text / Scripted
    time = models.FloatField() # The video time when this danmaku is posted
    color = models.IntegerField(default=0xFFFFFF) # Text color
    size = models.IntegerField(default=25) # Font size



