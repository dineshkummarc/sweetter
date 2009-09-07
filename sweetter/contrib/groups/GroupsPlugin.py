from django.template.loader import render_to_string
from sweetter.contrib.groups.models import Group

class GroupHooks:
    def __init__(self):
        pass
        
    def sidebar(self, context):
        user = context['user']
        return render_to_string('groupsidebar.html', {
                'groups': Group.objects.filter(users__user=user),
            }, context_instance=context)
    
    def tools(self, context, post):
        return ''
        
    def parse(self, value):
        return value