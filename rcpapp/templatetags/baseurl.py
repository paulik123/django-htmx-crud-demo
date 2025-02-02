from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def if_active(context, namespace, namespace2=None):
    if not namespace2:
        splitted = context['request'].path.split("/")
        if len(splitted) > 1 and splitted[1] == namespace:
            return 'active'
        return ''
    
    splitted = context['request'].path.split("/")
    if len(splitted) > 2 and splitted[1] == namespace and splitted[2] == namespace2:
        return 'active'
    return ''
