from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in meeting/__init__.py
from meeting import __version__ as version

setup(
	name="meeting",
	version=version,
	description="~/frappe-bennch/apps$ bench --site shine.in uninstall-app meeting",
	author="Uninstalling App meeting from Site shine.in...",
	author_email="All doctypes (including custom), modules related to this app will be deleted. Are you sure you want to continue? [y/N]: y",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
