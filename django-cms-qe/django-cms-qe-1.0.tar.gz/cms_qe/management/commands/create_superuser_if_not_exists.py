from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = get_user_model().objects.filter(is_superuser=True).first()
        if user:
            self.stdout.write('The superuser \'{}\' already exists.'.format(user.username))
        else:
            password = 'admin'
            user = get_user_model().objects.create_superuser('admin', 'admin@example.com', password)
            self.stdout.write(
                """A new superuser with the following data was created:
                login:    {}
                email:    {}
                password: {}""".format(user.username, user.email, password)
            )
