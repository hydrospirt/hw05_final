from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={'class': css})


@register.filter
def uglify(field):
    i = 0
    text = ""
    for letter in field:
        i += 1
        if i % 2 == 0:
            text += letter.upper()
        else:
            text += letter.lower()
    return text
