from _winreg import *
 
mapping = { "HKLM":HKEY_LOCAL_MACHINE, "HKCU":HKEY_CURRENT_USER, "HKU":HKEY_USERS }
 
def readSubKeys(hkey, regPath):
	if not pathExists(hkey, regPath):
		return -1
	reg = OpenKey(mapping[hkey], regPath)
	subKeys = []
	noOfSubkeys = QueryInfoKey(reg)[0]
	for i in range(0, noOfSubkeys):
		subKeys.append(EnumKey(reg, i))
	CloseKey(reg)
	return subKeys

def queryValue(hkey, regPath, name):       
	key = OpenKey(mapping[hkey], regPath)
	value, type_id = QueryValueEx(key, name)
	return value
 
def readValues(hkey, regPath):
	if not pathExists(hkey, regPath):
		return -1
	reg = OpenKey( mapping[hkey], regPath )
	values = {}
	noOfValues = QueryInfoKey(reg)[1]
	for i in range(0, noOfValues):
		values[EnumValue(reg, i)[0]] = EnumValue(reg, i)[1]
	CloseKey(reg)
	return values
 
def pathExists(hkey, regPath):
	try:
		reg = OpenKey(mapping[hkey], regPath)
	except WindowsError:
		return False
	CloseKey(reg)
	return True

def set_reg(hkey, regPath, name, value):
	try:
		CreateKey(mapping[hkey], regPath)
		registry_key = OpenKey(mapping[hkey], regPath, 0, KEY_WRITE)
		SetValueEx(registry_key, name, 0, REG_SZ, value)
		CloseKey(registry_key)
		return True
	except WindowsError:
		return False

def get_reg(hkey, regPath, name):
	try:
		registry_key = OpenKey(mapping[hkey], regPath, 0, KEY_READ)
		value, regtype = QueryValueEx(registry_key, name)
		CloseKey(registry_key)
		return value
	except WindowsError:
		return None
