from django import template


register = template.Library()


@register.filter()
def remove(value, word):
    """Removes the unwated text from the definition"""
    return value.replace(word, "")
