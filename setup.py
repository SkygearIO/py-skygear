import sys
from os import path

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

README = path.abspath(path.join(path.dirname(__file__), 'README.md'))

classifiers = [
    'License :: OSI Approved :: Apache Software License',
    'Intended Audience :: Developers',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
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

extras_require={
    'zmq': ['pyzmq>=14.7'],
}

setup(
      name='skygear',
      version='0.11.0',
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
            'bcrypt>=2.0.0',
            'ConfigArgParse>=0.10.0',
            'werkzeug>=0.11.0',
      ],
      extras_require=extras_require,
      cmdclass= {'test': PyTest},
      tests_require=[
            'pytest',
      ] + extras_require['zmq'],
      entry_points={
          'console_scripts': [
              'py-skygear = skygear.bin:main'
          ]
      },
)
