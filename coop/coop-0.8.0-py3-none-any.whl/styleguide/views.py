from django.shortcuts import render


def styleguide(request, page):
    template = 'styleguide/{}.html'.format(page)

    request.is_preview = False

    return render(request, template)
