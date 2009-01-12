from django import template
from django.template import Library

register = Library()

class HydeContextNode(template.Node):
    def __init__(self): 
        print value
    
    def render(self, context):
        return self.value
        
@register.tag(name="hyde")
def hyde_context(parser, token):
    return HydeContextNode()

@register.filter
def value_for_key(d, key):
    if not d:
        return ""
    if not d.has_key(key):
        return ""
    return d[key]
