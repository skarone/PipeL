from distutils.core import setup
import py2exe
 
setup(
    console = ['managerUI.py'],
    options = {
        "py2exe" : {
			"skip_archive": True,
            "includes" : ['sys', 'tempfile', 'zipfile', 'mmap', 'encodings',
                          'json', 'hashlib', 'datetime', 'struct',
                          'os', 'time', 'random', 'math', 'xmlrpclib']
        }
    }
)

"""
python basic_setup.py py2exe
"""
