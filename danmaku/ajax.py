from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.db.models import Q

from danmaku.models import Post

import re
import json

'''
@author: koyabr
@contact: koyabr@gmail.com

'''


def split_list(origin_list, page_len=3):
    '''
    A toolkit method.
    Divide a long list into separate pages,
    very useful in multi-pages & carousel.

    @param origin_list: The list to be split
    @param page_len: How many items in a page

    @return: A list of pages
    '''

    page_list = []
    i = 0
    while i + page_len <= len(origin_list):
        page_list.append(origin_list[i:i + page_len])
        i += page_len

    if i < len(origin_list):
        page_list.append(origin_list[i:])

    return page_list


@login_required()
def user(request):
    '''
    Accept any request and return current user's info.
    Currently only yields the email_hash.

    @param request: Any types of http request

    @return: Currrent user's info in JSON format

    '''

    email_hash = ""
    if request.user.is_authenticated():
        email_hash = request.user.userinfo.hash

    user_json = {}
    user_json["email_hash"] = email_hash
    return HttpResponse(json.dumps(user_json))


@login_required()
@csrf_exempt
def follow(request):
    '''
    Add a user to / Remove a user from current user's follow list.
    A user cannot follow himself.

    @param request: A POST request with an user_id

    @return: The number of target user's followers in JSON format
    '''
    follow_json = {}
    if 'user_id' in request.POST:
        author = get_object_or_404(User, id=request.POST['user_id'])
        if author in request.user.userinfo.follow.all():
            request.user.userinfo.follow.remove(author)
        elif author != request.user:
            request.user.userinfo.follow.add(author)
        follow_json['follow_num'] = len(author.follow.all())

    return HttpResponse(json.dumps(follow_json))


@login_required()
@csrf_exempt
def like(request):
    '''
    Add a post to / Remove a post from current user's like list.

    @param request: A POST request with a post_id

    @return: How many users like the post, in JSON format
    '''
    like_json = {}
    if 'post_id' in request.POST:
        post = get_object_or_404(Post, id=request.POST['post_id'])
        if post in request.user.userinfo.like.all():
            request.user.userinfo.like.remove(post)
        else:
            request.user.userinfo.like.add(post)
        like_json['like_num'] = len(post.like.all())

    return HttpResponse(json.dumps(like_json))


@login_required()
@csrf_exempt
def favorite(request):
    '''
    Add a post to / Remove a post from current user's favorite list.

    @param request: A POST request with a post_id

    @return: How many users add the post to favorite, in JSON format
    '''
    fav_json = {}
    if 'post_id' in request.POST:
        post = get_object_or_404(Post, id=request.POST['post_id'])
        if post in request.user.userinfo.favorite.all():
            request.user.userinfo.favorite.remove(post)
        else:
            request.user.userinfo.favorite.add(post)
        fav_json['fav_num'] = len(post.favorite.all())

    return HttpResponse(json.dumps(fav_json))


@csrf_exempt
def watcher(request):
    '''
    1. Declare that current user start/stop watching the post.
    2. Provide polling for current watcher list of the post.

    @param request: A POST request with a post_id

    @return: A rendered html showing current watcher list
    '''
    watcher_list = []
    if 'post_id' in request.POST:
        post = get_object_or_404(Post, id=request.POST['post_id'])

        if 'type' in request.POST and request.user.is_authenticated():
            type = request.POST['type']

            if type == '0':
                request.user.userinfo.watch.remove(post)
            elif type == '1':
                request.user.userinfo.watch.add(post)
                # Here we add the play number
                post.play_num += 1
                post.save()

        info_list = post.watch.all()
        for info in info_list:
            watcher_list.append(info.user)

        watcher_list = split_list(watcher_list, 6)

    return render_to_response('include/watcher_list.html', {
        'watcher_list': watcher_list,
    }, context_instance=RequestContext(request))


@csrf_exempt
def posts(request):
    '''
    Return list of posts to current user,
    if the user is authenticated, he can fetch the posts he has published.

    @param request: A POST request with three optional key-values.
                    1. category: What kinds of posts
                    2. sort: How the posts are sorted
                    3. personal: If fetch posts published by current user

    @return: A rendered html showing result post list
    '''

    sort = 'date'
    category = ''
    personal = ''
    if 'sort' in request.POST:
        sort = request.POST['sort'].lower()
    if 'category' in request.POST:
        category = request.POST['category'].lower()
    if 'personal' in request.POST:
        personal = request.POST['personal'].lower()

    if sort != 'date' and sort != 'title':
        sort = 'date'
    if category == 'tv':
        category = 't'
    elif category == 'game':
        category = 'g'
    elif category == 'cartoon':
        category = 'c'
    elif category == 'course':
        category = 's'
    elif category == 'favorite':
        category = 'f'
    else:
        category = ''

    if category == '': # return home panel

        if personal == 'true':
            hot_list = Post.objects.filter(author=request.user).order_by('-play_num')
            fresh_list = Post.objects.filter(author=request.user).order_by('-date')

        else:
            hot_list = Post.objects.order_by('-play_num')
            fresh_list = Post.objects.order_by('-date')

        hot_list = split_list(hot_list, 3)
        fresh_list = split_list(fresh_list, 3)

        return render_to_response('include/tab_panel_home.html', {
            'hot_list': hot_list,
            'fresh_list': fresh_list,
        }, context_instance=RequestContext(request))


    else:
        if category == 'f': # return favorite
            post_list = request.user.userinfo.favorite.all()
        elif personal == 'true':
            post_list = Post.objects.filter(category=category, author=request.user).order_by('-' + sort)
        else:
            post_list = Post.objects.filter(category=category).order_by('-' + sort)

        page_list = split_list(post_list, 9)

        return render_to_response('include/tab_panel.html', {
            'page_list': page_list,
        }, context_instance=RequestContext(request))


@login_required()
@csrf_exempt
def people(request):
    '''
    Return a list of following/followed users to current user.

    @param request: A POST request with a category (following/followed)

    @return: A rendered html showing result user list
    '''
    people_list = []

    category = 'following'
    if 'category' in request.POST:
        category = request.POST['category'].lower()

    if category != 'following' and category != 'followed':
        category = 'following'

    if category == 'following':
        people_list = request.user.userinfo.follow.all()
    else:
        info_list = request.user.follow.all()
        for info in info_list:
            people_list.append(info.user)

    page_list = split_list(people_list, 9)

    return render_to_response('include/people_panel.html', {
        'page_list': page_list,
        'category': category,
    }, context_instance=RequestContext(request))


@csrf_exempt
def profile(request):
    '''
    Return a list pf posts published by target user.

    @param request: A POST request with an user_id

    @return: A rendered html showing result post list
    '''
    post_list = []
    sort = 'date'

    if 'user_id' in request.POST:
        author = get_object_or_404(User, id=request.POST['user_id'])
        post_list = Post.objects.filter(author=author).order_by('-' + sort)

    page_list = split_list(post_list, 9)

    return render_to_response('include/tab_panel.html', {
        'page_list': page_list,
    }, context_instance=RequestContext(request))


@csrf_exempt
def search(request):
    '''
    Search for posts in their titles and text notes.

    @param request: A POST request with the query string

    @return: A rendered html showing result post list


    '''
    post_list = None
    print request.POST
    if ('search_query' in request.POST) and request.POST['search_query'].strip():
        search_query = request.POST['search_query']
        sort = 'date'
        personal = ''
        if 'sort' in request.POST:
            sort = request.POST['sort'].lower()
        if 'personal' in request.POST:
            personal = request.POST['personal'].lower()

        if sort != 'date' and sort != 'title':
            sort = 'date'

        query = get_query(search_query, ['title', 'text', ])

        if personal == 'true':
            post_list = Post.objects.filter(author=request.user).filter(query).order_by('-' + sort)
        else:
            post_list = Post.objects.filter(query).order_by('-' + sort)

    page_list = split_list(post_list, 9)

    return render_to_response('include/tab_panel.html', {
        'page_list': page_list,
    }, context_instance=RequestContext(request))


def get_query(search_query, search_fields):
    '''
    A toolkit method.
    Generate filters using query string and search fields.

    @param search_query: The query string from users
    @param search_fields: Which fields of post we should look up in

    @return: query filters for Post.objects.filter()
    '''
    find_terms = re.compile(r'"([^"]+)"|(\S+)').findall
    norm_space = re.compile(r'\s{2,}').sub

    query = None # Query to search for every search term
    terms = [norm_space(' ', (t[0] or t[1]).strip()) for t in find_terms(search_query)]

    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field in search_fields:
            q = Q(**{"%s__icontains" % field: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query

    return query