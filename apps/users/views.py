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
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.comments.models import Comment
from django.contrib.sites.models import Site
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, defaultfilters
from django.template.defaultfilters import slugify
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.generic.list_detail import object_list, object_detail
from django.utils.translation import ugettext as _
from insidetags.apps.posts.models import Post
from models import UserProfile, ConfirmAccountForm
from django.conf import settings
from datetime import datetime

def update_data_user(user, profile):
    from socialauth.models import *
    
    auth = AuthMeta.objects.get(user=user)
    
    user_association = {
        'Default': OpenidProfile,
        'Facebook': FacebookUserProfile,
        'Twitter': TwitterUserProfile,
        'LinkedIn': LinkedInUserProfile
    }

    if auth.provider in user_association:
        provider_profile = user_association[auth.provider]
    else:
        provider_profile = user_association['Default']

    data = provider_profile.objects.get(user=user)
    
    try:
        if data.url is not None: 
            profile.url = data.url
    except (AttributeError, TypeError):
        pass
            
    try:
        if data.profile_image_url is not None: 
            profile.avatar = data.profile_image_url
    except (AttributeError, TypeError):
        pass
    
@login_required
def dashboard(request):
    posts_list = Post.objects.select_related().filter(author=request.user).order_by('-created_at')
    nb_posts_online = posts_list.filter(status=3, published_at__lte=datetime.now()).count()
    comments_list = Comment.objects.filter(user=request.user, is_public=True, \
        is_removed=False).order_by('-submit_date')
    profile = request.user.get_profile()
    
    return object_list(request, queryset=posts_list, extra_context={'comments_list': comments_list[:10], \
        'comments_count': comments_list.count(), 'nb_posts_online': nb_posts_online, \
        'profile': profile}, template_name='users/dashboard.html', template_object_name='posts')
    
@login_required
def login_redirect(request):
    user = get_object_or_404(User, pk=request.user.pk)
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if '_next_page' in request.session:
        redirect_to = request.session['_next_page']
    else:
        redirect_to = getattr(settings, 'LOGIN_REDIRECT_BOARD', reverse('dashboard'))
    
    if profile.nb_login > 0:
        profile.nb_login += 1
        profile.save()
        update_data_user(user, profile)
        return HttpResponseRedirect(redirect_to)
    
    if request.method == 'POST':
        form = ConfirmAccountForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            
            user.username = form.cleaned_data['username']
            user.email = form.cleaned_data['email']
            user.save()

            profile.nb_login += 1
            update_data_user(user, profile)
            profile.save()
            
            if '_next_page' in request.session:
                del request.session['_next_page']
            
            return HttpResponseRedirect(redirect_to)
    else:
        initial = {'username': user.username, 'email': user.email}
        form = ConfirmAccountForm(instance=profile, initial=initial)
    
    return render_to_response('users/finish_register.html', {'form': form}, \
        context_instance=RequestContext(request))
