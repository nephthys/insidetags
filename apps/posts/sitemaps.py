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
from django.contrib.sitemaps import Sitemap
from templatetags.common_tags import url_encode
from models import Post, Category
from tagging.models import Tag
from datetime import datetime
from django.conf import settings

class BaseSitemap(Sitemap):
    priority = 0.8
    
    def items(self):
        return ['/', '/archives/', '/contact/']
        
    def location(self, obj):
        return obj
        
class BlogSitemap(Sitemap):
    changefreq = 'never'
    priority = 0.7

    def items(self):
        return Post.objects.filter(status=3, published_at__lte=datetime.now())

    def lastmod(self, obj):
        return obj.published_at