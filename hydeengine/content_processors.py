import re
from django.conf import settings
from file_system import File

def get_context_text(page):
    start = re.compile(r'.*?{%\s*hyde\s*(.*?)(%}|$)')
    end = re.compile(r'(.*?)(%})')
    fin = open(str(page),'r')
    started = False
    text = ''
    matcher = start
    for line in fin:
        match = matcher.match(line)
        if match:
            text = text + match.group(1)
            if started: break
            else:
                matcher = end 
                started = True
        elif started:
            text = text + line
    fin.close()
    return text
    
def add_page_variables(page, vars):
    if not vars: return
    for key, value in vars.iteritems():
        if not hasattr(File, key):
            setattr(File, key, object())
        setattr(page, key, value)
            

class PyContentProcessor:
    
    @staticmethod
    def process(page):
        text = get_context_text(page)
        page_context = {}
        source_code = "page_context.update(" + text + ")"
        from py.code import Source
        source = Source(source_code)
        exec source.compile()
        add_page_variables(page, page_context)
        return page
        
class YAMLContentProcessor:
    
    @staticmethod
    def process(page):
        text = get_context_text(page)
        import yaml
        context = yaml.load(text)
        if not context:
            context = {}
        add_page_variables(page, context) 
        return page