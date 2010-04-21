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
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils.translation import ugettext as _

class ContactForm(forms.Form):
    pseudo = forms.CharField(label=_('Nom'), required=False)
    mail = forms.EmailField(label=_('Email'))
    objet  = forms.CharField(label=_('Titre'), required=False)
    message = forms.CharField(label=_('Content'), widget=forms.Textarea)

    def send(self, mails=[]):
        if self.is_valid():
            if not mails:
                mails = [a[1] for a in settings.MANAGERS]
            # Codage de l'envoi
            subject = u'%s' % (self.cleaned_data['objet'])
            msg = EmailMessage(subject, self.cleaned_data['message'], self.cleaned_data['mail'], mails)
            try:
                msg.send()
            except:
                return False

            return True

        return False