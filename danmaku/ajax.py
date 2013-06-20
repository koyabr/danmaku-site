from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse

from django.views.decorators.csrf import csrf_exempt

from danmaku.models import Post, UserInfo
from django.contrib.auth.models import User
from django.db.models import Q

import re
import json


def split_list(post_list, page_len=3):
    # split a list of posts into pages
    page_list = []
    i = 0
    while i + page_len <= len(post_list):
        page_list.append(post_list[i:i + 3])
        i += 3

    if i < len(post_list):
        page_list.append(post_list[i:])

    return page_list


def user(request):
# Get hash for user's email
    email_hash = ""
    if request.user.is_authenticated():
        email_hash = request.user.userinfo.hash

    user_json = {}
    user_json["email_hash"] = email_hash
    return HttpResponse(json.dumps(user_json))


@csrf_exempt
def follow(request):
    follow_json = {}
    if 'target_id' in request.POST:
        author = get_object_or_404(User, id=request.POST['target_id'])
        if author in request.user.userinfo.follow.all():
            request.user.userinfo.follow.remove(author)
        elif author != request.user:
            request.user.userinfo.follow.add(author)
        follow_json['follow_num'] = len(author.follow.all())

    return HttpResponse(json.dumps(follow_json))


@csrf_exempt
def like(request):
    like_json = {}
    if 'post_id' in request.POST:
        post = get_object_or_404(Post, id=request.POST['post_id'])
        if post in request.user.userinfo.like.all():
            request.user.userinfo.like.remove(post)
        else:
            request.user.userinfo.like.add(post)
        like_json['like_num'] = len(post.like.all())

    return HttpResponse(json.dumps(like_json))


@csrf_exempt
def favorite(request):
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
    watcher_list = []
    if 'post_id' in request.POST:
        post = get_object_or_404(Post, id=request.POST['post_id'])

        if 'type' in request.POST:
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
    # Sort the posts
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
    elif category == 'movie':
        category = 'm'
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


@csrf_exempt
def people(request):
    people_list = []

    sort = 'name'
    category = 'following'
    if 'sort' in request.POST:
        sort = request.POST['sort'].lower()
    if 'category' in request.POST:
        category = request.POST['category'].lower()

    if sort != 'name':
        sort = 'name'
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

    people_id = 0
    sort = 'date'

    if 'sort' in request.POST:
        sort = request.POST['sort'].lower()
    if 'people_id' in request.POST:
        people_id = request.POST['people_id'].lower()

    if sort != 'date' and sort != 'title':
        sort = 'date'

    author = get_object_or_404(User, id=people_id)

    post_list = Post.objects.filter(author=author).order_by('-'+sort)


    page_list = split_list(post_list, 9)

    return render_to_response('include/tab_panel.html', {
        'page_list': page_list,
    }, context_instance=RequestContext(request))

@csrf_exempt
def search(request):
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