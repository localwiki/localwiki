from django import template
from versionutils.diff.diffutils import diff

register = template.Library()

class DiffNode(template.Node):
    def __init__(self, object1, object2, context_var):
        object1 = template.Variable(object1)
        object2 = template.Variable(object2)
        self.objects = [object1, object2]
        self.context_var = context_var
        
    def render(self, context):
        vars = [o.resolve(context) for o in self.objects]
        context[self.context_var] = diff(*vars)
        return ''
    
@register.tag(name='diff')
def do_diff(parser, token):
    try:
        tag_name, object1, object2, dummy, context_var = token.split_contents()
        if not dummy == 'as':
            raise ValueError()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires four arguments" % token.contents.split()[0]
    return DiffNode(object1, object2, context_var)
