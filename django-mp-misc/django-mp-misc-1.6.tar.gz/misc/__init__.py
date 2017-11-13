
__version__ = '1.6'

__all__ = ['handler400', 'handler403', 'handler404', 'handler500']


handler404 = 'misc.views.page_not_found'
handler500 = 'misc.views.server_error'
handler403 = 'misc.views.permission_denied'
handler400 = 'misc.views.bad_request'
