# coding: utf-8
from distutils.core import setup
import py2exe

setup(
    options={'py2exe': {'bundle_files': 1, 'compressed': True}},
    windows=[{'script': 'Main.py'}], 
    zipfile=None,
)