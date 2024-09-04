#!/usr/bin/env python

from os import path, walk

from setuptools import find_namespace_packages, setup

NAME = 'oranchada'

VERSION = '1.0.0'

DESCRIPTION = 'Orange add-on for Raman spectroscopy'
README_FILE = path.join(path.dirname(__file__), 'README.pypi')
LONG_DESCRIPTION = open(README_FILE, 'r', encoding='utf-8').read()
LONG_DESCRIPTION_CONTENT_TYPE = 'text/markdown'
URL = 'https://github.com/h2020charisma/oranchada'
AUTHOR = 'IDEAconsult Ltd.'
AUTHOR_EMAIL = 'dev-charisma@ideaconsult.net'
LICENSE = 'MIT'

KEYWORDS = [
    # [PyPi](https://pypi.python.org) packages with keyword "orange3 add-on"
    # can be installed using the Orange Add-on Manager
    'Raman',
    'oranchada',
    'orange3 add-on',
    'spectroscopy',
]

PYTHON_REQUIRES = '>3.8.0'

PACKAGE_DATA = {}

PACKAGE_DIR = { '': 'src' }

PACKAGES = find_namespace_packages(where='src', exclude=['tests'])

DATA_FILES = [
    # Data files that will be installed outside site-packages folder
]

INSTALL_REQUIRES = [
    'Orange3>=3.31.0',
    'fuzzywuzzy~=0.18.0',
    'numpy>=1.18.0',
    'orange-canvas-core>=0.1.24',
    'orange-widget-base>=4.16.1',
    'pip>=9.0',  # same as for Orange 3.28
    'ploomber~=0.23.0',
    'ramanchada2~=1.0',
    'setuptools>=36.3',  # same as for Orange 3.28
    'tables~=3.9.1',
    # 'AnyQt>=0.0.6',
    # 'bottleneck',
    # 'colorcet',
    # 'extranormal3 >=0.0.3',
    # 'h5py',
    # 'lmfit>=1.0.2',
    # 'pebble',
    # 'pillow',
    # 'pyqtgraph>=0.11.1,!=0.12.4',  # https://github.com/pyqtgraph/pyqtgraph/issues/2237
    # 'renishawWiRE>=0.1.8',
    # 'scikit-learn>0.23.0',
    # 'scipy>=1.4.0',
    # 'serverfiles>=0.2',
    # 'spectral>=0.18,!=0.23',
]

EXTRAS_REQUIRE = {
    'test': ['coverage'],
    # 'test': ['pytest', 'coverage'],
    # 'doc': ['sphinx', 'recommonmark', 'sphinx_rtd_theme'],
}

ENTRY_POINTS = {
    # Entry points that marks this package as an orange add-on. If set, addon will
    # be shown in the add-ons manager even if not published on PyPi.
    'orange3.addon': (
        'oranchada = orangecontrib.oranchada',
    ),

    # Entry point used to specify packages containing tutorials accessible
    # from welcome screen. Tutorials are saved Orange Workflows (.ows files).
    'orange.widgets.tutorials': (
        # Syntax: any_text = path.to.package.containing.tutorials
        'infraredtutorials = orangecontrib.oranchada.tutorials',
    ),

    # Entry point used to specify packages containing widgets.
    'orange.widgets': (
        # Syntax: category name = path.to.package.containing.widgets
        # Widget category specification can be seen in
        #    orangecontrib/example/widgets/__init__.py
        'Oranchada Easy = orangecontrib.oranchada.widgets_easy',
        'Oranchada Pro = orangecontrib.oranchada.widgets_pro',
    ),

    # Register widget help
    "orange.canvas.help": (
        'html-index = orangecontrib.oranchada.widgets:WIDGET_HELP_PATH',)

}

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Plugins',
    'Intended Audience :: Developers',
    'Intended Audience :: Education',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3 :: Only',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python',
    'Topic :: Scientific/Engineering :: Artificial Intelligence',
    'Topic :: Scientific/Engineering :: Bio-Informatics',
    'Topic :: Scientific/Engineering :: Visualization',
    'Topic :: Scientific/Engineering',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Software Development :: Libraries',
]

TEST_SUITE = "orangecontrib.oranchada.tests.suite"


def include_documentation(local_dir, install_dir):
    global DATA_FILES

    doc_files = []
    for dirpath, _, files in walk(local_dir):
        doc_files.append((dirpath.replace(local_dir, install_dir),
                          [path.join(dirpath, f) for f in files]))
    DATA_FILES.extend(doc_files)


def setup_package():
    # cmdclass = {
    #     'coverage': CoverageCommand,
    #     'lint': LintCommand,
    # }

    # include_documentation('doc/build/htmlhelp', 'help/orange-spectroscopy')

    setup(
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        classifiers=CLASSIFIERS,
        data_files=DATA_FILES,
        description=DESCRIPTION,
        entry_points=ENTRY_POINTS,
        extras_require=EXTRAS_REQUIRE,
        include_package_data=True,
        install_requires=INSTALL_REQUIRES,
        keywords=KEYWORDS,
        license=LICENSE,
        long_description=LONG_DESCRIPTION,
        long_description_content_type=LONG_DESCRIPTION_CONTENT_TYPE,
        name=NAME,
        package_dir=PACKAGE_DIR,
        package_data=PACKAGE_DATA,
        packages=PACKAGES,
        python_requires=PYTHON_REQUIRES,
        url=URL,
        version=VERSION,
        zip_safe=False,
    )


if __name__ == '__main__':
    setup_package()
