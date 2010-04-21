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

from django.utils.translation import ugettext as _
from django.contrib import admin
from models import *

# http://www.djangosnippets.org/snippets/1054/ è
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'author', 'nb_views', 'nb_comments', \
        'open_comments', 'updated_at')
    list_filter = ('status', 'open_comments')
    search_fields = ['title', 'tags',]
    date_hierarchy = 'updated_at'
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = [
        (None,                          {'fields': ['title', 'slug', 'category', 'tags']}),
        (_('Contenu'),                  {'fields': ['head', 'body']}),
        (_('Dates relatives'),          {'fields': ['published_at']}),
        (_(u'Informations complémentaires'), {'fields': ['status', 'featured', 'open_comments', \
            'nb_views', 'nb_votes', 'nb_comments']}),
        (_(u'Meta-données'),          {'fields': ['page_title', 'page_description'], \
            'classes': ['collapse']}),
    ]
    
    class Media:
        js = (
            '/site_media/js/jquery-1.4.2.min.js', 
            '/site_media/js/jquery.tabby.js',
            '/site_media/js/extends_admin.js'
        )
    def save_model(self, request, obj, form, change):
        obj.author = request.user 
        obj.save()
        
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    
admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Vote)