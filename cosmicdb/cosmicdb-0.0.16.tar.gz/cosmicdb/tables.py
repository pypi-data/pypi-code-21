import django_tables2 as tables
from django.utils.safestring import mark_safe


row_onclick = "if(window.hasOwnProperty('goTo')){if(typeof window.goTo === 'function'){goTo(this);}}"

class MessageTable(tables.Table):
    read = tables.Column(attrs={'th': {'class': 'read_column',}}, order_by='read')
    short_message = tables.Column(verbose_name="Message", order_by='message')
    created_at = tables.Column(verbose_name="Received At")
    def render_read(self, record):
        html = '<i class="fa fa-envelope"></i>'
        if record.read:
            html = '<i class="fa fa-envelope-o"></i>'
        return mark_safe(html)
    def render_short_message(self, record, value):
        html = record.image_tag() + ' ' + value
        return mark_safe(html)
    class Meta:
        empty_text = "No messages"
        row_attrs = {
            'data-id': lambda record: record.pk,
            'onclick': row_onclick,
            'class': 'table-row',
        }


class NotificationTable(tables.Table):
    read = tables.Column(attrs={'th': {'class': 'read_column',}}, order_by='read')
    short_notification = tables.Column(verbose_name="Message", order_by='notification')
    created_at = tables.Column(verbose_name="Received At")
    def render_read(self, record):
        html = '<i class="fa fa-envelope"></i>'
        if record.read:
            html = '<i class="fa fa-envelope-o"></i>'
        return mark_safe(html)
    def render_short_notification(self, record, value):
        icon = ''
        if record.icon_class:
            icon = '<i class="%s"></i>' % record.icon_class
        html = icon + value
        return mark_safe(html)
    class Meta:
        empty_text = "No notifications"
        row_attrs = {
            'data-id': lambda record: record.pk,
            'onclick': row_onclick,
            'class': 'table-row',
        }
