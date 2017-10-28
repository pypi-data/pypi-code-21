from django_hosts import reverse as reverse_host


def reverse(viewname, *args, **kwargs):
    kwargs['host'] = 'api'
    return reverse_host(viewname, *args, **kwargs)
