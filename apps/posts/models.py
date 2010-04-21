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

from django import forms
from django.db import models
from django.forms import ModelForm
from django.core.cache import cache
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.comments.models import Comment
from django.utils.translation import ugettext as _
from django.contrib.sitemaps import ping_google
from django.contrib.comments.signals import comment_was_posted
from django.db.models.signals import post_save, post_delete
from django.template.defaultfilters import slugify
from insidetags.functions import *
from signals import *
from datetime import datetime
from tagging.fields import Tag, TagField
from threadedcomments.models import ThreadedComment

MARKDOWN_FORMAT = 'Syntaxe <a href="http://fr.wikipedia.org/wiki/Markdown">markdown</a>'

class Post(models.Model):
    CHOICE_STATUS = (
        (3,  _('En ligne')),
        (2,  _(u'Proposé')),
        (1,  _('Brouillon')),
        (0,  _('Hors ligne')),
        (-1, _(u'Refusé')),
    )
    
    title = models.CharField(_('Titre'), max_length=150, blank=False, null=False)
    slug = models.SlugField(_('URL'), unique=True, null=True, blank=True)
    category = models.ForeignKey('Category', verbose_name=_(u'Catégorie'))
    author = models.ForeignKey(User, verbose_name=_('Auteur'), blank=True, null=True)
    tags = TagField(help_text=_(u'Séparez vos tags par une virgule'))
    
    head = models.TextField(_('Extrait'), help_text=MARKDOWN_FORMAT, null=True, blank=True)
    head_html = models.TextField(editable=False, blank=True, null=True)
    body = models.TextField(_('Contenu'), help_text=MARKDOWN_FORMAT, blank=False, null=False)
    body_html = models.TextField(editable=False, blank=True, null=True)
    
    featured = models.BooleanField(_(u'Article sélectionné'), default=False)
    status = models.PositiveSmallIntegerField(_('Etat'), default=1, choices=CHOICE_STATUS)
    open_comments = models.BooleanField(_(u'Ouvrir les commentaires'), default=True)
    
    created_at = models.DateTimeField(_(u'Date de création'), auto_now_add=True)
    updated_at = models.DateTimeField(_(u'Dernière modification'), auto_now=True)
    published_at = models.DateTimeField(_('Date de publication'), null=True, blank=True)
    
    nb_views = models.IntegerField(_('Nb de clics'), default=0)
    nb_votes = models.PositiveSmallIntegerField(_('Nb de votes'), default=0)
    nb_comments = models.SmallIntegerField(_('Nb de commentaires'), default=0)
    tweet_url = models.URLField(verify_exists=False, blank=True, null=True)
    
    page_title = models.CharField(_('Titre de la page'), max_length=150, null=True, blank=True)
    page_description = models.CharField(_('Description de la page'), max_length=200, null=True, blank=True)
    
    def __unicode__(self):
        return self.title
        
    @models.permalink
    def get_absolute_url(self):
        return ('view_post', (self.category.slug, self.slug,))
    
    def get_absolute_comments_url(self):
        return '%s#c' % self.get_absolute_url()
    
    def is_open_comments(self):
        status = self.open_comments
        diff = datetime.now() - self.published_at
        if diff.days >= 60:
            status = False
        return status
    
    def save(self):
        import markdown
        is_published = False
        # Try to find an unique slug
        if not self.slug:
            slug = slugify(self.title)
            count_slug = Post.objects.filter(slug__exact=slug).count()
            if count_slug:
                slug = '%s-%d' % (slug, count_slug)
            self.slug = slug
        
        if self.status == 3:
            if not self.id:
                if not self.published_at:
                    self.published_at = datetime.now()
                    is_published = True
            else:
                data = Post.objects.get(id=self.id)
                if data.status != self.status and not self.published_at:
                    self.published_at = data.updated_at
                    is_published = True
        
        # Parse head & body in markdown
        if self.head:
            self.head_html = markdown.markdown(self.head, \
                ['extra', 'codehilite(force_linenos=True)', 'headerid(level=3)'], safe_mode='remove')
        self.body_html = markdown.markdown(self.body, \
            ['extra', 'codehilite(force_linenos=True)', 'headerid(level=3)'], safe_mode='remove')
            
        super(Post, self).save()
        cache.delete('sidebar_latest_featured_posts')
        
        if is_published:    
            try:
                site = Site.objects.get_current()
                url = 'http://%s%s' % (site.domain, self.get_absolute_url())
                tweet = post_to_twitter(url, self.title, self.tags)
                if tweet:
                    self.tweet_url = tweet
                    super(Post, self).save()
                    
                ping_google()
            except:
                pass
                
class Category(models.Model):
    name = models.CharField(_('Nom'), max_length=150, blank=False, null=False)
    description = models.TextField(null=True, blank=True)
    slug = models.SlugField(_('URL'), unique=True, null=True, blank=True)
    posts_number = models.PositiveSmallIntegerField(_('Nombre d\'articles'), default=0)
    
    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('view_cat', (self.slug,))
        
class Vote(models.Model):
    post = models.ForeignKey(Post, blank=False, null=False)
    user = models.ForeignKey(User, null=True, blank=True, verbose_name=_('Auteur'))
    ip = models.IPAddressField(_(u'Adresse IP'), blank=False, null=False)
    date = models.DateTimeField(auto_now=True)
    
class SubmitPost(ModelForm):
    CHOICE_STATUS = (
        (2,  _(u'Proposé')),
        (1,  _('Brouillon')),
    )
    status = forms.IntegerField(initial=1, widget=forms.Select(choices=CHOICE_STATUS))
    
    class Meta:
        model = Post
        fields = ('title', 'category', 'tags', 'head', 'body')

comment_was_posted.connect(check_comments_akismet, dispatch_uid='comments.moderate_comment')
comment_was_posted.connect(parse_comments_markdown, dispatch_uid='comments.post_comment')
post_save.connect(when_comment_was_posted, sender=ThreadedComment, dispatch_uid='comments.post_comment')
post_delete.connect(when_comment_was_posted, sender=ThreadedComment, dispatch_uid='comments.post_comment')
post_save.connect(when_post_was_saved, sender=Post, dispatch_uid='posts.post_post')
post_delete.connect(when_post_was_saved, sender=Post, dispatch_uid='posts.post_post')