from django.http import HttpResponse
from insidetags.functions import *

class SaveNextPage(object):
    def process_request(self, request):
        if len(request.GET.get('redirect_to', '')) > 0:
            request.session['_next_page'] = url_decode(request.GET.get('redirect_to', ''))