import glob
import sys
from os import chdir, environ, mkdir, path, system
from shutil import copyfile, rmtree

from setuptools import Command, find_packages, setup
from setuptools.command.test import test as TestCommand

README = path.abspath(path.join(path.dirname(__file__), 'README.md'))

classifiers = [
    'License :: OSI Approved :: Apache Software License',
    'Intended Audience :: Developers',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Operating System :: POSIX',
    'Operating System :: MacOS :: MacOS X',
    'Environment :: Web Environment',
    'Development Status :: 3 - Alpha',
]

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['skygear']
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

class Doc(Command):
    """Sphinx Document Generation Command"""
    description = 'run sphinx-apidoc'
    user_options = []
    def finalize_options(self):
        pass

    def initialize_options(self):
        pass

    def run(self):
        metadata = self.distribution.metadata
        temp_dir = 'rst'
        chdir('docs')
        if path.exists(temp_dir) and path.isdir(temp_dir):
            rmtree(temp_dir)
        mkdir(temp_dir)
        environ['SPHINX_APIDOC_OPTIONS'] = 'members'
        system('sphinx-apidoc %s -H %s -A %s -V %s -R %s -o %s %s' %
               (path.join('..', 'skygear'),
                metadata.name,
                metadata.author,
                metadata.version,
                metadata.version,
                temp_dir,
                path.join('..', 'skygear')))
        for f in glob.glob(r'*.rst') + ['conf.py']:
            print(f)
            copyfile(f, path.join(temp_dir, f))
        system('sphinx-build %s %s' % (temp_dir, '_build'))
        rmtree(temp_dir)

extras_require={
    'zmq': ['pyzmq>=14.7'],
    'doc': ['Sphinx>=1.6.3',
            'sphinx-rtd-theme>=0.2.4',
            'sphinxcontrib-napoleon>=0.6.1',
            'sphinxcontrib-websupport>=1.0.1']
}

setup(
      name='skygear',
      version='1.4.0',
      packages=find_packages(),
      description='Python plugin runtime for Skygear',
      long_description=open(README).read(),
      classifiers=classifiers,
      author='Rick Mak',
      author_email='rick.mak@gmail.com',
      url='https://github.com/SkygearIO/py-skygear',
      license='Apache License, Version 2.0',
      install_requires=[
            'psycopg2>=2.6.1',
            'SQLAlchemy>=1.0.8',
            'strict-rfc3339>=0.5',
            'requests',
            'websocket-client>=0.32.0',
            'bcrypt==2.0.0',
            'ConfigArgParse>=0.12.0',
            'werkzeug>=0.11.0',
            'boto3>=1.4',
      ],
      extras_require=extras_require,
      cmdclass= {'test': PyTest, 'doc': Doc},
      tests_require=[
            'pytest',
      ] + extras_require['zmq']
        + extras_require['doc'],
      entry_points={
          'console_scripts': [
              'py-skygear = skygear.bin:main'
          ]
      },
)
