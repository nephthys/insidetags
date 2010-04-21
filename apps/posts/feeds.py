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
from django.contrib.comments.models import Comment
from django.contrib.syndication.feeds import FeedDoesNotExist
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sites.models import Site
from django.contrib.syndication.feeds import Feed
from django.utils.translation import ugettext as _
from templatetags.common_tags import url_decode, url_encode
from tagging.models import Tag, TaggedItem
from models import Post, Category
from datetime import datetime
from django.conf import settings

current_site = Site.objects.get_current()
  
class HomepagePosts(Feed):
    title = '%s - %s' % (current_site.name, _('Derniers articles'))
    link = ''
    description = getattr(settings, 'BLOG_SLOGAN', '')
            
    def items(self):
        return Post.objects.select_related().filter(status=3, \
            published_at__lte=datetime.now()).order_by('-published_at')[:25]

    def item_pubdate(self, item):
        return item.published_at
        
    def item_categorie(self, item):
        return item.category.name
        
    def item_author_name(self, item):
        return item.author.username
        
    def item_author_email(self, item):
        if item.author.get_profile().show_email:
            return item.author.email
        else:
            return getattr(settings, 'CONTACT_EMAIL_WEBMASTER', None)
        
class FeaturedPosts(Feed):
    title = '%s - %s' % (current_site.name, _(u'Lectures recommandées'))
    link = ''
    description = ''
    
    def items(self):
        return Post.objects.select_related().filter(status=3, featured=True, \
            published_at__lte=datetime.now()).order_by('-published_at')[:25]
            
    def item_pubdate(self, item):
        return item.published_at

    def item_categorie(self, item):
        return item.category.name

    def item_author_name(self, item):
        return item.author.username

    def item_author_email(self, item):
        if item.author.get_profile().show_email:
            return item.author.email
        else:
            return getattr(settings, 'CONTACT_EMAIL_WEBMASTER', None)
    
class CategoryPosts(Feed):
    def get_object(self, bits):
        if len(bits) != 1:
            raise ObjectDoesNotExist
        return Category.objects.get(slug=bits[0])
        
    def link(self, obj):
        return obj.get_absolute_url()
        
    def title(self, obj):
        return _(u'Catégorie %(name)s - %(site)s') % {'name': obj.name, 'site': current_site.name}
        
    def description(self, obj):
        if obj.description:
            return obj.description
        else:
            return ''
        
    def items(self, obj):
        return Post.objects.select_related().filter(status=3, category=obj, \
            published_at__lte=datetime.now()).order_by('-published_at')[:25]
            
    def item_pubdate(self, item):
        return item.published_at

    def item_categorie(self, item):
        return item.category.name

    def item_author_name(self, item):
        return item.author.username

    def item_author_email(self, item):
        if item.author.get_profile().show_email:
            return item.author.email
        else:
            return getattr(settings, 'CONTACT_EMAIL_WEBMASTER', None)
        
class TagPosts(Feed):
    def get_object(self, bits):
        if len(bits) != 1:
            raise ObjectDoesNotExist
        return Tag.objects.get(name=url_decode(bits[0]))
        
    def link(self, obj):
        tag_slug = url_encode(obj.name)
        return reverse('view_tag', args=[tag_slug])
        
    def items(self, obj):
        return TaggedItem.objects.get_by_model(Post, obj).select_related(). \
            filter(status=3, published_at__lte=datetime.now()).order_by('-published_at')[:25]
            
    def item_pubdate(self, item):
        return item.published_at

    def item_categorie(self, item):
        return item.category.name

    def item_author_name(self, item):
        return item.author.username

    def item_author_email(self, item):
        if item.author.get_profile().show_email:
            return item.author.email
        else:
            return getattr(settings, 'CONTACT_EMAIL_WEBMASTER', None)
    
class RecentsComments(Feed):
    title = '%s - %s' % (current_site.name, _(u'Derniers commentaires'))
    link = ''
    description = ''
    
    def items(self):
        return Comment.objects.select_related().filter(is_public=True, is_removed=False).order_by('-submit_date')[:25]
    
    def item_link(self, item):
        return reverse('redirect_to_comment', args=[item.pk])
        
    def item_pubdate(self, item):
        return item.submit_date
        
class RecentsPostComments(Feed):
    def get_object(self, bits):
        if len(bits) != 1:
            raise ObjectDoesNotExist
        return Post.objects.get(id=bits[0])
        
    def link(self, obj):
        return obj.get_absolute_comments_url()
        
    def title(self, obj):
        return _('Commentaires - %(site)s') % {'site': current_site.name}
        
    def description(self, obj):
        return obj.title
        
    def items(self, obj):
        return Comment.objects.for_model(obj).select_related().filter(is_public=True, is_removed=False).order_by('-submit_date')[:25]
        
    def item_link(self, item):
        return reverse('redirect_to_comment', args=[item.pk])

    def item_pubdate(self, item):
        return item.submit_date