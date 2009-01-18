from django import template
from django.template import Library
import re

register = Library()

class HydeContextNode(template.Node):
    def __init__(self): pass
    
    def render(self, context):
        return ""
        
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

@register.filter
def remove_date_prefix(slug, sep="-"):
    expr = sep.join([r"\d{2,4}"]*3 + ["(.*)"]) 
    match = re.match(expr, slug)
    if not match:
        return slug
    else:
        return match.group(0)

@register.filter
def unslugify(slug):
    words = slug.replace("_", " ").replace("-", " ").replace(".", "").split()
    return ' '.join(map(lambda str: str.capitalize(), words))
