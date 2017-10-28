
def reverse_host(view_name, **kwargs):
    if 'host' in kwargs:
        from django_hosts import reverse
    else:
        from django.urls import reverse

    return reverse(view_name, **kwargs)
