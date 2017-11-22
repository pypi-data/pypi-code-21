class VersaoRegistroService(object):

    @staticmethod
    def desativa_versao_registro(model, **query_args):
        registros = model.objects.filter(**query_args)

        if len(registros) > 0:
            for registro in registros:
                registro.set_status("I")
                registro.save()
        return True

    @staticmethod
    def get_versao_registro(model, **query_args):
        registros = model.objects.filter(**query_args).order_by('-data_hora')

        if len(registros) > 0:
            return registros[0]
        else:
            return False

    @staticmethod
    def get_versao_user(model, user_meta: dict, **query_args):

        # se usuarioCod foi informado, tenta filtrar por usuário.
        if 'usuario_cod' in user_meta:
            user_query = query_args
            user_query['usuario_cod'] = user_meta['usuario_cod']
            busca_user = model.objects.filter(**user_query).order_by('-data_hora')[:1]

            if len(busca_user) > 0:
                return busca_user[0]

        # se orgaoEntidadeCod foi informado, tenta filtrar por entidade.
        if 'orgao_entidade_cod' in user_meta:
            entidade_query = query_args
            entidade_query['orgao_entidade_cod'] = user_meta['orgao_entidade_cod']
            busca_entidade = model.objects.filter(**entidade_query).order_by('-data_hora')[:1]

            if len(busca_entidade) > 0:
                return busca_entidade[0]

        # se orgaoCod foi informado, tenta filtrar por órgão.
        if 'orgao_cod' in user_meta:
            orgao_query = query_args
            orgao_query['orgao_cod'] = user_meta['orgao_cod']
            busca_orgao = model.objects.filter(**orgao_query).order_by('-data_hora')[:1]

            if len(busca_user) > 0:
                return busca_orgao[0]

        # em último caso, tenta filtrar sem nenhuma das restrições anteriores.
        busca = model.objects.filter(**query_args).order_by('-data_hora')[:1]

        if len(busca) > 0:
            return busca[0]
        else:
            return False

