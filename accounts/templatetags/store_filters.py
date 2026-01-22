from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """ضرب قيمة في رقم"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def add(value, arg):
    """جمع قيمة مع رقم"""
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def subtract(value, arg):
    """طرح قيمة من رقم"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def divide(value, arg):
    """قسمة قيمة على رقم"""
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0