from django import template
from django.utils.safestring import mark_safe
register = template.Library()
from django.template.loader import render_to_string

@register.simple_tag
def field_content(field):
    '''Return the content of a field'''
    try:
        return_value = getattr(field.form.instance,field.name)
        if hasattr(return_value,"pk"):
            return(return_value.pk)        
        elif return_value:
            return(return_value)
        else:
            return("")
    except: ## Catches if field does not have attribute
        return("")

@register.simple_tag
def form_model(field):
    '''Return the model name of a field via form object'''
    return(type(field.form.instance).__name__)

@register.simple_tag
def render_form_dict(form_dict):
    '''Used to render separate forms or formsets with ajax_forms
    Usage: {% render_form_dict registrations_table %}

    form_dict may contain the following:
    read_only (iterable)    
    '''

    assert ("form" in form_dict or "formset" in form_dict)
    template = form_dict.pop("template")
    return(render_to_string(template,context=form_dict))

@register.simple_tag
def column_content(form,column):
    return(getattr(form.instance,column))