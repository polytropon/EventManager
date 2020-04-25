from django.template import engines, TemplateSyntaxError
from django.template.loader import render_to_string

def simple_render(template_string,context):
    '''String template and context in, string out.
    '''
    engine = engines.all()[0]
    template = engine.from_string(template_string)
    return(template.render(context))