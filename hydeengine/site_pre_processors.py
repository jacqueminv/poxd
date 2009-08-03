from hydeengine.siteinfo import ContentNode
from django.conf import settings
from hydeengine.file_system import Folder

"""
    PRE PROCESSORS
    
    Can be launched before the parsing of each templates and
    after the loading of site info.
"""

class CategoriesManager:
    """
    Fetch the category(ies) from every post under BLOG_DIR node
    and creates a reference on them in CONTEXT.
    """
    @staticmethod
    def process(folder, params):
        context = settings.CONTEXT
        site = context['site']
        blog_node = site.find_node(Folder(settings.BLOG_DIR))
        categories = {}
        for post in blog_node.walk_pages():
            if hasattr(post, 'categories') and post.categories != None:
                for category in post.categories:
                    if categories.has_key(category) == False:
                        categories[category] = set()
                    categories[category].add(post)
        if context.has_key('blog') == False:
            context['blog'] = {}
        context['blog']['categories'] = categories
                       
