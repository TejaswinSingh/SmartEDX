from django import template

register = template.Library()

@register.filter
def normalize_rating(grade, max_grade):
    try:
        return (float(grade) / float(max_grade)) * 10
    except (ValueError, ZeroDivisionError):
        return 0