from django.conf import settings

class CategoryProcessor:
    '''Fetch categories of each blog post and (will) provide them
    to the template engine'''
    category_map = {}

    @staticmethod
    def _buildresource(resource):
        return {'title': resource.title, 'url': resource.full_url}

    @staticmethod
    def process(resource):
        if resource.categories:
            category_map = CategoryProcessor.category_map
            if resource.categories.find(',') > -1 :
                for category in resource.categories.split(',') :
                    cat = category.strip().lower()
                    if len(cat) > 0 :
                        if category_map.has_key(cat) :
                            c = category_map[cat]
                        else:
                            c = []
                        r = CategoryProcessor._buildresource(resource)
                        c.append(r)
                        category_map[cat] = c
            else:
                cat = resource.categories.strip().lower()
                if category_map.has_key(cat) :
                    c = category_map[cat]
                else:
                    c = []
                r = CategoryProcessor._buildresource(resource)
                c.append(r)
                category_map[cat] = c
        settings.CONTEXT['categories'] = CategoryProcessor.category_map

class PassthroughProcessor:

   @staticmethod
   def process(resource):       
	   resource.prerendered = True

