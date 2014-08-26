from setuptools import setup, find_packages
 
setup(
	name = "PipeL",
	version = "1.0",
	author = 'Ignacio Urruty',
	description = 'Tools for 3d production',
	packages = find_packages(),
	package_data = {'':['*.hdr','*.jpg','*.png','*.ui','*.qrc','*.html']}
)

