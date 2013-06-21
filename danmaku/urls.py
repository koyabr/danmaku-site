from django.conf.urls import patterns, include, url


from django.contrib import admin
admin.autodiscover()

'''
@author: koyabr
@contact: koyabr@gmail.com

'''



urlpatterns = patterns('',

    url(r'^$', 'danmaku.views.home', name='home'),

    # user session

    url(r'^register/$', 'danmaku.views.register', name='register'),

    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name=

'login'),

    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name=

'logout'),

    # user management
    url(r'^manage/posts$', 'danmaku.views.manage_posts', name='manage_posts'),

    url(r'^manage/people$', 'danmaku.views.manage_people', name='manage_people'),

    # post

    url(r'^post/publish/$', 'danmaku.views.publish', name='publish'),

    url(r'^post/(?P<post_id>\d+)/$', 'danmaku.views.post', name='post'),

    url(r'^post/(?P<post_id>\d+)/edit/$', 'danmaku.views.edit', name='edit'),

    # reserved for flash player
    url(r'^post/(?P<post_id>\d+)/danmaku/(?P<vid>\d+)/?$', 'danmaku.views.danmaku', name='danmaku'),




    # admin
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/', include(admin.site.urls)),

    # ajax
    url(r'^ajax/user/$', 'danmaku.ajax.user', name='ajax_user'),
    url(r'^ajax/posts/$', 'danmaku.ajax.posts', name='ajax_posts'),
    url(r'^ajax/people/$', 'danmaku.ajax.people', name='ajax_people'),
    url(r'^ajax/profile/$', 'danmaku.ajax.profile', name='ajax_profile'),

    url(r'^ajax/follow/$', 'danmaku.ajax.follow', name='ajax_follow'),
    url(r'^ajax/watcher/$', 'danmaku.ajax.watcher', name='ajax_watcher'),
    url(r'^ajax/like/$', 'danmaku.ajax.like', name='ajax_like'),
    url(r'^ajax/favorite/$', 'danmaku.ajax.favorite', name='ajax_favorite'),
    # search
    url(r'^ajax/search/$', 'danmaku.ajax.search', name='ajax_search'),



)
