from django import template
from django.conf import settings
from django.template import Template
from django.template.loader import render_to_string
from django.template.defaultfilters import truncatewords_html
from django.template import Library
from hydeengine.file_system import *
import re
from datetime import datetime

excerpt_start = "<!-- Hyde::Excerpt::Begin -->\n"
excerpt_end = "<!-- Hyde::Excerpt::End -->\n"

register = Library()

class HydeContextNode(template.Node):
    def __init__(self): pass
    
    def render(self, context):
        return ""
@register.tag(name="hyde")
def hyde_context(parser, token):
    return HydeContextNode()

@register.tag(name="excerpt")
def excerpt(parser, token):
    nodelist = parser.parse(('endexcerpt',))
    parser.delete_first_token()
    return ExcerptNode(nodelist)

class ExcerptNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        rendered_string = self.nodelist.render(context)
        return excerpt_start + rendered_string + excerpt_end


class LatestExcerptNode(template.Node):
    def __init__(self, path, words = 50):
        self.path = path
        self.words = words
        
    def render(self, context):
        sitemap_node = None
        if not self.words == 50:
            self.words = self.words.render(context)
        self.path = self.path.render(context).strip('"')
        sitemap_node = context["site"].get_node_for(Folder(self.path))
        if not sitemap_node:
           sitemap_node = context["site"]
        def later(page1, page2):
            page2_created = page1_created = datetime.strptime("2000-01-01 00:00", settings.DATETIME_FORMAT)
            if hasattr(page1, "created") and page1.created:
                page1_created = page1.created
            if hasattr(page2, "created") and page2.created:
                page2_created = page2.created                
            return (page1, page2)[page2_created > page1_created]
            
        page = reduce(later, sitemap_node.walk_pages())
        rendered = None
        rendered = render_to_string(str(page), context)
        start = rendered.find(excerpt_start)
        if not start == -1:
            context["latest_excerpt_url"] = page.url
            context["latest_excerpt_title"] = page.title
            start = start + len(excerpt_start)
            end = rendered.find(excerpt_end, start)
            return truncatewords_html(rendered[start:end], self.words)
        else:
            return ""
        
@register.tag(name="latest_excerpt")
def latest_excerpt(parser, token):
    tokens = token.split_contents()
    path = None
    words = 50
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
