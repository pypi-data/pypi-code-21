# coding: utf-8
from __future__ import unicode_literals

import logging
import traceback

from django.core.mail import mail_managers
from django.core.management import BaseCommand

from django_boxberry.models import Parsel


logging.basicConfig(level=logging.DEBUG)


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Start'))

        # Конечные статусы, которые больше не нужно обновлять
        # 7 - Выдано, 12 - Возвращено в ИМ
        end_statuses = (7, 12)
        errors = {}

        parsels_to_update = Parsel.objects.all().exclude(current_status__status_id__in=end_statuses,
                                                         track__isnull=False, delivery_act_id__isnull=False)
        self.stdout.write(self.style.NOTICE('Parsels to update count: {}'.format(parsels_to_update.count())))

        for parsel in Parsel.objects.all().exclude(current_status__status_id__in=end_statuses):
            self.stdout.write(self.style.NOTICE('Updating parsel: {}'.format(parsel)))
            try:
                parsel.update_status()
                self.stdout.write(self.style.SUCCESS('\tSuccess'))
            except Exception as e:
                logging.exception(e)
                errors[parsel.id] = traceback.format_exc()
                self.stdout.write(self.style.WARNING(traceback.format_exc()))

        if errors:
            msg = '\n\n'.join(['Id посылки: {}. Ошибка:\n{}'.format(parsel_id, err) for parsel_id, err in errors.items()])
            mail_managers(subject='Ошибки при проверки статуса', message=msg, fail_silently=True)

        self.stdout.write(self.style.NOTICE('Done'))
