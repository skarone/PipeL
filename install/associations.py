#!python

try:
	import winreg
except ImportError:
	import _winreg as winreg

def set_file_associations(root=r'c:\Python'):
	items = {
		r'Python.NoConFile\shell\open\command': 'C:\Python\pythonw.exe "%1" %*',
		r'Python.CompiledFile\shell\open\command': 'C:\Python\python.exe "%1" %*',
		r'Python.File\shell\open\command': 'C:\Python\python.exe "%1" %*',
		r'Python.File\shell\Edit\command': 'notepad "%1"',
		}
	for key_path, value in items.items():
		winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, key_path)
		key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, key_path, 0,
			winreg.KEY_WRITE)
		reserved = None
		value_name = None
		type = winreg.REG_SZ
		winreg.SetValueEx(key, value_name, reserved, type, value)

if __name__ == '__main__':
	set_file_associations()

