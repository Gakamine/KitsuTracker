from django import template
register = template.Library()

@register.filter
def lookup(List, i):
    return List[int(i)]
