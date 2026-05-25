from django import template

register = template.Library()

BLOOD_CSS = {
    'A+': 'blood-a-plus',
    'A-': 'blood-a-minus',
    'B+': 'blood-b-plus',
    'B-': 'blood-b-minus',
    'O+': 'blood-o-plus',
    'O-': 'blood-o-minus',
    'AB+': 'blood-ab-plus',
    'AB-': 'blood-ab-minus',
}


@register.filter
def blood_css(blood_type):
    return BLOOD_CSS.get(str(blood_type), 'blood-a-plus')
