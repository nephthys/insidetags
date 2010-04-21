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

from django import template
from django.core.cache import cache
from django.contrib.comments.models import Comment
from django.utils.translation import ungettext, ugettext as _
from insidetags.apps.posts.models import Post, Category
from insidetags.functions import *
from datetime import datetime
import twitter

register = template.Library()

class LatestFeaturedPosts(template.Node):
    def __init__(self, num, varname):
        self.num, self.varname = int(num), varname
        
    def render(self, context):
        queryset = cache.get('sidebar_latest_featured_posts')
        if queryset is None:
            queryset = Post.objects.select_related().filter(status=3, featured=True, \
                published_at__lte=datetime.now()).order_by('-published_at')[:self.num]
            qlist = list(queryset)
            cache.set('sidebar_latest_featured_posts', qlist, 60*60*24)
        context[self.varname] = queryset
        return ''
        
class LatestComments(template.Node):
    def __init__(self, num, varname):
        self.num, self.varname = int(num), varname

    def render(self, context):
        queryset = cache.get('sidebar_latest_comments')
        if queryset is None:
            queryset = Comment.objects.filter(is_public=True, is_removed=False).order_by('-submit_date')[:self.num]
            qlist = list(queryset)
            cache.set('sidebar_latest_comments', qlist, 60*60*24)
        context[self.varname] = queryset
        return ''
        
class PopularCategories(template.Node):
    def __init__(self, num, varname):
        self.num, self.varname = int(num), varname

    def render(self, context):
        queryset = cache.get('speedbar_categories')
        if queryset is None:
            queryset = Category.objects.all().order_by('-posts_number')[:self.num]
            qlist = list(queryset)
            cache.set('speedbar_categories', qlist, 60*60*24)
        context[self.varname] = queryset
        return ''
        
class LatestTweetsNode(template.Node):
    def __init__(self, username, num, varname):
        try:
            self.username = template.Variable(username)
        except template.VariableDoesNotExist:
            self.username = username
        self.num = int(num)
        self.varname = varname
    
    def render(self, context):
        try:
            self.username = self.username.resolve(context)
        except template.VariableDoesNotExist:
            pass
        cache.delete('tweets_%s' % self.username)
        tweets = cache.get('tweets_%s' % self.username)
        if tweets is None:
            tweets = []
            tweets_nb = 0
            tweets_list = twitter.Api().GetUserTimeline(self.username)
            for tweet in tweets_list:
                if not tweet.text.startswith('@') and tweets_nb < self.num:
                    tweet.text = twitterfy(tweet.text)
                    tweet.date = datetime.strptime(tweet.created_at, "%a %b %d %H:%M:%S +0000 %Y")
                    tweets.append(tweet)
                    tweets_nb += 1
            cache.set('tweets_%s' % self.username, tweets, 60*15)
        context[self.varname] = tweets
        return ''
                 
@register.tag
def get_latest_tweets(parser, token):
    bits = token.contents.split() # {% get_latest_tweets nephthys 5 as tweets_list %}
    if len(bits) != 5:
        raise template.TemplateSyntaxError("'%s' tag takes three arguments" % bits[0])
    if bits[3] != 'as':
        raise template.TemplateSyntaxError("third argument to '%s' tag must be 'as'" % bits[0])
    # raise template.TemplateSyntaxError('1: %s, 2: %s, 3: %s' % (bits[1], bits[2], bits[4]))
    return LatestTweetsNode(bits[1], bits[2], bits[4])
            
@register.tag
def get_featured_posts(parser, token):
    bits = token.contents.split() # {% get_featured_posts 5 as list_featured %}
    if len(bits) != 4:
        raise template.TemplateSyntaxError("'%s' tag takes three arguments" % bits[0])
    if bits[2] != 'as':
        raise template.TemplateSyntaxError("third argument to '%s' tag must be 'as'" % bits[0])
    return LatestFeaturedPosts(bits[1], bits[3])

@register.tag
def get_last_comments(parser, token):
    bits = token.contents.split() # {% get_last_comments 10 as list_comments %}
    if len(bits) != 4:
        raise template.TemplateSyntaxError("'%s' tag takes three arguments" % bits[0])
    if bits[2] != 'as':
        raise template.TemplateSyntaxError("third argument to '%s' tag must be 'as'" % bits[0])
    return LatestComments(bits[1], bits[3])

@register.tag
def get_popular_categories(parser, token):
    bits = token.contents.split() # {% get_popular_categories 7 as categories %}
    if len(bits) != 4:
        raise template.TemplateSyntaxError("'%s' tag takes three arguments" % bits[0])
    if bits[2] != 'as':
        raise template.TemplateSyntaxError("third argument to '%s' tag must be 'as'" % bits[0])
    return PopularCategories(bits[1], bits[3])