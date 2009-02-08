def join(parent, child):
    return parent.rstrip("/") + "/" + child.lstrip("/")
    
def fixslash(url, relative=True):
    url = url.lstrip("/").rstrip("/")
    if relative:
        url = "/" + url
    return url