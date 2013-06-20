Danmaku video
=============

1. Third-Party Packages
-----------------------

* django-apptemplates

    [https://pypi.python.org/pypi/django-apptemplates](https://pypi.python.org/pypi/django-apptemplates)

    `pip install django-apptemplates=0.0.1`
    
* django-disqus

    [https://pypi.python.org/pypi/django-disqus](https://pypi.python.org/pypi/django-disqus)

    `pip install django-disqus=0.4.1`
    

2. Current Features
-------------------


* Register & Login (currently using auth.models.User, need polishing)
* Publish a video (must login, only support sina videos, thumbnails cannot be uploaded)
* Watch videos & danmaku-comment! (fall back to Flash player, since html5 video tag is currently not supported well by video sites and browsers)

    >Note: to add a sina video, you should provide its vid instead of pure url. There are ways to find out the vid, I'll implement an automatic mechanism. For now I suggest you visit this one:
    >[http://you.video.sina.com.cn/c](http://you.video.sina.com.cn/c)
    >
    >You'll find video pages with url like http://video.sina.com.cn/v/b/57455040-1640601392.html, number before the dash is what we want. Return to my site, publish a video and type in 57455040, you are good to go.


3. Future plans:
---------------

* Customized User model to provider more services (SNS, chatting...)
* Support videos from qq.com & youku.com (I need some neat algorithms to get them work)
* Polishing the player (it's based on an open-source flex project, I'll distinguish my revision work from origin ones)
* Embellish all pages (Ah, CSS&JS is really a headache)
* Anything...
