import abc
import os

class Base:
    __metaclass__ = abc.ABCMeta

    def __init__(self, root, config):
        self.root = root
        self.config = config

    MAX_FILE_SIZE = 5 * 1024 * 1024 # 5MB

    def _walk(self, processor, *args, **kwargs):
        """
        >>> from collections import namedtuple
        >>> from tests.mock import Mock
        >>> mock = Mock(__name__)

        >>> processed = []
        >>> class Runtime(Base):
        ...     def processor(self, filename, file, custom_positional, custom_keyword):
        ...         processed.append((filename, file.read(), custom_positional, custom_keyword))

        >>> mock.filesystem = {'path': {'to': {'function': {
        ...     'a': True,
        ...     'b': {'c': True, 'd': True},
        ...     'e': True,
        ...     }}}}
        >>> with mock.open("path/to/function/a", 'w') as f:
        ...     f.write("a content") and None
        >>> with mock.open("path/to/function/b/c", 'w') as f:
        ...     f.write("c content") and None
        >>> with mock.open("path/to/function/b/d", 'w') as f:
        ...     f.write("d content") and None

        >>> runtime = Runtime('path/to/function', config={})

        >>> def stat(filename):
        ...     return namedtuple('Stat', ('st_size',))(5*1024*1024 if filename == "path/to/function/e" else 512)
        >>> mock.mock(runtime, '_stat', stat)

        >>> runtime._walk(runtime.processor, 'positional', custom_keyword='keyword')
        >>> sorted(processed)
        [('path/to/function/a', 'a content', 'positional', 'keyword'),
         ('path/to/function/b/c', 'c content', 'positional', 'keyword'),
         ('path/to/function/b/d', 'd content', 'positional', 'keyword')]
        """

        for path, dirs, files in os.walk(self.root):
            for file in files:
                filename = os.path.join(path, file)

                if self._stat(filename).st_size >= Base.MAX_FILE_SIZE:
                    continue

                with open(filename, 'r', errors='replace') as file:
                    processor(filename, file, *args, **kwargs)

    def _stat(self, filename):
        """ Making os.stat testable again. """
        return os.stat(filename)
