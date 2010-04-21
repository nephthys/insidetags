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
from django.db.models.signals import post_save
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify
from insidetags.apps.middleware import threadlocals

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    slug = models.SlugField(_('URL'), unique=True, null=True, blank=True)

    biography = models.TextField(_('Biographie'), null=True, blank=True)
    biography_html = models.TextField(editable=False, blank=True, null=True)
    
    avatar = models.URLField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    
    receive_newsletter = models.BooleanField(_(u'Recevoir la newsletter'), default=False)
    show_email = models.BooleanField(_(u'Autoriser l\'affichage de son email'), default=False)
    
    nb_login = models.PositiveSmallIntegerField(_('Nombre de connexions'), default=0)
    
    def save(self, force_insert=False, force_update=False):
        import markdown
        if not self.slug:
            self.slug = slugify(self.user.username)
        if self.biography:
            self.biography_html = markdown.markdown(self.biography, \
                ['extra', 'codehilite', 'headerid(level=3)'], safe_mode='remove')
        super(UserProfile, self).save()
        
class ConfirmAccountForm(ModelForm):
    username = forms.CharField(label=_('Pseudo'), required=True)
    email = forms.EmailField(label=_('Adresse email'), required=True, help_text=_(u'Ne sera jamais revendue à des tiers'))
    
    class Meta:
        model = UserProfile
        fields = ('username', 'email', 'receive_newsletter',)
          
    def clean_username(self):
        username = self.cleaned_data.get('username', '')
        try:
            current_user = threadlocals.get_current_user()
            user = User.objects.get(username=username)
            if user.pk != current_user.pk:
                raise forms.ValidationError(_(u'Ce pseudo est déjà utilisé.'))
        except User.DoesNotExist:
            pass
        return username
        
    def clean_receive_newsletter(self):
        receive_newsletter = self.cleaned_data.get('receive_newsletter', '')
        email = self.cleaned_data.get('email', '')
        if receive_newsletter and not email:
            raise forms.ValidationError(_(u'Vous devez indiquer votre adresse email pour recevoir la newsletter.'))
        return receive_newsletter
        
def user_post_save(sender, instance, **kwargs):
    profile, new = UserProfile.objects.get_or_create(user=instance)
    
post_save.connect(user_post_save, sender=User)