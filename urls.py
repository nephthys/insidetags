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

from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.sitemaps import FlatPageSitemap
from insidetags.apps.posts.models import Post
from insidetags.apps.posts.views import *
from insidetags.apps.users.views import *
from insidetags.apps.contact.views import *
from insidetags.apps.posts.feeds import *
from insidetags.apps.posts.sitemaps import *

admin.autodiscover()

feeds_dict = {
    'posts': HomepagePosts,
    'featured': FeaturedPosts,
    'category': CategoryPosts,
    'tag': TagPosts,
    'comment': RecentsPostComments,
    'comments': RecentsComments
}

archives_dict = {
    'queryset': Post.objects.select_related().filter(status=3).order_by('-published_at'),
    'date_field': 'published_at',
    'template_object_name': 'posts',
    'allow_future': False
}

sitemaps = {
    'base': BaseSitemap,
    'blog': BlogSitemap,
    'flatpages': FlatPageSitemap,
}

archives_dict_daymonth = archives_dict.copy()
archives_dict_daymonth.update({'template_name': 'posts/post_archive.html'})

urlpatterns  = patterns('django.views.generic.date_based',
    url(r'^archives/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/$', 'archive_day', \
        dict(archives_dict_daymonth, extra_context={'archive_day': True}), name='archive_day'),
    url(r'^archives/(?P<year>\d{4})/(?P<month>[a-z]{3})/$', 'archive_month', \
        dict(archives_dict_daymonth, extra_context={'archive_month': True}), name='archive_month'),
    url(r'^archives/(?P<year>\d{4})/$', 'archive_year', archives_dict, name='archive_year'),
)

urlpatterns += patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^comments/', include('django.contrib.comments.urls')),
    url(r'^comments/redirect_to/(?P<id>\d+)/$',         redirect_to_comment, name='redirect_to_comment'),
    (r'^accounts/', include('socialauth.urls')),
    url(r'^feeds/$',                                    feeds_list, name='feeds'),
    url(r'^contact/$',                                  contact_form, name='contact'),
    url(r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds_dict}),
    url(r'^archives/$', 'django.views.generic.simple.direct_to_template', {
        'template': 'posts/post_archive_index.html', 
        'extra_context': {'list_dates': Post.objects.dates('published_at', 'month')}
    }, name='archive_index'),
    url(r'^$',                                          last_posts, name='last_posts'),
    url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.index', {'sitemaps': sitemaps}),
    url(r'^sitemap-(?P<section>.+)\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    url(r'^robots\.txt$', lambda _: HttpResponse('User-agent: *\nDisallow:\n', mimetype='text/plain')),
    # Users
    url(r'^post/create/$',                              create_post, name='create_post'),
    url(r'^post/edit/(?P<post_id>\d+)/$',               update_post, name='update_post'),
    url(r'^post/submit/(?P<post_id>\d+)/$',             submit_post, name='submit_post'),
    url(r'^dashboard/$',                                dashboard, name='dashboard'),
    url(r'^accounts/done/$',                            login_redirect, name='socialauth_editprofile'),
    url(r'^profile/(?P<slug>.*)/$',                     posts_author, name='profile_user'),
    # Posts   
    url(r'^search/(?P<query>[\+\-\d\w]+)/$',            search_posts, name='search_posts'),
    url(r'^tag/(?P<slug>.*)/$',                         view_tag, name='view_tag'),
    url(r'^vote/(?P<post_id>\d+)/$',                    vote_post, name='vote_post'),   
    url(r'^(?P<cat>[\-\d\w]+)/$',                       view_cat, name='view_cat'),
    url(r'^(?P<cat>[\-\d\w]+)/(?P<slug>[\-\d\w]+)/$',   view_post, name='view_post'),
)

if settings.DEBUG:
    urlpatterns += patterns('django.views.static', (r'^site_media/(?P<path>.*)$', 'serve', {
        'document_root': settings.STATIC_ROOT,
        'show_indexes': True
    }),)
    

