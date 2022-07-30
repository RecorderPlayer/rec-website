from django import template

register = template.Library()


def split(value):
    return value.split(str('\r\n'))


register.filter('split', split)
