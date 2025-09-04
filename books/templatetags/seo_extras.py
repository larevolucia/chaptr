""" SEO TAGS """
from django import template
from books.utils import meta_description_from_volume  # or paste function here

register = template.Library()


@register.filter
def meta_desc(volume, max_len=155):
    """ Create meta description """
    try:
        max_len = int(max_len)
    except Exception:
        max_len = 155
    return meta_description_from_volume(volume, max_len)
