from distutils.core import setup
import py2exe, sys, os

sys.argv.append('py2exe')


setup(
    options = {'py2exe': { "skip_archive": True,
            "includes" : ['sys', 'tempfile', 'zipfile', 'mmap', 'encodings',
                          'json', 'hashlib', 'datetime', 'struct',
                          'os', 'time', 'random', 'math', 'xmlrpclib']}},
    windows = ["install.py"],
)

