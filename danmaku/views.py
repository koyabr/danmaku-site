from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from danmaku.models import Post, UserInfo, Danmaku
from danmaku.forms import PostForm, MyUserCreationForm

import hashlib

'''
@author: koyabr
@contact: koyabr@gmail.com

'''


def home(request):
    '''
    Return the homepage. (OPTIONAL: handle the search query)
    '''

    query = ''
    if 'q' in request.GET:
        query = request.GET['q']

    return render_to_response('home.html', {
        'request': request,
        'query': query,
    }, context_instance=RequestContext(request))


def register(request):
    '''
    Handle the Registration, auto-login if success.
    '''

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            new_user = authenticate(username=request.POST['username'],
                                    password=request.POST['password1'])
            login(request, new_user)
            user_info = UserInfo(user=new_user, hash=hashlib.md5(new_user.email.lower()).hexdigest())
            user_info.save()
            return HttpResponseRedirect(reverse('home', ))
    else:
        form = MyUserCreationForm()
    return render_to_response("register.html", {
        'form': form,
    }, context_instance=RequestContext(request))

@login_required
def manage_posts(request):
    '''
    Jump to personal post-manage center,
    users can add/edit posts, and view their favorite posts.
    '''
    return render_to_response('manage/posts.html', {
        'request': request,
    }, context_instance=RequestContext(request))


@login_required
def manage_people(request):
    '''
    Jump to personal people-manage center,
    users can view other people they are following / followed by.
    '''

    return render_to_response('manage/people.html', {
        'request': request,
    }, context_instance=RequestContext(request))


@login_required
def publish(request):
    '''
    Handle the publish of a post,
    return a special 222 code if success, which tells the javascript to guide user.
    '''
    if request.method == 'POST':
        # Get video data, check and save
        form = PostForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            return HttpResponse(status='222')

    form = PostForm()

    return render_to_response('publish.html', {
        'request': request,
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def edit(request, post_id):
    '''
    Handle the edition of a post,
    return a special 222 code if success, which tells the javascript to guide user.
    '''
    post = get_object_or_404(Post, id=post_id)

    if request.user == post.author and request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return HttpResponse(status='222')


    form = PostForm(instance=post)

    return render_to_response('edit.html', {
        'request': request,
        'form': form,
    }, context_instance=RequestContext(request))


def post(request, post_id):
    '''
    Jump to the post page, and enjoy the video!
    '''
    post = get_object_or_404(Post, id=post_id)

    return render_to_response('post.html', {
        'request': request,
        'post': post,
    }, context_instance=RequestContext(request))



@csrf_exempt
def danmaku(request, post_id, vid):
    '''
    Handle the danmaku player's behaviors.
    1. GET: The player is fetching all danmakus of the post, render using xml and return.
    2. POST: The player is posting a danmaku for the post, save it.
    '''
    if request.method == 'GET':
        danmaku_set = Danmaku.objects.filter(post=Post.objects.get(id=post_id))
        return render_to_response('danmaku.xml', {
            'danmaku_set': danmaku_set,
        }, mimetype="application/xml")


    elif request.method == 'POST':

        new_danmaku = Danmaku(text=request.POST['message'],
                              mode=request.POST['mode'],
                              time=request.POST['stime'],
                              color=request.POST['color'],
                              size=request.POST['size'],
                              post=Post.objects.get(id=post_id)
        )

        new_danmaku.save()
        return HttpResponse(status='200')








