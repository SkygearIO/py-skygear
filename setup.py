from setuptools import setup

from os import path

README = path.abspath(path.join(path.dirname(__file__), 'README.md'))

setup(
      name='pyourd',
      version='0.1',
      packages=['pyourd'],
      description='Python plugin runtime for Ourd',
      long_description=open(README).read(),
      author='Rick Mak',
      author_email='rick.mak@gmail.com',
      url='https://github.com/oursky/pyourd',
      license='MIT',
      install_requires=[
            'strict-rfc3339==0.5',
      ]
)
