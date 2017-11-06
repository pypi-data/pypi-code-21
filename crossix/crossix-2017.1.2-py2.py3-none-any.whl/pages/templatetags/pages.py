
import markdown

from django import template
register = template.Library()

from .. import models


@register.inclusion_tag('pages/minipage.html')
def include_page(page_name):
    try:
        page = models.Page.objects.get(name=page_name)
    except models.Page.DoesNotExist:
        return {'html': ''}

    html = markdown.markdown(page.content)
    return {'html': html}
