from django import template
from django.utils.safestring import mark_safe
register = template.Library()
from django.template.loader import render_to_string

@register.filter
def editable_table_header(field):
    if field.verbose_name:
        name = field.verbose_name
    else:
        name = field.name

    return(mark_safe(f"<th>{name}</th>"))

@register.simple_tag
def editable_cell(field,entry):
    '''Return the input element for a cell in the table
    or return the cell value if not editable'''
    value = getattr(entry,field.name)

    ## TODO: Clean up disorderly code!
    if not value:
        value = ""

    if hasattr(field,"editable"):
        if not field.editable:
            classes = []
            return(value)
        else:
            classes = ["editable"]

    if hasattr(field,"classes"):
        classes = classes.extend(field.classes)
    class_string = 'class = "' + " ".join(classes) + '"'

    if type(field).__name__ == "ForeignKey":
        pass
            
    ## Options for text field
    if hasattr(field,"options"):

        return(render_to_string('crm/editable_table/options.html',
        {"field":field,"value":value,
        "options":field.options}))
    # elif type(field).__name__ == "TextField" or (type(field).__name__ == "CharField" and field.max_length >100):
    #     return(mark_safe(f'''<textarea {class_string} rows="8" cols="50" data-start-value="{value}" value ="{value}">{value}</textarea>
    #     '''))
    # elif not hasattr(field,"hide") or not field.hide:
    #     return(value)
    else:
        input_type = "text"
        if type(field).__name__ == "Date":
            input_type = "datetime"
        return(mark_safe(f'''
        <input {class_string} data-start-value="{value}" data-column-name="{field.name}" type="{input_type}" value="{value}">
        '''))
