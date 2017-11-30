# -*- coding: utf-8 -*-
import os
import json
import logging
from li_api_client.integration import ApiIntegration
from repositories.integration.models import (
    AccountIntegration, ModelIntegration, IntegrationHistory)


class BaseNotificationService(object):
    def __init__(
            self,
            instance=None,
            delete_id=None,
            account_id=None,
            same_number=False,
            *args,
            **kwargs):
        super(BaseNotificationService, self).__init__(*args, **kwargs)
        self.instance = instance
        self.sandbox = os.environ.get('ENVIRONMENT') != 'production'
        if hasattr(instance, 'conta'):
            self.account_id = instance.conta.id
        else:
            self.account_id = account_id
        self.crud = '',
        self.integration_list = []
        self.model_dict = {}
        self.instance_id = delete_id if delete_id else instance.id
        self.delete = True if delete_id else False
        self.instance_model = self.model._meta.model_name \
            if delete_id else self.instance._meta.model_name
        self.same_number = same_number
        self.plan = None

    def get_next_number(self):
        try:
            last_history = IntegrationHistory.objects.filter(
                account_id=self.account_id,
                operation_id__isnull=False
            ).order_by('start_date').last()
            new_id = last_history.operation_id
        except:
            new_id = 1

        if self.same_number:
            return new_id
        else:
            return new_id + 1

    # Checar se os dados são válidos
    def validate_args(self):
        if not self.serializer:
            raise ValueError(
                u"É preciso definir o serializador usando nesta classe")
        if not self.model:
            raise ValueError(u"É preciso definir o modelo usando nesta classe")
        if not self.delete:
            if self.model != self.instance._meta.model:
                raise ValueError(
                    u"A instância enviada não é compativel com o modelo")
        if not self.account_id:
            raise ValueError("Informe a conta")

    # Se for sandbox, adicionar o produto as integracoes ativas
    def add_model_instance(self):
        if self.instance and self.instance._meta.model_name == 'pedidovenda':
            return
        active_integrations = AccountIntegration.objects.filter(
            account_id=self.account_id, active=True)
        # Para cada integração ativa na Loja
        for account_integration in active_integrations:
            if self.instance and self.instance._meta.model_name == 'produto' \
                    and not account_integration.integration.all_products:
                continue
            else:
                new_model_integration, \
                    created = ModelIntegration.objects.get_or_create(
                        account_id=self.account_id,
                        model_selected=self.instance_model,
                        model_selected_id=self.instance_id,
                        integration=account_integration.integration
                    )

    def model_select_is_valid(self, obj, *args, **kwargs):
        """
                Sobrescrever este método para validações
                específicas do modelo
        """
        return True

    # Listar conectores válidos para modelo/loja enviados
    def get_connectors(self):
        self.integration_list = []

        # Para cada modelo em ModelIntegration
        for model_for_integration in ModelIntegration.objects.filter(
                account_id=self.account_id,
                model_selected=self.instance_model,
                model_selected_id=self.instance_id,
        ):
            # Se a integrãção está ativa, não for exclusão sem external_id
            # e o objeto selecionado passar pela própria validação
            if not model_for_integration.active():
                logging.warning("O MODELO NAO ESTA ATIVO")
                continue

            if self.delete and not model_for_integration.external_id:
                logging.warning("EXCLUSAO SEM REFERENCIA EXTERNA")
                continue

            if not self.model_select_is_valid(
                model_for_integration.get_object(
                    self.account_id, self.model
                ),
                model_for_integration.integration.slug
            ):
                continue

            self.integration_list.append(model_for_integration)

        return self.integration_list

    # Definir Create, Update, Delete (Removed) ou Delete (Model)
    def set_crud(self, crud=None):
        self.crud = crud

    # Gerar o dicionario
    def model_to_dict(self):
        if self.delete:
            self.model_dict = self.serializer(
                delete_id=self.instance_id).serialize()
        else:
            self.model_dict = self.serializer(
                self.instance).serialize()

    # Enviar notificação
    def send_notification(self):
        # Uma mensagem para todos os conectores
        self.model_dict['connector_list'] = [
            model_integration.integration.slug
            for model_integration in self.integration_list
        ]
        # Para cada modelo nos integradores listados
        for model_integration in self.integration_list:

            history_test_list = IntegrationHistory.objects.filter(
                account_id=self.account_id,
                model_selected=self.instance_model,
                model_selected_id=self.instance_id,
                integration=model_integration.integration,
                status="WAIT"
            )
            if history_test_list.count() > 1:
                history_test_list.delete()

            integration_history, \
                created = IntegrationHistory.objects.get_or_create(
                    account_id=self.account_id,
                    model_selected=self.instance_model,
                    model_selected_id=self.instance_id,
                    integration=model_integration.integration,
                    status="WAIT"
                )
            if created:
                integration_history.operation_id = self.get_next_number()
                integration_history.save()
            print("CRIOU HISTORICO: {}".format(integration_history.id))

    def use_internal_api(self):
        history_list = IntegrationHistory.objects.filter(
            account_id=self.account_id,
            status="WAIT"
        )
        for history in history_list:
            # Criar a notificação via API interna
            ApiIntegration().send_notification(
                crud=self.crud,
                history_id=history.id,
                model_dict=json.dumps(self.model_dict)
            )

    # Processar Notificacao
    def notify(self, crud, plan=None):
        if plan:
            self.plan = plan
        self.validate_args()
        self.add_model_instance()
        self.get_connectors()
        if self.integration_list:
            self.set_crud(crud)
            self.model_to_dict()
            self.send_notification()
            self.use_internal_api()
