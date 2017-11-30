# -*- coding: utf-8 -*-
from datetime import timedelta
from django.db import models
from repositories import custom_models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.utils import timezone


INTEGRATION_STATUS = [
    (u'WAIT', u'Aguardando envio para {}'),
    (u'QUEUE', u'Em fila para {}'),
    (u'RETRY', u'Nova tentativa para {}'),
    (u'SUCCESS', u'Integrado com sucesso para {}'),
    (u'FAIL', u'{} não aceitou os dados'),
    (u'ERROR', u'Ocorreu um erro no envio'),
    (u'NO CHANGES', u'Nenhum dado foi alterado')
]

INTEGRATION_ENVIRONMENT = [
    (0, u'Testes'),
    (1, u'Produção')
]


class Integration(models.Model):

    id = custom_models.BigAutoField(
        db_column='integration_id', primary_key=True)
    name = models.CharField(
        db_column='integration_name',
        max_length=255,
        verbose_name='nome')
    slug = models.SlugField(
        db_column='integration_slug',
        unique=True,
        editable=False, null=True, blank=True)
    sandbox_token = models.CharField(
        db_column='integration_sandbox_token',
        max_length=255,
        verbose_name='token teste',
        null=True, blank=True)
    sandbox_url = models.URLField(
        db_column='integration_sandbox_url',
        verbose_name='URL do sandbox',
        null=True, blank=True
    )
    production_token = models.CharField(
        db_column='integration_production_token',
        max_length=255,
        verbose_name=u'Token de Produção',
        null=True, blank=True)
    production_url = models.URLField(
        db_column='integration_production_url',
        verbose_name=u'URL de Produção',
        null=True, blank=True
    )
    active = models.BooleanField(
        db_column='integration_active',
        default=False)

    all_products = models.BooleanField(
        db_column='integration_all_products',
        default=True)

    class Meta:
        db_table = u"integration\".\"tb_integration"
        verbose_name = u'integration'
        verbose_name_plural = u'Integracoes'

    def __unicode__(self):
        return "{}".format(self.name)


class AccountIntegration(models.Model):

    id = custom_models.BigAutoField(
        db_column='account_integration_id',
        primary_key=True)
    account_id = models.BigIntegerField(
        db_column='account_integration_account_id'
    )
    contract_id = models.BigIntegerField(
        db_column='account_integration_contract_id'
    )
    integration = models.ForeignKey(
        'integration.Integration',
        db_column='integration_id',
        related_name='integration_account_integration',
        on_delete=models.CASCADE
    )
    active = models.BooleanField(
        db_column='account_integration_active',
        default=False)
    client_id = models.CharField(
        db_column='account_integration_client_id',
        max_length=255,
        null=True, blank=True)
    secret_id = models.CharField(
        db_column='account_integration_secret_id',
        max_length=255,
        null=True, blank=True)
    token = models.CharField(
        db_column='account_integration_token',
        max_length=255,
        null=True, blank=True)
    url = models.URLField(
        db_column='account_integration_url',
        verbose_name='URL de acesso',
        null=True, blank=True
    )
    environment = models.IntegerField(
        db_column='account_integration_environment',
        choices=INTEGRATION_ENVIRONMENT,
        default=1
    )

    class Meta:
        db_table = u"integration\".\"tb_account_integration"
        verbose_name = u'Account Integration'
        verbose_name_plural = u'Account Integrations'
        unique_together = ('account_id', 'integration')

    def __unicode__(self):
        return "{}/{}".format(self.account_id, self.integration)


class ModelIntegration(models.Model):

    id = custom_models.BigAutoField(
        db_column='model_integration_id',
        primary_key=True)
    account_id = models.BigIntegerField(
        db_column='model_integration_account_id')
    model_selected = models.CharField(
        db_column='model_integration_model_selected',
        max_length=50
    )
    model_selected_id = models.BigIntegerField(
        db_column='model_integration_model_selected_id',
    )
    integration = models.ForeignKey(
        'integration.Integration',
        db_column='integration_id',
        related_name='integration_model_integration',
        on_delete=models.CASCADE
    )
    start_date = models.DateTimeField(
        db_column='model_integration_start_date',
        null=True,
        blank=True,
        auto_now_add=True)
    end_date = models.DateTimeField(
        db_column='model_integration_end_date', null=True, blank=True)
    block_integration = models.BooleanField(
        db_column='model_integration_block_integration',
        default=False)
    removed = models.BooleanField(
        db_column='model_integration_removed',
        default=False)
    external_id = models.BigIntegerField(
        db_column='model_integration_external_id',
        null=True, blank=True
    )
    external_sku_id = models.BigIntegerField(
        db_column='model_integration_external_sku_id',
        null=True, blank=True
    )

    class Meta:
        db_table = u"integration\".\"tb_model_integration"
        verbose_name = u'Model Integration'
        verbose_name_plural = u'Model Integrations'
        unique_together = (
            'model_selected',
            'model_selected_id',
            'integration',
            'account_id')

    def __unicode__(self):
        return "{}/{}".format(self.model_selected_id, self.integration)

    def active(self):
        result = True
        if not AccountIntegration.objects.filter(
                account_id=self.account_id,
                integration=self.integration,
                active=True
        ).exists():
            result = False
        if self.block_integration or self.removed:
            result = False
        return result

    def get_object(self, account_id, model):
        default_manager = model._default_manager
        return default_manager.get(
            conta_id=account_id,
            pk=self.model_selected_id)


class IntegrationHistory(models.Model):

    id = custom_models.BigAutoField(
        db_column='integration_history_id',
        primary_key=True)
    account_id = models.BigIntegerField(
        db_column='integration_history_account_id')
    model_selected = models.CharField(
        db_column='integration_history_model_selected',
        max_length=50
    )
    model_selected_id = models.BigIntegerField(
        db_column='integration_history_model_selected_id',
    )
    integration = models.ForeignKey(
        'integration.Integration',
        db_column='integration_id',
        related_name='integration_integration_history',
        on_delete=models.CASCADE
    )
    operation_id = models.BigIntegerField(
        db_column='integration_history_operation_id', null=True, blank=True)
    start_date = models.DateTimeField(
        db_column='integration_history_start_date',
        auto_now_add=True
    )
    end_date = models.DateTimeField(
        db_column='integration_history_end_date',
        null=True,
        blank=True)
    status = models.CharField(
        db_column='integration_history_status',
        choices=INTEGRATION_STATUS,
        default="WAIT",
        max_length=35
    )
    message_body = models.TextField(
        db_column='integration_history_message_body',
        null=True,
        blank=True)
    duration = models.DurationField(
        db_column='integration_history_duration',
        null=True,
        blank=True)
    contract_id = models.BigIntegerField(
        db_column='integration_history_contract_id',
        null=True, blank=True
    )
    response = models.TextField(
        db_column='integration_history_web_response',
        null=True, blank=True
    )

    class Meta:
        db_table = u"integration\".\"tb_integration_history"
        verbose_name = u'Integration History'
        verbose_name_plural = u'Integrations History'

    def __unicode__(self):
        return "{}/{} {}".format(self.id,
                                 self.integration,
                                 self.start_date.isoformat())


class Webhook(models.Model):

    integration = models.ForeignKey(
        'integration.Integration',
        db_column='integration_id',
        related_name='integration_webhook',
        on_delete=models.CASCADE
    )
    model_selected = models.CharField(
        db_column='webhoook_model_selected',
        max_length=50
    )
    external_id = models.BigIntegerField(
        db_column='webhook_external_id'
    )
    account_id = models.BigIntegerField(
        db_column='webhook_account_id')
    contract_id = models.BigIntegerField(
        db_column='webhook_contract_id',
    )
    message_body = models.TextField(
        db_column='webhook_message_body',
        null=True,
        blank=True
    )
    response = models.TextField(
        db_column='webhook_web_response',
        null=True, blank=True
    )
    status = models.CharField(
        db_column='webhook_status',
        choices=INTEGRATION_STATUS,
        default="WAIT",
        max_length=35
    )
    access_key = custom_models.UUIDField(db_column="webhook_access_key")
    order_id = models.BigIntegerField(
        db_column='webhook_order_id',
        null=True,
        blank=True
    )
    marketplace = models.CharField(
        db_column='webhook_marketplace',
        max_length=60,
        null=True,
        blank=True
    )
    markeplace_id = models.BigIntegerField(
        db_column='webhook_marketplace_id',
        null=True,
        blank=True
    )
    date_created = models.DateTimeField(
        db_column='webhook_date_created',
        null=True,
        blank=True
    )

    class Meta:
        db_table = u"integration\".\"tb_webhook"
        verbose_name = "Webhook"
        verbose_name_plural = "Webhooks"

    def __unicode__(self):
        return "{}/{}/{}".format(
            self.integration,
            self.model_selected,
            self.external_id
        )


@receiver(post_save, sender=Integration)
def post_save_integration(sender, instance, created, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.name[:30])
        instance.save()


@receiver(post_save, sender=IntegrationHistory)
def post_save_integration_history(
        sender,
        instance,
        created,
        *args,
        **kwargs):
    if not instance.duration and instance.end_date:
        instance.duration = timedelta(instance.start_date - instance.end_date)
        instance.save()
