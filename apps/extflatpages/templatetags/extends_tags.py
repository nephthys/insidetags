from django import template
from django.core.cache import cache
from django.utils.translation import ungettext, ugettext as _
from insidetags.apps.extflatpages.models import ExtendPage

register = template.Library()

class ExtendPageNode(template.Node):                                                                                                                                                                                                                 
    def __init__(self, flatpage_id, context_name):
        self.flatpage_id = template.Variable(flatpage_id)
        self.context_name = context_name
        
    def render(self, context):
        try:
            real_flatpage_id = self.flatpage_id.resolve(context)
            data = cache.get('static_flatpage_%d' % real_flatpage_id)
            if data is None:
                data = ExtendPage.objects.get(flatpage__id__exact=real_flatpage_id)
                cache.set('static_flatpage_%d' % real_flatpage_id, data)
            context[self.context_name] = data
            return ''
        except:
            return ''
                                                                                                                                                                                                                                    
@register.tag                                                                                                                                                                                                                                
def extend_flatpage(parser, token):                                                                                                                                                                                                       
    """usage : {% extend_flatpage flatpage.id as more_flatpage %}"""                                                                                                                                                                                       
    bits = token.split_contents()
    if len(bits) != 4:                                                                                                                                                                                                                       
        raise template.TemplateSyntaxError, "extend_flatpage tag takes exactly three arguments"                                                                                                                                                    
    if bits[2] != 'as':                                                                                                                                                                                                                      
        raise template.TemplateSyntaxError, "second argument to extend_flatpage tag must be 'as'"                                                                                                                                                  
    return ExtendPageNode(bits[1], bits[3])