import os
import json
from collections import OrderedDict

from django.utils import timezone


class CacheService(object):
    """
    Service responsável pelas operções de criação, leitura e destruição de cache
    """
    cache_path = str()
    cache_root = str()

    def __init__(self, cache_root="", cache_path=""):
        self.cache_root = cache_root
        self.cache_path = cache_path

    def get_cached_data(self, cache_name, cache_file_id) -> object:
        """
        Recupera os dados em cache na pasta de uma App
        :param cache_name: nome do cache 'pf_nome', 'lotacao', 'mat' etc
        :param cache_file_id: identifição do cache, pf_nome_id, lotacao_id, mat_id etc
        :return: object
        """
        cache_file = "%s/%s/json/%s/%s.json" % (self.cache_root, self.cache_path, cache_name, cache_file_id)

        if os.path.isfile(cache_file):
            return self.read_file(cache_file)
        else:
            return False

    def get_cached_data_raw(self, cache_name, cache_file_id) -> object:
        """
        Recupera os dados em cache na pasta de uma App e retorna seu conteúdo sem alterar o formato de texto para objeto
        :param cache_name: nome do cache 'pf_nome', 'lotacao', 'mat' etc
        :param cache_file_id: identifição do cache, pf_nome_id, lotacao_id, mat_id etc
        :return: object
        """
        cache_file = "%s/%s/json/%s/%s.json" % (self.cache_root, self.cache_path, cache_name, cache_file_id)

        if os.path.isfile(cache_file):
            return self.read_file_raw(cache_file)
        else:
            return False

    def write_cache_data_pf(self, pf_id: str(), oid: str(), cache_name: str(), data: dict()):
        """
        Escreve dados em cache, na pasta pf_id de uma determinada pessoa física.
        :param pf_id: Id da pessoa física
        :param oid: Id do órgão do usuário que criou a informação
        :param cache_name: Pasta do cache nome, cpf, nome_social etc
        :param data: Dados a serem salvos em cache
        :return: bool
        """
        cache_dir = "%s/%s/json/%s/%s/%s" % (
            self.cache_root, self.cache_path, pf_id, cache_name, oid
        )

        if os.path.isdir(cache_dir) is False:
            self.build_cache_path(pf_id, cache_name, oid)

        file_timestamp = timezone.now().timestamp()
        return self.write_file_raw("%s/%s.json" % (cache_dir, str(file_timestamp).replace('.', '')), data)

    def write_cache_data_inverso(self, oid: str(), ref_id: str(), file_id: str(), cache_name: str(), data: dict()):
        """
        Escreve dados em cache na pasta da ref_id informada
        :param oid:
        :param ref_id: Id do órgão do usuário que criou a informação
        :param file_id: Identifição do arquivo de cache
        :param cache_name: Nome do cache
        :param data: Dados a serem salves em cache
        :return: bool
        """
        cache_dir = "%s/%s/json/%s/%s" % (
            self.cache_root, self.cache_path, cache_name, oid
        )

        if os.path.isdir(cache_dir) is False:
            os.mkdir(cache_dir, 0o777)

        cache_ref_dir = "%s/%s" % (cache_dir, ref_id)

        if os.path.isdir(cache_ref_dir) is False:
            os.mkdir(cache_ref_dir, 0o777)

        file_name = "%s/%s.json" % (cache_ref_dir, file_id)
        return self.write_file_raw(file_name, data)

    def write_cache_data(self, cache_name, cache_file_id, data):
        """
        Salva dados em cache na pasta da App que instancio este service
        :param cache_name: Nome do cache
        :param cache_file_id: Identificação do arquivo de cache
        :param data: Dados a serem salvos
        :return: bool
        """
        cache_file = "%s/%s/json/%s/%s.json" % (self.cache_root, self.cache_path, cache_name, cache_file_id)
        return self.write_file(cache_file, data)

    def write_cache_data_raw(self, cache_name, cache_file_id, data):
        """
        Salva dados em cache na pasta da App que instancio este service, mas sem alterar o formato em que os dados serão
        salvos
        :param cache_name: Nome do cache
        :param cache_file_id: Identificação do arquivo de cache
        :param data: Dados a serem salvos
        :return: bool
        """
        cache_dir = "%s/%s/json/%s" % (
            self.cache_root, self.cache_path, cache_name
        )

        if os.path.isdir(cache_dir) is False:
            os.mkdir(cache_dir, 0o777)

        cache_file = "%s/%s.json" % (cache_dir, cache_file_id)
        return self.write_file_raw(cache_file, data)

    def remove_cached_data(self, cache_name, cache_file_id):
        """
        Deleta um arquivo de cache, conforme os parâmetros informados
        :param cache_name: Nome do cache
        :param cache_file_id: Identficação do arquivo de cache
        :return: bool
        """
        cache_file = "%s/%s/json/%s/%s.json" % (self.cache_root, self.cache_path, cache_name, cache_file_id)
        return self.remove_file(cache_file)

    @staticmethod
    def read_file_raw(file_name):
        """
        Lê um arquivo de cache e retorna seu conteúdo sem alterar o formato.
        :param file_name: Identficação do arquivo de cache
        :return: str
        """
        if os.path.isfile(file_name):
            handle = open(file_name, "r")
            json_data = handle.read()
            handle.close()
            return json_data
        else:
            return False

    @staticmethod
    def write_file_raw(file_name, data):
        """
        Salvo um arquivo de cache, conforme os parâmetros informados, sem alterar o seu formato
        :param file_name: Path completo(caminho, nome e extensão) onde o arquivo será salvo
        :param data: str
        :return: bool
        """
        handle = open(file_name, "w+")
        handle.write(data)
        handle.close()
        return True

    @staticmethod
    def read_file(file_name):
        """
        Lê um arquivo de cache e tenta decodificar o conteúdo como JSON
        :param file_name: Path completo(caminho, nome e extensão) onde o arquivo será salvo
        :return: object
        """
        if os.path.isfile(file_name):
            json_data = False
            handle = open(file_name, "r")
            data = handle.read()
            if len(data) > 0:
                json_data = json.loads(data, object_pairs_hook=OrderedDict)
            handle.close()
            return json_data
        else:
            return False

    @staticmethod
    def write_file(file_name, data):
        """
        Salvo um arquivo de cache, conforme os parâmetros informados, convertendo o conteúdo em data para JSON
        :param file_name: Path completo(caminho, nome e extensão) onde o arquivo será salvo
        :param data: object
        :return: bool
        """
        handle = open(file_name, "w+")
        handle.write(json.dumps(data))
        handle.close()
        return True

    @staticmethod
    def remove_file(file_name):
        """
        Deleta um arquivo de cache, conforme os parâmetros informados
        :param file_name: Path completo(caminho, nome e extensão) onde o arquivo será salvo
        :return: bool
        """
        if os.path.isfile(file_name):
            os.unlink(file_name)
            return True
        else:
            return False

    def build_cache_path(self, pf_id: str(), cache_name: str(), oid: str()):
        """
        Cria as patas e sub-pastas da estrutura de cache da pessoa física, conforme parâmetros
        :param pf_id: Id da pessoa física
        :param cache_name: Nome do cache
        :param oid: Órgão do usuário que criou o registro
        :return: bool
        """
        pf_path = "%s/%s/json/%s" % (self.cache_root, self.cache_path, pf_id)

        if os.path.isdir(pf_path) is False:
            os.mkdir(pf_path, 0o777)

        cache_pf_path = "%s/%s" % (pf_path, cache_name)

        if os.path.isdir(cache_pf_path) is False:
            os.mkdir(cache_pf_path, 0o777)

        cache_pf_oid_path = "%s/%s/%s" % (pf_path, cache_name, oid)

        if os.path.isdir(cache_pf_oid_path) is False:
            os.mkdir(cache_pf_oid_path, 0o777)

        return True
