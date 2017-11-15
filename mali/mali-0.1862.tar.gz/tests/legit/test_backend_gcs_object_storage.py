import tempfile

import fudge
import six
from fudge import patched_context
from fudge.inspector import arg

from mali_commands.data_volume import create_data_volume, with_repo
from mali_commands.legit.dulwich import porcelain
from mali_commands.legit.object_store.gcs.gcs_object_store import GCSObjectStore, do_upload, GCSUpload
from mali_commands.legit.object_store.gcs.backend_gcs_object_store import BackendGCSObjectStore
from tests.base import BaseTest
from mali_commands.legit.dulwich.repo import Repo


class TestBGCSStorage(BaseTest):
    @classmethod
    def get_repo(cls, temp_path=None, volume_id=None, linked=False, description=None, display_name=None):
        temp_path = temp_path or tempfile.tempdir
        volume_id = volume_id or cls.some_random_shit_number_int63()
        data_path = temp_path
        description = description or cls.some_random_shit(size=50)
        display_name = display_name or cls.some_random_shit(size=10)
        res = create_data_volume(volume_id, data_path, linked, display_name, description)
        return res

    @classmethod
    def __base_64_decoder_func(cls):
        import base64
        if six.PY2:
            return base64.decodestring
        else:
            return base64.decodebytes

    @classmethod
    def image(cls):
        return cls.__base_64_decoder_func()(
            b'/9j/4AAQSkZJRgABAQEAYABgAAD//gA+Q1JFQVRPUjogZ2QtanBlZyB2MS4wICh1c2luZyBJSkcgSlBFRyB2ODApL'
            b'CBkZWZhdWx0IHF1YWxpdHkK/9sAQwAIBgYHBgUIBwcHCQkICgwUDQwLCwwZEhMPFB0aHx4dGhwcICQuJyAiLCMcHCg'
            b'3KSwwMTQ0NB8nOT04MjwuMzQy/9sAQwEJCQkMCwwYDQ0YMiEcITIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMj'
            b'IyMjIyMjIyMjIyMjIyMjIyMjIy/8AAEQgAHgAeAwEiAAIRAQMRAf/EAB8AAAEFAQEBAQEBAAAAAAAAAAABAgMEBQYHC'
            b'AkKC//EALUQAAIBAwMCBAMFBQQEAAABfQECAwAEEQUSITFBBhNRYQcicRQygZGhCCNCscEVUtHwJDNicoIJChYXGBka'
            b'JSYnKCkqNDU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6g4SFhoeIiYqSk5SVlpeYmZqio6Slpqe'
            b'oqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2drh4uPk5ebn6Onq8fLz9PX29/j5+v/EAB8BAAMBAQEBAQEBAQEAAAA'
            b'AAAABAgMEBQYHCAkKC//EALURAAIBAgQEAwQHBQQEAAECdwABAgMRBAUhMQYSQVEHYXETIjKBCBRCkaGxwQkjM1LwFWJy'
            b'0QoWJDThJfEXGBkaJicoKSo1Njc4OTpDREVGR0hJSlNUVVZXWFlaY2RlZmdoaWpzdHV2d3h5eoKDhIWGh4iJipKTlJWWl'
            b'5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uLj5OXm5+jp6vLz9PX29/j5+v/aAAwDAQACEQMRAD8'
            b'ArUVLFbSTIWjCnbyRuAwPX6U14XR9pXJ46c5yMiv0PmV7H5ryu1xlFSxW0kyFowp28kbgMD1+lMkjaJ9rYzgHg54IyKLq9g5'
            b'WlclhungRkUKVYYYHPI/OgXUiuzKFG5AhGP4cYx+gqCijlQc8tieG6eBGRQpVhhgc8j86jkkMr7iAOAMD0AwP5UyihRSdwcm1Y//Z')

    @classmethod
    def make_temp_files(cls, count, image=False):
        suffix = '.txt'
        if image:
            suffix = '.jpg'
            # image_bytes = cls.__base_64_decoder_func(cls.image_str)
        for i in range(count):
            f = tempfile.NamedTemporaryFile(suffix=suffix, prefix='test_enumerate_paths__', delete=False)
            if image:
                f.write(cls.image())
            else:
                f.write(bytearray("Hello World!\n{}\n".format(i), 'utf8'))
            f.close()
            yield f.name

    def test_group_files_by_meta_jpg(self):
        file_count = 10
        is_embedded = True
        volume_id = self.some_random_shit_number_int63()
        repo_config = self.get_repo(volume_id=volume_id, linked=is_embedded)
        tempfiles = list(self.make_temp_files(file_count, image=True))
        with with_repo(None, volume_id) as rep:
            rep.data_path = '/'
            rep.path = '/'

            closure_dict = {}

            def patched_stage(inst, paths, embedded):
                for path in paths:
                    self.assertIn('/' + path, tempfiles)
                self.assertEqual(len(paths), len(tempfiles))
                closure_dict['rel_paths'] = paths

            with patched_context(rep, 'stage', patched_stage):
                porcelain.add(rep, tempfiles, is_embedded)

            relpaths = closure_dict['rel_paths']
            index = rep.open_index()
            files = list(rep._build_stage_files(relpaths, index, is_embedded))

            object_store = rep.create_object_store()
            self.assertIsNotNone(object_store)
            # object_store.add_objects(files)
            res = object_store._group_files_by_meta(files)
            res = object_store._group_files_by_meta(files)
            self.assertIsNotNone(res)
            keys = list(res.keys())
            self.assertTrue(len(keys) == 1)
            self.assertEquals(keys[0], 'image/jpeg')
            self.assertEquals(len(res[keys[0]]), file_count)

    def test_group_files_by_meta_txt(self):
        file_count = 10
        is_embedded = True
        volume_id = self.some_random_shit_number_int63()
        repo_config = self.get_repo(volume_id=volume_id, linked=is_embedded)
        tempfiles = list(self.make_temp_files(file_count, image=False))
        with with_repo(None, volume_id) as rep:
            rep.data_path = '/'
            rep.path = '/'

            closure_dict = {}

            def patched_stage(inst, paths, embedded):
                for path in paths:
                    self.assertIn('/' + path, tempfiles)
                self.assertEqual(len(paths), len(tempfiles))
                closure_dict['rel_paths'] = paths

            with patched_context(rep, 'stage', patched_stage):
                porcelain.add(rep, tempfiles, is_embedded)

            relpaths = closure_dict['rel_paths']
            index = rep.open_index()
            files = list(rep._build_stage_files(relpaths, index, is_embedded))

            object_store = rep.create_object_store()
            self.assertIsNotNone(object_store)
            # object_store.add_objects(files)
            res = object_store._group_files_by_meta(files)
            self.assertIsNotNone(res)
            keys = list(res.keys())
            self.assertTrue(len(keys) == 1)
            self.assertIsNone(keys[0])

            self.assertEquals(len(res[keys[0]]), file_count)

    def test_group_files_by_meta_mixed(self):
        per_meta_file_count = 10
        is_embedded = True
        volume_id = self.some_random_shit_number_int63()
        repo_config = self.get_repo(volume_id=volume_id, linked=is_embedded)
        temp_txt = list(self.make_temp_files(per_meta_file_count, image=False))
        temp_images = list(self.make_temp_files(per_meta_file_count, image=True))
        tempfiles = temp_txt + temp_images
        with with_repo(None, volume_id) as rep:
            rep.data_path = '/'
            rep.path = '/'

            closure_dict = {}

            def patched_stage(inst, paths, embedded):
                for path in paths:
                    self.assertIn('/' + path, tempfiles)
                self.assertEqual(len(paths), len(tempfiles))
                closure_dict['rel_paths'] = paths

            with patched_context(rep, 'stage', patched_stage):
                porcelain.add(rep, tempfiles, is_embedded)

            relpaths = closure_dict['rel_paths']
            index = rep.open_index()
            files = list(rep._build_stage_files(relpaths, index, is_embedded))

            object_store = rep.create_object_store()
            self.assertIsNotNone(object_store)
            # object_store.add_objects(files)
            res = object_store._group_files_by_meta(files)
            self.assertIsNotNone(res)
            keys = list(res.keys())
            self.assertTrue(len(keys) == 2)
            self.assertIn(None, res)
            self.assertIn('image/jpeg', res)

            self.assertEquals(len(res[keys[0]]), per_meta_file_count)
            self.assertEquals(len(res[keys[1]]), per_meta_file_count)

    @fudge.patch('mali_commands.legit.object_store.gcs.backend_gcs_object_store.BackendGCSSignedUrlService.get_signed_urls')
    def test_get_urls_for_paths(self, get_signed_urls):
        file_count = 10
        is_embedded = True
        volume_id = self.some_random_shit_number_int63()
        repo_config = self.get_repo(volume_id=volume_id, linked=is_embedded)
        tempfiles = list(self.make_temp_files(file_count, image=True))
        with with_repo(None, volume_id) as rep:
            rep.data_path = '/'
            rep.path = '/'

            closure_dict = {}

            def patched_stage(inst, paths, embedded):
                for path in paths:
                    self.assertIn('/' + path, tempfiles)
                self.assertEqual(len(paths), len(tempfiles))
                closure_dict['rel_paths'] = paths

            with patched_context(rep, 'stage', patched_stage):
                porcelain.add(rep, tempfiles, is_embedded)

            relpaths = closure_dict['rel_paths']
            index = rep.open_index()
            files = list(rep._build_stage_files(relpaths, index, is_embedded))

            object_store = rep.create_object_store()
            self.assertIsNotNone(object_store)
            # object_store.add_objects(files)
            res = object_store._group_files_by_meta(files)

            content_type = 'image/jpeg'
            sign_files = res[content_type]
            content_headers = object_store.get_content_headers()
            get_signed_urls.expects_call().with_args(['HEAD', 'PUT'], sign_files, content_type, **content_headers).returns({'HEAD': sign_files, 'PUT': sign_files}).times_called(1)
            # get_signed_urls.expects_call().returns((access_token, refresh_token, id_token)).times_called(1)
            head, put = object_store._get_urls_for_paths(sign_files, content_type, content_headers)
            self.assertIs(head, sign_files)
            self.assertIs(put, sign_files)

    def test_call_for_upload(self):
        file_count = 10
        is_embedded = True
        volume_id = self.some_random_shit_number_int63()
        repo_config = self.get_repo(volume_id=volume_id, linked=is_embedded)
        tempfiles = list(self.make_temp_files(file_count, image=True))
        with with_repo(None, volume_id) as rep:
            rep.data_path = '/'
            rep.path = '/'

            closure_dict = {}

            def patched_stage(inst, paths, embedded):
                for path in paths:
                    self.assertIn('/' + path, tempfiles)
                self.assertEqual(len(paths), len(tempfiles))
                closure_dict['rel_paths'] = paths

            with patched_context(rep, 'stage', patched_stage):
                porcelain.add(rep, tempfiles, is_embedded)

            relpaths = closure_dict['rel_paths']
            index = rep.open_index()
            files = list(rep._build_stage_files(relpaths, index, is_embedded))

            object_store = rep.create_object_store()
            self.assertIsNotNone(object_store)
            # object_store.add_objects(files)
            res = object_store._group_files_by_meta(files)

            content_type = 'image/jpeg'
            sign_files = list(res[content_type])
            content_headers_full = object_store.get_content_headers(content_type)

            def validate_upload_commnad(inst, blob, content_type_arg, head_url, put_url):
                uploading_file = None
                for file in sign_files:
                    if file.blob == blob:
                        uploading_file = file
                        break
                self.assertIsNotNone(uploading_file)
                x = GCSObjectStore._get_shafile_path(uploading_file.blob.id)
                self.assertEquals(content_type_arg, content_type)
                self.assertEquals('{}_HEAD'.format(x), head_url)
                self.assertEquals('{}_PUT'.format(x), put_url)

                # self.upload(cur_file.blob, content_type, head_url, put_url, self.get_content_headers(content_type))

                pass

            def build_upload_paths(inst, paths, content_type, headers):
                head_urls = list(map(lambda x: '{}_HEAD'.format(x), paths))
                put_urls = list(map(lambda x: '{}_PUT'.format(x), paths))
                return head_urls, put_urls

            with patched_context(object_store, 'upload', validate_upload_commnad):
                with patched_context(object_store, '_get_urls_for_paths', build_upload_paths):
                    object_store.add_objects(files)

    @fudge.patch('mali_commands.legit.object_store.gcs.gcs_object_store.do_upload')
    def test_call_to_upload_file(self, do_upload):
        is_embedded = True
        volume_id = self.some_random_shit_number_int63()
        repo_config = self.get_repo(volume_id=volume_id, linked=is_embedded)
        tempfile = list(self.make_temp_files(1, image=True))[0]
        file = Repo.UploadFileRequest(tempfile, tempfile[1:], True)

        content_type = 'image/jpeg'

        file_upload_path = GCSObjectStore._get_shafile_path(file.blob.id)
        head_url = 'HEAD'
        put_url = 'PUT'
        do_upload.expects_call().with_args(
            arg.any(),
            volume_id,
            file_upload_path,
            file.blob.data,
            arg.any(),
            content_type,
            head_url,
            put_url
        ).returns(None).times_called(1)

        # bucket_name, volume_id, object_name, signed_url_service=None
        with with_repo(None, volume_id) as rep:
            object_store = rep.create_object_store()
            with patched_context(object_store, 'is_multiprocess', False):
                self.assertIsNotNone(file)
                object_store.upload(file.blob, content_type, head_url, put_url)

    @fudge.patch('mali_commands.legit.object_store.gcs.gcs_object_store.GCSUpload.upload')
    def test_do_upload(self, upload):

        is_embedded = True
        volume_id = self.some_random_shit_number_int63()
        tempfile = list(self.make_temp_files(1, image=True))[0]
        file = Repo.UploadFileRequest(tempfile, tempfile[1:], True)

        content_type = 'image/jpeg'

        file_upload_path = GCSObjectStore._get_shafile_path(file.blob.id)
        head_url = 'HEAD'
        put_url = 'PUT'
        upload.expects_call().with_args(
            'x',
            volume_id,
            file_upload_path,
            file.blob.data,
            content_type,
            head_url,
            put_url
        ).returns(None).times_called(1)
        do_upload('x', volume_id, file_upload_path, file.blob.data, None, content_type, head_url, put_url)
