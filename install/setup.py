from setuptools import setup, find_packages
 
setup(
	name = "pipel",
	version = "0.1",
	author = 'Ignacio Urruty',
	description = 'Tools for 3d production',
	packages = find_packages(),
	package_data = {'':['*.hdr','*.jpg','*.png','*.ui','*.qrc','*.html']}
)

