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

from django.db.models import Q
from django.core.cache import cache
from django.http import HttpRequest
from django.utils.cache import get_cache_key
from django.utils.safestring import mark_safe
from django.conf import settings
import re, urllib

def expire_page(path):
    request = HttpRequest()
    request.path = path
    key = get_cache_key(request)
    
    if cache.has_key(key):   
        cache.delete(key)
        
def not_combining(char):
    return unicodedata.category(char) != 'Mn'

def strip_accents(value):
    import unicodedata
    value = unicodedata.normalize('NFKD', value).encode('ascii','ignore')
    return value

def normalize_query(query_string, findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
        normspace=re.compile(r'\s{2,}').sub):
    ''' 
    Splits the query string in invidual keywords, getting rid of unecessary spaces
    and grouping quoted words together.
    Example:
    >>> normalize_query('  some random  words "with   quotes  " and   spaces')
    ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
    
    Source : http://www.julienphalip.com/blog/2008/08/16/adding-search-django-site-snap/
    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)] 

def get_query(query_string, search_fields):
    ''' 
    Returns a query, that is a combination of Q objects. That combination
    aims to search keywords within a model by testing the given search fields.
        
    Source : http://www.julienphalip.com/blog/2008/08/16/adding-search-django-site-snap/
    '''
    query = None # Query to search for every search term        
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query
    
def url_encode(url):
    dict = urllib.urlencode({'key': url})
    return dict[4:]

def url_decode(url):
    return urllib.unquote_plus(url)
    
BITLY_LOGIN = getattr(settings, 'BITLY_LOGIN', None)
BITLY_APIKEY = getattr(settings, 'BITLY_APIKEY', None)
TWITTER_LOGIN = getattr(settings, 'TWITTER_LOGIN', None)
TWITTER_PASS = getattr(settings, 'TWITTER_PASSWORD', None)
    
def shorten_url(long_url, login_user, api_key):
    values = {
        'version': '2.0.1',
        'longUrl': long_url,
        'login': BITLY_LOGIN,
        'apiKey': BITLY_APIKEY
    }

    params = urllib.urlencode(values)
    request = urllib.urlopen('http://api.bit.ly/shorten?%s' % params)
    responde = request.read()
    request.close()
    responde_dict = eval(responde)
    try:
        short_url = responde_dict['results'][long_url]['shortUrl']
    except:
        print responde_dict
        pass
        
    return short_url
    
def post_to_twitter(url, title, tags):
    if not BITLY_LOGIN or not BITLY_APIKEY or not TWITTER_LOGIN or not TWITTER_PASS:
        return

    import twitter

    url = shorten_url(url, BITLY_LOGIN, BITLY_APIKEY)
    tweet = '%s %s' % (title, url)
    hashtags = ''

    if tags:
        tags = tags.replace(',', '')
        new_tags = list()
        for tag in tags.split():
            new_tags.append('#%s' % tag)
        hashtags = ' '.join(new_tags)

    if len(tweet) > 140:
        title = truncate_chars(title, 140-4-len(url))
        tweet = '%s %s' % (title, url)

    for tag in hashtags.split():
        if (len(tweet) + len(tag) + 1) <= 140:
            tweet += ' %s' % tag
            
    api = twitter.Api(username=TWITTER_LOGIN, password=TWITTER_PASS)
    api.PostUpdates(tweet)

    return url

def twitterfy(text):
    ''' 
    Parse links, @replies and #hashtags
    
    Source : http://teebes.com/blog/17/simple-python-twitter-rss-feed-parser
    ''' 
    text = re.sub(r'(http://(\w|\.|/|\?|=|%|&)+)', \
        lambda x: '<a href="%s">%s</a>' % (x.group().strip(), x.group().strip()), text)

    text = re.sub(r'@(\w+)', lambda x: '<a href="http://twitter.com/%s">%s</a>' \
        % (x.group()[1:], x.group()), text)

    text = re.sub(r'#(\w+)', lambda x: '<a href="http://twitter.com/search?q=%%23%s">%s</a>' \
        % (x.group()[1:], x.group()), text)

    return mark_safe(text)