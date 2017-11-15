import os
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from feincms.module.medialibrary.models import Category, MediaFile


def import_path(path, parent_category=None):
    category_name = os.path.basename(path)
    if not category_name:
        path = os.path.dirname(path)
        category_name = os.path.basename(path)

    if parent_category and parent_category.parent:
        parent_category = parent_category.parent

    try:
        category = Category.objects.filter(title=category_name, parent=parent_category)[0]
    except IndexError:
        category = Category(title=category_name, parent=parent_category)
        category.save()

    for item in os.listdir(path):
        subpath = os.path.join(path, item)
        if os.path.isdir(subpath):
            import_path(subpath, parent_category=category)
        elif item.startswith('.'):
            # ignore . files
            pass
        else:
            content = ContentFile(open(subpath).read())
            media_file = MediaFile()
            media_file.save()
            media_file.categories.add(category)
            media_file.file.save(media_file.file.storage.get_valid_name(item), content)



class Command(BaseCommand):
    help = 'Recursively import files into the medialibrary and add them to a category based on their folder name.'
    args = '<folder folder ...>'

    def handle(self, *args, **options):
        for folder in args:
            import_path(folder)

