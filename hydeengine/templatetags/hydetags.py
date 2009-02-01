from django import template
from django.conf import settings
from django.template import Template
from django.template.loader import render_to_string
from django.template.defaultfilters import truncatewords_html
from django.template import Library
from hydeengine.file_system import Folder
import re
from datetime import datetime
from datetime import timedelta

marker_start = "<!-- Hyde::%s::Begin -->\n"
marker_end = "<!-- Hyde::%s::End -->\n"

register = Library()

class HydeContextNode(template.Node):
    def __init__(self): 
        pass
    
    def render(self, context):
        return ""
        
@register.tag(name="hyde")
def hyde_context(parser, token):
    return HydeContextNode()

@register.tag(name="excerpt")
def excerpt(parser, token):
    nodelist = parser.parse(('endexcerpt',))
    parser.delete_first_token()
    return BracketNode("Excerpt", nodelist)
    
@register.tag(name="article")
def excerpt(parser, token):
    nodelist = parser.parse(('endarticle',))
    parser.delete_first_token()
    return BracketNode("Article", nodelist)

class BracketNode(template.Node):
    def __init__(self, marker, nodelist):
        self.nodelist = nodelist
        self.marker = marker

    def render(self, context):
        rendered_string = self.nodelist.render(context)
        return marker_start % self.marker +\
                rendered_string + \
                marker_end % self.marker


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
            return (page1, page2)[page2.created > page1.created]
        page = reduce(later, sitemap_node.walk_pages())
        rendered = None
        rendered = render_to_string(str(page), context)
        excerpt_start = marker_start % "Excerpt"
        excerpt_end = marker_end % "Excerpt"
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

@register.tag(name="render_excerpt")    
def render_excerpt(parser, token):
    tokens = token.split_contents()
    path = None
    words = 50
    if len(tokens) > 1:
        path = parser.compile_filter(tokens[1])
    if len(tokens) > 2:
        words = Template(tokens[2])
    return RenderExcerptNode(path, words)

@register.tag(name="render_article")    
def render_excerpt(parser, token):
    tokens = token.split_contents()
    path = None
    if len(tokens) > 1:
        path = parser.compile_filter(tokens[1])
    return RenderArticleNode(path)
    
class RenderExcerptNode(template.Node):
    def __init__(self, page, words = 50):
        self.page = page
        self.words = words

    def render(self, context):
        if not self.words == 50:
            self.words = self.words.render(context)
        page = self.page.resolve(context)
        context["excerpt_url"] = page.url
        context["excerpt_title"] = page.title
        rendered = get_bracketed_content(context, page, "Excerpt")
        return truncatewords_html(rendered, self.words)
        

class RenderArticleNode(template.Node):
    def __init__(self, page):
        self.page = page

    def render(self, context):
        page = self.page.resolve(context)
        return get_bracketed_content(context, page, "Article")

            
def get_bracketed_content(context, page, marker):
        rendered = None
        original_page = context['page']
        context['page'] = page
        rendered = render_to_string(str(page), context)
        context['page'] = original_page
        bracket_start = marker_start % marker
        bracket_end = marker_end % marker
        start = rendered.find(bracket_start)
        if not start == -1:
            start = start + len(bracket_start)
            end = rendered.find(bracket_end, start)
            return rendered[start:end]
        return ""


@register.filter
def value_for_key(dictionary, key):
    if not dictionary:        
        return ""
    if not dictionary.has_key(key):        
        return ""
    value = dictionary[key]
    return value

@register.filter
def xmldatetime(dt):
    if not dt:
        dt = datetime.now()
    zprefix = "Z"
    tz = dt.strftime("%z")
    if tz:
        zprefix = tz[:3] + ":" + tz[3:]
    return dt.strftime("%Y-%m-%dT%H:%M:%S") + zprefix

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
    words = slug.replace("_", " ").\
                    replace("-", " ").\
                        replace(".", "").split()
                        
    return ' '.join(map(lambda str: str.capitalize(), words))
