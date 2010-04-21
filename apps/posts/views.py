#-*- encoding: utf-8 -*-
"""
Copyright (c) 2010 Camille "nephthys" Bouiller <aftercem@gmail.com>

InsideTags is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.
 
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.
 
You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, defaultfilters
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.create_update import create_object
from models import Post, Category, Vote, SubmitPost
from insidetags.apps.users.models import UserProfile
from insidetags.functions import *
from tagging.models import Tag, TaggedItem
from datetime import timedelta, datetime, time, date
from time import strptime
from django.conf import settings

def last_posts(request, page=0):
    search_name = request.POST.get('search_name', None)
    
    if search_name:
        return HttpResponseRedirect(reverse('search_posts', args=[url_encode(search_name)]))
    
    post_list = Post.objects.select_related('category', 'author').filter(status=3, \
        published_at__lte=datetime.now()).order_by('-published_at')
    
    return object_list(request, queryset=post_list, \
        paginate_by=getattr(settings, 'NB_POSTS_BY_PAGE_HOMEPAGE', 10), page=page, \
        extra_context={'home': True}, template_object_name='posts')
        
def view_cat(request, cat, page=0):
    category = get_object_or_404(Category, slug=cat)
    post_list = Post.objects.select_related('category', 'author').filter(category__slug=cat, status=3, \
        published_at__lte=datetime.now()).order_by('-published_at')
        
    res_feed_url = None
    if getattr(settings, 'FEEDS_URL', '') and 'category_%d' % category.id in settings.FEEDS_URL: 
        res_feed_url = settings.FEEDS_URL['category_%d' % category.id]
        
    return object_list(request, queryset=post_list, \
        paginate_by=getattr(settings, 'NB_POSTS_BY_PAGE_CATEGORY', 10), page=page, \
        extra_context={'category': category, 'RES_FEED_URL': res_feed_url}, \
        template_object_name='posts')
    
def view_tag(request, slug, page=0):
    slug = url_decode(slug)
    
    tag = get_object_or_404(Tag, name=slug)
    tags_list = TaggedItem.objects.get_by_model(Post, tag).select_related('category', 'author'). \
        filter(status=3, published_at__lte=datetime.now()).order_by('-published_at')
    related_tags = Tag.objects.related_for_model(tag, Post, counts=True, min_count=2)[:5]
    
    return object_list(request, queryset=tags_list, \
        paginate_by=getattr(settings, 'NB_POSTS_BY_PAGE_TAG', 10), page=page, \
        extra_context={'tag': tag, 'related_tags': related_tags}, template_object_name='posts')
        
def posts_author(request, slug, page=0):
    author = get_object_or_404(User, username=url_decode(slug))
    post_list = Post.objects.select_related('category', 'author').filter(author__exact=author, \
        status=3, published_at__lte=datetime.now()).order_by('-published_at')

    return object_list(request, queryset=post_list, \
        paginate_by=getattr(settings, 'NB_POSTS_BY_PAGE_AUTHOR', 10), page=page, \
        extra_context={'author': author, 'display': 'clean'}, template_object_name='posts')
        
def search_posts(request, query, page=0):
    from django.db.models import Q
    from functions import *
    
    query = url_decode(query)
    entry_query = get_query(query, ['title', 'head_html', 'body_html',])
    post_list = Post.objects.select_related('category', 'author').filter(Q(status=3) & \
        Q(published_at__lte=datetime.now()) & entry_query).order_by('-published_at')
    
    return object_list(request, queryset=post_list, \
        paginate_by=getattr(settings, 'NB_POSTS_BY_PAGE_SEARCH', 10), page=page, \
        extra_context={'search': query}, template_object_name='posts')
       
def view_post(request, cat, slug):
    reply_to = request.GET.get('reply_to', None)
    id_comment = request.GET.get('c', None)
    
    if id_comment:
        return HttpResponseRedirect(reverse('redirect_to_comment', args=[id_comment]))
        
    post = get_object_or_404(Post.objects.select_related('category', 'author'), slug=slug)
    post.nb_views += 1
    post.save()
    related_tags = Tag.objects.get_for_object(post)
    
    return render_to_response('posts/post_detail.html', {'post': post, 'related_tags': related_tags, \
        'reply_to': reply_to}, context_instance=RequestContext(request))  
        
def vote_post(request, post_id, mode='plain'):
    post_id = int(post_id)
    post = get_object_or_404(Post, id=post_id)
    kwargs = dict(post=post)

    if not mode in ['plain', 'ajax'] or '_pv_%d' % post_id in request.session:
        return HttpResponseRedirect(post.get_absolute_url())

    if request.user.is_authenticated():
        kwargs['user'] = request.user
    else:
        kwargs['ip'] = request.META['REMOTE_ADDR']

    try:
        Vote.objects.get(**kwargs)
        output_ajax = 0
    except Vote.DoesNotExist:
        new_vote = Vote(**kwargs)
        new_vote.save()
        post.nb_votes += 1
        post.save()
        request.session['_pv_%d' % post_id] = True
        request.session.set_expiry(timedelta(days=365))
        output_ajax = 1

    if mode == 'ajax':
        return HttpResponse(output_ajax)
    else:
        return HttpResponseRedirect(post.get_absolute_url())
        
def redirect_to_comment(request, id):
    from django.contrib.comments.models import Comment
    comment = get_object_or_404(Comment, pk=id)
    return HttpResponseRedirect('%s#c%d' % (comment.content_object.get_absolute_url(), int(id)))

@login_required
def create_post(request):
    if request.method == 'POST':
        form = SubmitPost(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.tags = strip_accents(form.cleaned_data['tags'])
            post.save()
            if post.status == 1:
                object = Post.objects.get(id=post.id)
                return HttpResponseRedirect(object.get_absolute_url())
            else:
                return HttpResponseRedirect(reverse('dashboard'))
    else:
        form = SubmitPost()
    return render_to_response('posts/post_form.html', {'form': form}, \
            context_instance=RequestContext(request))
            
@login_required
def update_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if post.author != request.user:
        return HttpResponseRedirect('/')
        
    if request.method == 'POST':
        form = SubmitPost(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.status = int(form.cleaned_data['status'])
            post.tags = strip_accents(form.cleaned_data['tags'])
            post.save()
            if post.status == 1:
                object = Post.objects.get(id=post.id)
                return HttpResponseRedirect(object.get_absolute_url())
            else:
                return HttpResponseRedirect(reverse('dashboard'))
    else:
        form = SubmitPost(instance=post)
    return render_to_response('posts/post_form.html', {'form': form}, \
        context_instance=RequestContext(request))
            
@login_required
def submit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=1)
    
    if post.author != request.user:
        return HttpResponseRedirect('/')
        
    post.status = 2
    post.save()
    
    return HttpResponseRedirect(reverse('dashboard'))
    
def feeds_list(request):
    cats_list = Category.objects.all().order_by('-posts_number')
    
    return object_list(request, queryset=cats_list, \
        template_name='posts/feeds_list.html', template_object_name='cats')