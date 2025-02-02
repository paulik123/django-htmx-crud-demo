from django import template

register = template.Library()

@register.filter
def render(field):
	if not field:
		return ''
	return field.render()

@register.filter
def render_no_label(field):
	if not field:
		return ''
	return field.render('rcpapp/fields/field_no_label.html')
