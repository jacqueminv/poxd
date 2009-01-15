import re
from django.conf import settings

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
    

class PyContentProcessor:
    
    @staticmethod
    def process(page):
        text = get_context_text(page)
        page_context = {}
        source_code = "page_context.update(" + text + ")"
        from py.code import Source
        source = Source(source_code)
        exec source.compile()
        settings.CONTEXT['page'] = page_context
        return page
        
class YAMLContentProcessor:
    
    @staticmethod
    def process(page):
        text = get_context_text(page)
        import yaml
        context = yaml.load(text)
        if not context:
            context = {}
        settings.CONTEXT['page'] = context    
        return page