from django import template
from django.core.urlresolvers import resolve
import datetime, calendar

register = template.Library()

@register.filter(name='month_name')
def month_name(value):
	month_num = int(value)
	name = calendar.month_name[month_num]
	if name:
		return name
	else:
		return value

@register.filter(name='format_phone')
def format_phone(value):
	phone_string = str(value)
	try:
		if (phone_string[0] == '1'):
			phone_string = phone_string[1:]
		return '{0}-{1}-{2}'.format(phone_string[:3], phone_string[3:6], phone_string[6:10])
	except:
		return value

# usage: {% navactive request 'comma-separated-list,of-url-pattern-names,to-match'}
@register.simple_tag
def navactive(request, urls):
    if resolve(request.path).url_name in [url.strip() for url in urls.split(',')]:
        return "active"
    return ''

# usage: {% unclaimed_form forms_dict form_id %}
@register.simple_tag
def unclaimed_form(forms_dict, form_id):
	form = forms_dict[str(form_id)]
	return str(append_attr(form['guide'], 'class:select2')) + str(form['tour_id'])

# From Django Widget Tweaks

def _process_field_attributes(field, attr, process):

    # split attribute name and value from 'attr:value' string
    params = attr.split(':', 1)
    attribute = params[0]
    value = params[1] if len(params) == 2 else ''

    # decorate field.as_widget method with updated attributes
    old_as_widget = field.as_widget

    def as_widget(self, widget=None, attrs=None, only_initial=False):
        attrs = attrs or {}
        process(widget or self.field.widget, attrs, attribute, value)
        return old_as_widget(widget, attrs, only_initial)

    bound_method = type(old_as_widget)
    try:
        field.as_widget = bound_method(as_widget, field, field.__class__)
    except TypeError:  # python 3
        field.as_widget = bound_method(as_widget, field)
    return field

def append_attr(field, attr):
  def process(widget, attrs, attribute, value):
      if attrs.get(attribute):
          attrs[attribute] += ' ' + value
      elif widget.attrs.get(attribute):
          attrs[attribute] = widget.attrs[attribute] + ' ' + value
      else:
          attrs[attribute] = value
  return _process_field_attributes(field, attr, process)




@register.filter
def get_range( value ):
  """
    Filter - returns a list containing range made from given value
    Usage (in template):

    <ul>{% for i in 3|get_range %}
      <li>{{ i }}. Do something</li>
    {% endfor %}</ul>

    Results with the HTML:
    <ul>
      <li>0. Do something</li>
      <li>1. Do something</li>
      <li>2. Do something</li>
    </ul>

    Instead of 3 one may use the variable set in the views
  """
  return range( value )

  