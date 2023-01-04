#!/usr/bin/env python

import os
from os import walk, path
import subprocess
import sys

from setuptools import setup, find_packages, Command

PACKAGES = find_packages()

PACKAGE_DATA = {}

README_FILE = os.path.join(os.path.dirname(__file__), 'README.pypi')
LONG_DESCRIPTION = open(README_FILE).read()

DATA_FILES = [
    # Data files that will be installed outside site-packages folder
]

ENTRY_POINTS = {
    # Entry points that marks this package as an orange add-on. If set, addon will
    # be shown in the add-ons manager even if not published on PyPi.
    'orange3.addon': (
        'charisma = orangecontrib.charisma',
    ),

    # Entry point used to specify packages containing tutorials accessible
    # from welcome screen. Tutorials are saved Orange Workflows (.ows files).
    'orange.widgets.tutorials': (
        # Syntax: any_text = path.to.package.containing.tutorials
        'infraredtutorials = orangecontrib.charisma.tutorials',
    ),

    # Entry point used to specify packages containing widgets.
    'orange.widgets': (
        # Syntax: category name = path.to.package.containing.widgets
        # Widget category specification can be seen in
        #    orangecontrib/example/widgets/__init__.py
        'charisma = orangecontrib.charisma.widgets',
    ),

    # Register widget help
    "orange.canvas.help": (
        'html-index = orangecontrib.charisma.widgets:WIDGET_HELP_PATH',)

}

KEYWORDS = [
    # [PyPi](https://pypi.python.org) packages with keyword "orange3 add-on"
    # can be installed using the Orange Add-on Manager
    'orange3 add-on',
    'spectroscopy',
    'Raman'
]


TEST_SUITE = "orangecontrib.charisma.tests.suite"

def include_documentation(local_dir, install_dir):
    global DATA_FILES

    doc_files = []
    for dirpath, _, files in walk(local_dir):
        doc_files.append((dirpath.replace(local_dir, install_dir),
                          [path.join(dirpath, f) for f in files]))
    DATA_FILES.extend(doc_files)

if __name__ == '__main__':

    cmdclass = {
        #'coverage': CoverageCommand,
        #'lint': LintCommand,
    }

    #include_documentation('doc/build/htmlhelp', 'help/orange-spectroscopy')

    setup(
        name="charisma",
        python_requires='>3.8.0',
        description='Extends Orange with Raman spectroscopy',
        long_description=LONG_DESCRIPTION,
        long_description_content_type='text/markdown',
        author='Ideaconsult Ltd.',
        author_email='dev-charisma@ideaconsult.net',
        version="0.0.1",
        packages=PACKAGES,
        package_data=PACKAGE_DATA,
        data_files=DATA_FILES,
        install_requires=[
            'setuptools>=36.3',  # same as for Orange 3.28
            'pip>=9.0',  # same as for Orange 3.28
            'numpy>=1.18.0',
            'Orange3>=3.31.0',
            'orange-canvas-core>=0.1.24',
            'orange-widget-base>=4.16.1',
            #'scipy>=1.4.0',
            #'scikit-learn>0.23.0',
            #'spectral>=0.18,!=0.23',
            #'serverfiles>=0.2',
            #'AnyQt>=0.0.6',
            #'pyqtgraph>=0.11.1,!=0.12.4',  # https://github.com/pyqtgraph/pyqtgraph/issues/2237
            #'colorcet',
            #'h5py',
            #'extranormal3 >=0.0.3',
            #'renishawWiRE>=0.1.8',
            #'pillow',
            #'lmfit>=1.0.2',
            #'bottleneck',
            #'pebble',
            'ramanchada2'
        ],
        extras_require={
            'test': ['coverage']
        },
        entry_points=ENTRY_POINTS,
        keywords=KEYWORDS,
        namespace_packages=['orangecontrib'],
        #test_suite=TEST_SUITE,
        include_package_data=True,
        zip_safe=False,
        url="https://github.com/h2020charisma/ramanchada-orange",
        cmdclass=cmdclass,
        license='MIT',
    )
