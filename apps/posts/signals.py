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

from django.core.cache import cache
from django.contrib.comments.models import Comment
from django.contrib.sites.models import Site
from django.conf import settings
from insidetags.functions import *
from datetime import datetime
import markdown

# By http://sciyoshi.com/blog/2008/aug/27/using-akismet-djangos-new-comments-framework/
def check_comments_akismet(sender, comment, request, *args, **kwargs):
    try:
        from akismet import Akismet
    except:
        return
    
    # Logged users don't spamming
    if request.user.is_authenticated(): 
        return

    # use TypePad's AntiSpam if the key is specified in settings.py
    if hasattr(settings, 'TYPEPAD_ANTISPAM_API_KEY'):
        ak = Akismet(
            key=settings.TYPEPAD_ANTISPAM_API_KEY,
            blog_url='http://%s/' % Site.objects.get(pk=settings.SITE_ID).domain)
        ak.baseurl = 'api.antispam.typepad.com/1.1/'
    else:
        ak = Akismet(
            key=settings.AKISMET_API_KEY,
            blog_url='http://%s/' % Site.objects.get(pk=settings.SITE_ID).domain)

    if ak.verify_key():
        data = {
            'user_ip': request.META.get('REMOTE_ADDR', '127.0.0.1'),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'referrer': request.META.get('HTTP_REFERER', ''),
            'comment_type': 'comment',
            'comment_author': comment.user_name.encode('utf-8'),
        }

        if ak.comment_check(comment.comment.encode('utf-8'), data=data, build_data=True): 
            comment.flags.create(
                user=comment.content_object.author,
                flag='spam'
            )
            comment.is_public = False
            comment.save()
            
def parse_comments_markdown(sender, comment, request, *args, **kwargs):
    comment.comment = markdown.markdown(comment.comment, \
        ['extra', 'codehilite', 'headerid(level=3)'], safe_mode='remove')
    comment.save()
    
def when_comment_was_posted(sender, instance, *args, **kwargs):
    instance.content_object.nb_comments = Comment.objects.for_model(instance.content_object).filter( \
        object_pk=instance.content_object.id, is_public=True, is_removed=False).count()
    instance.content_object.save()
    
    cache.delete('sidebar_latest_comments')
    # cache.clear()
    
def when_post_was_saved(sender, instance, *args, **kwargs):
    if not kwargs.get('created'):
        return
    from models import Post, Category
    for category in Category.objects.all():
        category.posts_number = Post.objects.filter(category=category, status=3, \
            published_at__lte=datetime.now()).count()
        category.save()