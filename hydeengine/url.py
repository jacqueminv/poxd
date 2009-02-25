def join(parent, child):
    return (parent.rstrip("/") + "/" + child.lstrip("/")).rstrip("/")
    
def fixslash(url, relative=True):
    url = url.strip("/")
    if relative:
        url = "/" + url
    return url
    
def clean_url(url):
    parts = url.rsplit(".", 1)
    if parts[1] == "html":
        return parts[0]
    return url