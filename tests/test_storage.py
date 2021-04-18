from datetime import datetime
from io import BytesIO
import os
import tempfile
from unittest import TestCase
from django.core.files.uploadedfile import InMemoryUploadedFile
from simple_django_api.file.storage import BaseStorage, LocalFileStorage


class Storage(BaseStorage):
    def _save(self, file_obj, content):
        pass


class BaseStorageTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.storage_root = tempfile.TemporaryDirectory()
        cls.storage = Storage(cls.storage_root.name)

    @classmethod
    def tearDownClass(cls):
        cls.storage_root.cleanup()

    def test_generate_filename_with_default_argument(self):
        filename_1 = self.storage.generate_filename(None)
        filename_2 = self.storage.generate_filename(None)
        self.assertIsInstance(filename_1, str)
        self.assertEqual(
            len(filename_1),
            self.storage.RANDOM_FILENAME_LENGTH,
        )
        self.assertNotEqual(filename_1, filename_2)

    def test_generate_filename_with_exist_filename(self):
        filename_1 = self.storage.generate_filename(None, filename='test.png')
        self.assertEqual(filename_1, 'test.png')

        filename_2 = self.storage.generate_filename(
            None,
            filename='test',
            ext='.jpg',
        )
        self.assertEqual(filename_2, 'test')

        filename_3 = self.storage.generate_filename(
            None,
            filename='test',
            prefix='upload',
        )
        self.assertEqual(filename_3, 'upload/test')

    def test_generate_filename_with_prefix(self):
        filename_1 = self.storage.generate_filename(
            None,
            filename='test',
            prefix='upload/%Y/%m/%d',
        )
        self.assertEqual(
            filename_1,
            datetime.now().strftime('upload/%Y/%m/%d/test'),
        )

        filename_2 = self.storage.generate_filename(
            None,
            filename='test',
            prefix='upload/%Y/%m/%d/',
        )
        self.assertEqual(
            filename_2,
            datetime.now().strftime('upload/%Y/%m/%d/test'),
        )

    def test_generate_filename(self):
        file_size = 100
        file_obj = InMemoryUploadedFile(
            BytesIO(os.urandom(file_size)),
            'image',
            '/user/demo.png',
            'image/png',
            file_size,
            '',
        )
        filename = self.storage.generate_filename(file_obj)
        self.assertNotEqual(filename, '/user/demo.png')
        filename, ext = os.path.splitext(filename)
        self.assertEqual(len(filename), self.storage.RANDOM_FILENAME_LENGTH)
        self.assertEqual(ext, '.png')

    def test_get_url(self):
        storage = Storage('', base_url='/upload/')
        self.assertEqual(storage.get_url('demo.png'), '/upload/demo.png')

        storage = Storage('', base_url='http://demo.com/upload/')
        self.assertEqual(storage.get_url('demo.png'),
                         'http://demo.com/upload/demo.png')

        storage = Storage(
            '',
            base_url=lambda filename: f'/uploaded/{filename}',
        )
        self.assertEqual(storage.get_url('demo.png'), '/uploaded/demo.png')


class TestFileStorage(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.storage_root = tempfile.TemporaryDirectory()
        cls.storage = LocalFileStorage(cls.storage_root.name, base_url='')

    @classmethod
    def tearDownClass(cls):
        cls.storage_root.cleanup()

    def test_upload_file(self):
        for file_size in [10, 1000, 10000000]:
            content = os.urandom(file_size)
            # upload BytesIO
            uploaded_filename = self.storage.upload(BytesIO(content))
            uploaded_filepath = self.storage.get_abspath(uploaded_filename)
            with open(uploaded_filepath, 'rb') as uploaded_file_obj:
                self.assertEqual(uploaded_file_obj.read(), content)
            with self.storage.download(uploaded_filename) as f:
                self.assertEqual(f.read(), content)

            # upload InMemoryUploadedFile
            inmemory_upload_file = InMemoryUploadedFile(
                BytesIO(content),
                'image',
                '/user/demo.png',
                'image/png',
                file_size,
                '',
            )
            uploaded_filename = self.storage.upload(inmemory_upload_file)
            uploaded_filepath = self.storage.get_abspath(uploaded_filename)
            with open(uploaded_filepath, 'rb') as uploaded_file_obj:
                self.assertEqual(uploaded_file_obj.read(), content)
            with self.storage.download(uploaded_filename) as f:
                self.assertEqual(f.read(), content)
