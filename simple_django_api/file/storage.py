import abc
from datetime import datetime
from contextlib import contextmanager
import os
from pathlib import Path
from urllib.parse import urljoin

from django.core.files.move import file_move_safe
from simple_django_api.utils.random import get_random_string


class BaseStorage(abc.ABC):
    DEFAULT_CHUNK_SIZE = 64 * 2**10
    RANDOM_FILENAME_LENGTH = 12

    def __init__(self, root, base_url=''):
        self.root = Path(root)
        self.base_url = base_url

    def _touch_file(self, name, mode='rb'):
        pass

    @abc.abstractmethod
    def _save(self, file_obj, content):
        pass

    def upload(self, file_obj, filename=None, ext='', prefix=''):
        filename = self.generate_filename(
            file_obj,
            filename=filename,
            ext=ext,
            prefix=prefix,
        )
        self._touch_file(filename)
        self._save(filename, file_obj)
        return filename

    def download(self, filename):
        raise NotImplementedError()

    def generate_filename(self, file_obj, filename='', prefix='', ext=''):
        if not filename:
            filename = get_random_string(length=self.RANDOM_FILENAME_LENGTH)
            if not ext:
                raw_filename = getattr(file_obj, 'filename', '')
                raw_filename = raw_filename or getattr(file_obj, 'name', '')
                ext = os.path.splitext(raw_filename)[-1].lstrip('.')
            filename = ext and f'{filename}.{ext}' or filename
        prefix = datetime.now().strftime(prefix)
        return os.path.join(prefix, filename)

    def get_abspath(self, filename):
        return self.root / filename

    def get_url(self, filename):
        if callable(self.base_url):
            return self.base_url(filename)
        return urljoin(self.base_url, filename)


class LocalFileStorage(BaseStorage):
    @contextmanager
    def _touch_file(self, name, ignore_exists=False, **kwargs):
        """Make sure file exists
        here we just make sure file exists.
        """
        abspath = self.get_abspath(name)
        if abspath.exists() and not ignore_exists:
            raise ValueError(f'{abspath} already exists')
        if not abspath.parent.exists():
            os.makedirs(abspath.parent)

    def _save(self, name, content, mode='wb'):
        """Save file to File System
        """
        abspath = self.get_abspath(name)
        if hasattr(content, 'temporary_file_path'):
            file_move_safe(content.temporary_file_path(), abspath)
        else:
            chunk_size = self.DEFAULT_CHUNK_SIZE
            content.seek(0)
            with open(abspath, mode=mode) as dest:
                while True:
                    data = content.read(chunk_size)
                    if not data:
                        break
                    dest.write(data)

    @contextmanager
    def download(self, filename, mode='rb', **kwargs):
        filepath = self.get_abspath(filename)
        with open(filepath, mode=mode, **kwargs) as f:
            yield f
