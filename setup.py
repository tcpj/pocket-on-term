from setuptools import setup
from setuptools import find_packages



setup(name="pocket-on-term_dev",
    version="0.3",
    description="Pocket client for terminals",
    url="http://github.com/jaduse/pocket-on-term",
    author="Jakub Dusek",
    author_email="jaduse@gmail.com",
    license="MIT",
    packages=find_packages(),
    zip_safe=True,
    install_requires=["urwid"],
    entry_points={
            'console_scripts': [
                'pot = pot:main',
        ]
    }

)
