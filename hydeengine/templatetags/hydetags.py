from django import template
from django.template import Template
from django.template.loader import render_to_string
from django.template.defaultfilters import truncatewords_html
from django.template import Library
from hydeengine.file_system import *
import re
import time

register = Library()

class HydeContextNode(template.Node):
    def __init__(self): pass
    
    def render(self, context):
        return ""
@register.tag(name="hyde")
def hyde_context(parser, token):
    return HydeContextNode()


class LatestExcerptNode(template.Node):
    def __init__(self, path, words = 200):
        self.path = path
        self.words = words
        
    def render(self, context):
        sitemap_node = None
        if not self.words == 200:
            self.words = self.words.render(context)
        self.path = self.path.render(context).strip('"')
        sitemap_node = context["site"].get_node_for(Folder(self.path))
        if not sitemap_node:
           sitemap_node = context["site"]
        t = lambda a: time.strptime(a.created, settings.DATETIME_FORMAT)
        print sitemap_node.pages
        page = reduce(lambda a,b:(t(a),t(b))[t(b)>t(a)], sitemap_node.pages)
        excerpt_page = page.parent.child("_excerpt_" + page.name)
        rendered = None
        print excerpt_page
        if File(excerpt_page).exists:
            rendered = render_to_string(excerpt_page, context)
            rendered =  truncatewords_html(rendered, self.words)
        return rendered
        
        
@register.tag(name="latest_excerpt")
def latest_excerpt(parser, token):
    tokens = token.split_contents()
    path = None
    words = 200
    if len(tokens) > 1:
        path = Template(tokens[1])
    if len(tokens) > 2:
        words = Template(tokens[2])
    return LatestExcerptNode(path, words)

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
