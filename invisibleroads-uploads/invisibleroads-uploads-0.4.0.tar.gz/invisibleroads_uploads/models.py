from glob import glob
from invisibleroads_macros.disk import (
    get_file_extension, make_enumerated_folder, make_unique_folder,
    resolve_relative_path)
from invisibleroads_posts.models import DummyBase, FolderMixin, get_record_id
from io import BytesIO
from os import rename
from os.path import basename, join
from pyramid.httpexceptions import HTTPBadRequest, HTTPNotFound
from shutil import copyfileobj
from six import string_types


class Upload(FolderMixin, DummyBase):

    @classmethod
    def save(Class, data_folder, owner_id, id_length, source_name, source_x):
        source_extension = get_file_extension(source_name)
        source_file = prepare_file(source_x)
        instance = Class.spawn(data_folder, id_length, owner_id)
        instance.name = source_name
        instance.path = join(instance.folder, 'raw' + source_extension)
        # Save name
        open(join(instance.folder, 'name.txt'), 'wt').write(source_name)
        # Save path
        temporary_path = join(instance.folder, 'temporary.bin')
        with open(temporary_path, 'wb') as temporary_file:
            copyfileobj(source_file, temporary_file)
        rename(temporary_path, instance.path)
        return instance

    @classmethod
    def save_from(Class, request, param_name):
        try:
            field_storage = request.POST[param_name]
        except KeyError:
            raise HTTPBadRequest
        try:
            source_file = field_storage.file
        except AttributeError:
            raise HTTPBadRequest
        source_name = basename(field_storage.filename)
        user_id = request.authenticated_userid
        settings = request.registry.settings
        return Class.save(
            request.data_folder, user_id, settings['upload.id.length'],
            source_name, source_file)

    @classmethod
    def load(Class, data_folder, owner_id, record_id):
        instance = Class(id=record_id, owner_id=owner_id)
        instance.folder = instance.get_folder(data_folder)
        instance.name = open(join(instance.folder, 'name.txt')).read()
        try:
            instance.path = glob(join(instance.folder, 'raw*'))[0]
        except IndexError:
            raise IOError
        return instance

    @classmethod
    def get_from(Class, request, record_id=None):
        key = Class._singular + '_id'
        if not record_id:
            record_id = get_record_id(request, key)
        user_id = request.authenticated_userid
        try:
            instance = Class.load(request.data_folder, user_id, record_id)
        except IOError:
            raise HTTPNotFound({key: 'bad'})
        return instance

    @classmethod
    def spawn(Class, data_folder, id_length=None, owner_id=None):
        upload = super(Upload, Class).spawn(data_folder, id_length, owner_id)
        upload.owner_id = owner_id
        return upload

    @classmethod
    def spawn_folder(Class, data_folder, id_length=None, owner_id=None):
        user_folder = Class.get_user_folder(data_folder, owner_id)
        return make_unique_folder(
            user_folder, length=id_length,
        ) if id_length else make_enumerated_folder(user_folder)

    @classmethod
    def get_user_folder(Class, data_folder, owner_id):
        parent_folder = Class.get_parent_folder(data_folder)
        folder_name = str(owner_id or 'anonymous')
        return resolve_relative_path(folder_name, parent_folder)

    def get_folder(self, data_folder):
        user_folder = self.get_user_folder(data_folder, self.owner_id)
        folder_name = str(self.id)
        return resolve_relative_path(folder_name, user_folder)


def prepare_file(x):
    if isinstance(x, string_types):
        x = x.encode('utf-8')
    if isinstance(x, bytes):
        x = BytesIO(x)
    return x
