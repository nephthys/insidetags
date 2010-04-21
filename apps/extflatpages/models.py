#-*- encoding: utf-8 -*-

from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
from django.contrib.flatpages.models import FlatPage
from django.utils.translation import ugettext as _

class ExtendPage(models.Model):
    flatpage = models.OneToOneField(FlatPage, primary_key=True)
    keywords = models.CharField(_(u'Mots clés'), max_length=255, blank=True, null=True)
    description = models.TextField(_('Description de la page'), blank=True, null=True)
    content_html = models.TextField(editable=False, blank=True, null=True)
    active = models.BooleanField(_('Page active'), default=False)
    created_at = models.DateTimeField(_(u'Date de création'), auto_now_add=True)
    updated_at = models.DateTimeField(_(u'Dernière modification'), auto_now=True)
    
    def __unicode__(self):
        return self.flatpage.title
        
    def save(self):
        import markdown
        self.content_html = markdown.markdown(self.flatpage.content, \
            ['extra', 'codehilite(force_linenos=True)', 'headerid(level=3)'], safe_mode='remove')
        super(ExtendPage, self).save()
        
def always_save_extendpage(sender, instance, **kwargs):
    try:
        extend = ExtendPage.objects.get(flatpage__exact=instance)
        extend.save() 
    except ExtendPage.DoesNotExist:
        return ''
        
post_save.connect(always_save_extendpage, sender=FlatPage)