from setuptools import setup
from setuptools import find_packages

setup(name="pot",
      version="0.1",
      description="Pocket client for terminals",
      url="http://github.com/jaduse/pocket-on-term",
      author="Jakub Dusek",
      author_email="jaduse@gmail.com",
      license="MIT",
      packages=find_packages(),
      install_requires=["urwid"],
      scripts=["pot/pot.py"])
