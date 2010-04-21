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
from django.contrib.sites.models import Site
from django.conf import settings

def context_base(request):
    site = Site.objects.get(id=settings.SITE_ID)
    cache.set('static_site', site, 60*60*24)
    
    context = {
        'SITE_ID': settings.SITE_ID, 
        'SITE_NAME': site.name, 
        'SITE_DOMAIN': site.domain,
        'TWITTER_LOGIN': getattr(settings, 'TWITTER_LOGIN', ''),
    }
    
    if getattr(settings, 'FEEDS_URL', ''):
        for name in settings.FEEDS_URL:
            context['FEED_URL_%s' % name.upper()] = settings.FEEDS_URL[name]
    
    return context