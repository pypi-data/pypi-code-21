# coding=utf-8
from tests.base import BaseTest
from mali_commands.data_volume import create_data_volume, with_repo
import tempfile
from mali_commands.legit.object_store.gcs.gcs_object_store import return_request_result
from mali_commands.legit.dulwich import porcelain
from fudge import patched_context
import os


class TestData(BaseTest):
    @classmethod
    def get_repo(cls, temp_path=None, volume_id=None, linked=False, description=None, display_name=None):
        temp_path = temp_path or tempfile.tempdir
        volume_id = volume_id or cls.some_random_shit_number_int63()
        data_path = temp_path
        description = description or cls.some_random_shit(size=50)
        display_name = display_name or cls.some_random_shit(size=10)
        res = create_data_volume(volume_id, data_path, linked, display_name, description)
        return res

    def test_return_request_result(self):
        t1 = self.some_random_shit(size=30)
        t2 = self.some_random_shit(size=30)
        x1, x2 = return_request_result(t1, t2)
        self.assertEqual(x1, t1)
        self.assertEqual(x2, t2)

    def test_repo_add_objects(self):
        temp_path = tempfile.tempdir
        volume_id = self.some_random_shit_number_int63()
        data_path = temp_path
        linked = False
        description = self.some_random_shit(size=50)
        display_name = self.some_random_shit(size=10)
        res = create_data_volume(volume_id, data_path, linked, display_name, description)
        self.assertIsNotNone(res)
        with with_repo(None, volume_id) as rep:
            self.assertIsNotNone(rep)

    def test_porcelan_add_stage(self):
        import os
        import tempfile
        file_count = 10
        is_embedded = True
        volume_id = self.some_random_shit_number_int63()
        repo_config = self.get_repo(volume_id=volume_id, linked=is_embedded)

        def make_temp_files(count):
            for i in range(count):
                f = tempfile.NamedTemporaryFile(suffix='.txt', prefix='test_enumerate_paths__', delete=False)
                f.write(bytearray("Hello World!\n{}\n".format(i), 'utf8'))
                f.close()
                yield f.name

        tempfiles = list(make_temp_files(file_count))
        with with_repo(None, volume_id) as rep:
            rep.data_path = '/'

            def patched_stage(inst, paths, embedded):
                for path in paths:
                    self.assertIn('/' + path, tempfiles)
                self.assertEqual(len(paths), len(tempfiles))

            with patched_context(rep, 'stage', patched_stage):
                porcelain.add(rep, tempfiles, is_embedded)

    def test_porcelan_stage_generate_files(self):
        import tempfile
        file_count = 10
        is_embedded = True
        volume_id = self.some_random_shit_number_int63()
        repo_config = self.get_repo(volume_id=volume_id, linked=is_embedded)

        def make_temp_files(count):
            for i in range(count):
                f = tempfile.NamedTemporaryFile(suffix='.txt', prefix='test_enumerate_paths__', delete=False)
                f.write(bytearray("Hello World!\n{}\n".format(i), 'utf8'))
                f.close()
                yield f.name

        tempfiles = list(make_temp_files(file_count))
        with with_repo(None, volume_id) as rep1:
            rep1.data_path = '/'
            rep1.path = '/'

            def patched_stage1(inst, files):
                for file in files:
                    self.assertIn(file.full_path, tempfiles)
                    self.assertIn(os.path.join('/', file.tree_path.decode('utf-8')), tempfiles)
                self.assertEqual(len(files), len(tempfiles))

            def patched_set_entities(inst, index, en):
                for file in en:
                    self.assertIn('/' + file.decode('utf-8'), tempfiles)
                self.assertEqual(len(en.keys()), len(tempfiles))

            with patched_context(rep1, '_upload_staged_files', patched_stage1):
                with patched_context(rep1, '_set_entries', patched_set_entities):
                    porcelain.add(rep1, tempfiles, is_embedded)

    def test_stage_file_builder(self):
        import tempfile
        file_count = 10
        is_embedded = True
        volume_id = self.some_random_shit_number_int63()
        repo_config = self.get_repo(volume_id=volume_id, linked=is_embedded)

        def make_temp_files(count):
            for i in range(count):
                f = tempfile.NamedTemporaryFile(suffix='.txt', prefix='test_enumerate_paths__', delete=False)
                f.write(bytearray("Hello World!\n{}\n".format(i), 'utf8'))
                f.close()
                yield f.name

        tempfiles = list(make_temp_files(file_count))
        with with_repo(None, volume_id) as rep:
            rep.data_path = '/'
            rep.path = '/'
            index = rep.open_index()

            closure_dict = {}

            def patched_stage(inst, paths, embedded):
                for path in paths:
                    self.assertIn('/' + path, tempfiles)
                self.assertEqual(len(paths), len(tempfiles))
                closure_dict['rel_paths'] = paths

            with patched_context(rep, 'stage', patched_stage):
                porcelain.add(rep, tempfiles, is_embedded)

            relpaths = closure_dict['rel_paths']
            files = list(rep._build_stage_files(relpaths, index, is_embedded))
            self.assertEqual(len(files), len(tempfiles))
