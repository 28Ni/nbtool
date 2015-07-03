from setuptools import setup

from nbtools._version import __version__

setup(
    name = 'nbtools',
    version = __version__,
    description = 'Tools to manage IPython notebooks',
    url = 'https://github.com/28Ni/nbtools',
    packages = ['nbtools',],
    package_data = {'nbtools': [
        'templates/report.html',
    ]},
    entry_points = {
        'console_scripts': [
            'nbcatsrc = nbtools.nbcatsrc:main',
            'nbdifftoolvim = nbtools.nbdifftoolvim:main',
            'nbvalidate = nbtools.nbvalidate:main',
        ],
    },
    license = 'new or revised BSD license',
    author = 'David Froger',
    author_email = 'david.froger@inria.fr',
    install_requires = ['Jinja2', 'ghdiff', 'nose'],
)
