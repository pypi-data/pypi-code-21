# -*- coding: utf-8 -*-
import os
import io
import tempfile
import zipfile
import datetime
import shutil
import json
import pathlib

from google.protobuf import json_format

from modelhub import __version__
from .apis import api
from .utils import cached_property
from .import conf

_model_pb2 = None


def model_pb2():
    global _model_pb2
    if _model_pb2 is None:
        from .protos import model_pb2
        _model_pb2 = model_pb2
    return _model_pb2


class Model(object):

    @classmethod
    def all(cls):
        return [Model(model_name) for model_name in api.ls_subfolder()]

    @classmethod
    def get(cls, name):
        # if name not in api.ls_subfolder():
        #     raise cls.DoesNotExist
        cls.validate_model_name(name)
        model = Model(name)
        try:
            model.manifest
        except api.FileDoesNotExist as e:
            raise cls.DoesNotExist(name) from e
        else:
            if model.local_exists:
                model.save(local=True)
        return model

    @classmethod
    def get_local(cls, name, fallback_to_remote=True):
        cls.validate_model_name(name)
        model = Model(name)
        if model.local_exists:
            with open(model.local_manifest_path) as f:
                model.manifest = cls._parse_manifest(json.load(f))
            return model
        if not fallback_to_remote:
            raise cls.DoesNotExist("{name} not exist in local")
        return cls.get(name)

    @classmethod
    def validate_model_name(cls, name: str):
        if not name.isidentifier():
            raise ValueError("Invalid model_name: {name}. model_name can only contains alphabets, numbers and underscore, and cannot start with number".format(name=name))

    class DoesNotExist(Exception):
        pass

    def __init__(self, name, manifest=None):
        self.name = name
        if manifest is not None:
            self.manifest = manifest

    def __repr__(self):
        return "<Model: %s>" % self.name

    def __eq__(self, other_model):
        if isinstance(other_model, str):
            return self.name == other_model
        return self.name == other_model.name

    manifest_file_name = "manifest.pb.json"

    @property
    def manifest_path(self):
        return os.path.join(self.name, self.manifest_file_name)

    @cached_property
    def manifest(self):
        """
            {
                "name":string,
                "description":string,
                "versions":[
                    {
                        "seq":int,
                        "comment":string,
                        "submit_date":"2012-12-22 11:11:11Z",
                        "file_name":"1.zip",
                        "require_gpu":false,
                    }
                ]
            }
        """
        json_result = api.get_json(self.manifest_path)
        return self._parse_manifest(json_result)

    @classmethod
    def _parse_manifest(cls, dict_):
        pb = model_pb2().Model()
        json_format.ParseDict(dict_, pb)
        return pb

    def save(self, local=False):
        self.manifest.last_update_datetime.FromDatetime(datetime.datetime.now())
        json_value = json_format.MessageToDict(self.manifest)
        if local:
            pathlib.Path(self.local_path).mkdir(parents=True, exist_ok=True)
            with open(self.local_manifest_path, "w") as f:
                json.dump(json_value, f, indent=4)
        else:
            res = api.upload_json(json_value, self.manifest_path, indent=4)
            self.save(local=True)
            return res

    @cached_property
    def versions(self):
        # return api.ls_subfolder(self.name)
        return [ModelVersion(self, version_pb) for version_pb in self.manifest.versions]

    @cached_property
    def latest_version(self):
        try:
            return self.versions[-1]
        except IndexError:
            raise ModelVersion.DoesNotExist("No Version exist")

    @cached_property
    def latest_local_version(self):

        for version in reversed(self.versions):
            if version.local_exists:
                return version
        raise ModelVersion.DoesNotExist("No version local exist")

    def create_version(self, path, **info):
        return ModelVersion.create(self, path, **info)

    def get_version(self, version=None):
        if not version:
            return self.latest_version
        for model_version in self.versions:
            if model_version.manifest.seq == version:
                return model_version
        raise ModelVersion.DoesNotExist

    @classmethod
    def create(cls, name, description, owner_name, owner_email):
        try:
            cls.get(name)
        except cls.DoesNotExist:
            pass
        else:
            raise ValueError("Model name '{name}' already exist".format(name=name))

        pb = model_pb2().Model(
            name=name,
            description=description,
            owner_name=owner_name,
            owner_email=owner_email,
        )
        pb.create_datetime.FromDatetime(datetime.datetime.now())
        obj = cls(name, manifest=pb)
        obj.save()
        return obj

    def delete(self):
        # TODO: now just delete everything, lately will provide a Trash Can
        return api.delete_file(self.name, recursive=True)

    def delete_local(self):
        for version in self.versions:
            print("deleting version", version.manifest.seq)
            version.local_exists and version.delete_local()
        shutil.rmtree(self.local_path)

    def update(self, **info):
        for k, v in info.values():
            setattr(self.manifest, k, v)
        self.save()

    @property
    def local_path(self):
        return os.path.join(conf.LOCAL_MODEL_DIR, self.name)

    @property
    def local_exists(self):
        return os.path.exists(self.local_manifest_path)

    @property
    def local_manifest_path(self):
        return os.path.join(self.local_path, self.manifest_file_name)

    @staticmethod
    def split_name_version(model_name):
        if "@" in model_name:
            model_name, version = model_name.split("@", 1)
            version = int(version)
        else:
            version = None
        return model_name, version

    def copy(self, new_name, local=False):
        if self.name == new_name:
            return

        cls = type(self)
        manifest = model_pb2().Model()
        manifest.CopyFrom(self.manifest)
        manifest.name = new_name
        new_model = cls(new_name, manifest=manifest)

        if local:
            api.local_link_dir(self.local_path, new_model.local_path)
            return new_model.local_path

        try:
            cls.get(new_name)
        except cls.DoesNotExist:
            pass
        else:
            raise ValueError("Model name '{name}' already exist".format(name=new_name))

        api.copy_dir(self.name, new_model.name)
        self.copy(new_name, local=True)
        new_model.save()


class ModelVersion(object):

    def __init__(self, model, manifest):
        self.model = model
        self.manifest = manifest

    def __repr__(self):
        return "<ModelVersion: %s-%s>" % (self.model.name, self.manifest.seq)

    @property
    def local_path(self):
        return os.path.join(self.model.local_path, str(self.manifest.seq))

    @property
    def saved_model_info(self):
        return self.manifest.saved_model_info[0] if self.manifest.saved_model_info else None

    @property
    def local_exists(self):
        return os.path.exists(self.local_path)

    def download(self, fp: io.BytesIO):
        return api.get_file(
            fp,
            self.model.name,
            self.manifest.file_name,
            md5=self.manifest.compressed_md5,
            progressbar=True,
            size=self.manifest.compressed_size
        )

    @classmethod
    def create(cls, model, path, **info):
        # comment is mandatory
        assert "comment" in info
        print("verifying...")
        api.ensure_version("submit")
        versions = model.manifest.versions
        if versions:
            last_version = versions[-1].seq
        else:
            last_version = 0
        version = model_pb2().ModelVersion(
            seq=last_version + 1,
            modelhub_version=__version__,
            **info
        )
        print("parsing...")
        try:
            saved_model_info = cls._parse_saved_model_info(path)
        except cls.ValidationError as e:
            print(e, ", will treate as a NTF model")
            version.is_saved_model = False
            cls.is_valid_ntf_folder(path)
        else:
            version.saved_model_info.extend(saved_model_info)
            version.is_saved_model = True

        file_infos = cls._parse_file_info(path)
        if not file_infos:
            raise cls.ValidationError("No file to submit.")
        version.files.extend(file_infos)

        file_name = "{model.name}-{version.seq}.zip".format(model=model, version=version)
        with tempfile.TemporaryFile() as f:
            print("compressing...")
            cls._compress_model(f, path)
            version.compressed_size = api.get_fp_size(f)
            print("hashing...")
            version.compressed_md5 = api.md5sum(f)
            print("uploading...")
            api.upload_file(f, model.name, file_name, progressbar=True)
        version.file_name = file_name
        version.submit_datetime.FromDatetime(datetime.datetime.now())
        model.manifest.versions.extend([version])
        print("saving...")
        model.save()
        obj = cls(model, version)
        api.local_link_dir(path, obj.local_path)
        return obj

    def delete(self):
        self.model.manifest.versions.remove(self.manifest)
        self.model.save()
        api.delete_file(self.model.name, self.manifest.file_name)
        api.delete_local()

    def delete_local(self):
        assert self.local_exists
        shutil.rmtree(self.local_path)

    def checkout(self, path=None):
        path = path or self.local_path
        if path == self.local_path and self.local_exists:
            return path
        with tempfile.TemporaryFile() as f:
            print("downloading...")
            self.download(f)
            print("decompressing...")
            self._decompress_model(f, path)
        self.model.save(local=True)
        return path

    @classmethod
    def _parse_saved_model_info(cls, path):
        saved_model_def = cls.is_valid_saved_model(path, load=True)
        if saved_model_def is False:
            raise cls.ValidationError("{path} is not a valid SavedModel path".format(path=path))
        return [
            cls._meta_graph_to_saved_model_info(meta_graph)
            for meta_graph in saved_model_def.meta_graphs
        ]

    @staticmethod
    def _meta_graph_to_saved_model_info(meta_graph):
        saved_model_info = model_pb2().SavedModelInfo(
            tags=meta_graph.meta_info_def.tags,
            tensorflow_version=meta_graph.meta_info_def.tensorflow_version,
            tensorflow_git_version=meta_graph.meta_info_def.tensorflow_git_version,
            # signature_def=meta_graph.signature_def,
            asset_file_def=meta_graph.asset_file_def
        )
        for k, v in meta_graph.signature_def.items():
            saved_model_info.signature_def[k].CopyFrom(v)

        return saved_model_info

    @staticmethod
    def is_valid_saved_model(path, load=False):
        if not os.path.isdir(path):
            return False
        if not os.path.exists(os.path.join(path, "saved_model.pb")):
            return False

        if load:
            from tensorflow.contrib.saved_model.python.saved_model.reader import read_saved_model
            try:
                return read_saved_model(path)
            except Exception:
                return False
        return True

    @classmethod
    def is_valid_ntf_folder(cls, path):
        if not os.path.isdir(path):
            raise cls.ValidationError("path {path} need to be a folder".format(path=path))
        for item_name in os.listdir(path):
            if not (item_name.startswith(".") or item_name in ("assets", "variables", "saved_model.pb")):
                raise cls.ValidationError("Error: NTF model can only contain 'assets' and 'variables' folder")
            if item_name in ("assets", "variables", "saved_model.pb"):
                if not os.path.isdir(os.path.join(path, item_name)):
                    raise cls.ValidationError("Error: {item_name} must be a folder".format(item_name=item_name))

    @staticmethod
    def _compress_model(f, path):
        with zipfile.ZipFile(f, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.startswith("."):
                        continue
                    print("compressing", root, file)
                    # dir_name, file_name=os.path.split(path)
                    full_path = os.path.join(root, file)
                    zipf.write(full_path, os.path.relpath(full_path, path))
        f.seek(0)

    @classmethod
    def _parse_file_info(cls, path):
        file_info_cls = model_pb2().FileDef
        file_infos = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.startswith("."):
                    continue
                file_path = os.path.join(root, file)
                file_name = os.path.relpath(file_path, path)
                with open(file_path, "rb") as f:
                    md5 = api.md5sum(f)
                file_infos.append(file_info_cls(
                    file_name=file_name,
                    file_size=os.path.getsize(file_path),
                    md5=md5
                ))
        return file_infos

    @staticmethod
    def _decompress_model(f, path):
        with zipfile.ZipFile(f, "r") as zipf:
            zipf.extractall(path)
        f.seek(0)

    class DoesNotExist(Exception):
        pass

    class ValidationError(Exception):
        pass
