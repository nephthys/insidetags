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
from django.utils.translation import ungettext, ugettext as _
import datetime, hashlib
from insidetags.functions import *

register = template.Library()

@register.filter
def date_diff(d):
    if not d:
        return 'None'
        
    now = datetime.datetime.now()
    today = datetime.datetime(now.year, now.month, now.day)
    delta = now - d
    delta_midnight = today - d
    days = delta.days
    hours = round(delta.seconds / 3600., 0)
    minutes = round(delta.seconds / 60., 0)
    chunks = (
        (365.0, lambda n: ungettext('year', 'years', n)),
        (30.0, lambda n: ungettext('month', 'months', n)),
        (7.0, lambda n : ungettext('week', 'weeks', n)),
        (1.0, lambda n : ungettext('day', 'days', n)),
    )
    
    if days == 0:
        if hours == 0:
            if minutes > 0:
                return ungettext('il y a 1 minute', \
                    'il y a %(minutes)d minutes', minutes) % \
                    {'minutes': minutes}
            else:
                return _('il y a moins d\'une minute')
        else:
            return ungettext('il y a 1 heure', 'il y a %(hours)d heures', hours) \
            % {'hours': hours}

    if delta_midnight.days == 0:
        return _(u'hier à %s') % d.strftime('%H:%M')

    count = 0
    for i, (chunk, name) in enumerate(chunks):
        if days >= chunk:
            count = round((delta_midnight.days + 1)/chunk, 0)
            break

    return _('il y a %(number)d %(type)s') % \
        {'number': count, 'type': name(count)}
        
@register.inclusion_tag('gravatar.html')
def gravatar(email, size=48):
    context = {'gravatar_id': hashlib.md5(email).hexdigest(), 'gravatar_size': str(size)}
    site = cache.get('static_site')
    if site:
        context['SITE_DOMAIN'] = site.domain
        context['SITE_NAME'] = site.name
    return context

register.filter('url_encode', url_encode)
register.filter('url_decode', url_decode)