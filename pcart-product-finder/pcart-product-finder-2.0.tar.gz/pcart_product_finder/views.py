from django.shortcuts import render, get_object_or_404
from .forms import ProductFinderForm
from .models import ObjectVariant


def product_finder_form(request, collection_slug):
    from pcart_catalog.models import Collection
    # if not request.is_ajax():
    #     return HttpResponseForbidden('Ajax request required')

    collection = get_object_or_404(Collection, slug=collection_slug, published=True)
    is_valid = False
    redirect_url = ''
    target = request.GET.get('target', request.POST.get('target', ''))
    if request.method == 'POST':
        form = ProductFinderForm(request.POST, collection=collection)
        if form.is_valid() and \
                        request.POST.get('vendor') and \
                        request.POST.get('model') and \
                        request.POST.get('year') and \
                        request.POST.get('variant'):
            is_valid = True
            object_variant = get_object_or_404(ObjectVariant, pk=form.cleaned_data['variant'])
            redirect_url = '%s%s/' % (
                collection.get_absolute_url(),
                object_variant.slug,
            )
    else:
        form = ProductFinderForm(collection=collection)
    context = {
        'collection': collection,
        'form': form,
        'is_valid': is_valid,
        'redirect_url': redirect_url,
        'target': target,
    }
    return render(request, 'productfinder/form.html', context)
