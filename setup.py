from setuptools import setup, find_packages

from os import path

README = path.abspath(path.join(path.dirname(__file__), 'README.md'))

classifiers = [
    'License :: OSI Approved :: MIT License',
    'Intended Audience :: Developers',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Operating System :: POSIX',
    'Operating System :: MacOS :: MacOS X',
    'Environment :: Web Environment',
    'Development Status :: 3 - Alpha',
]

setup(
      name='skygear',
      version='0.1',
      packages=find_packages(),
      description='Python plugin runtime for Skygear',
      long_description=open(README).read(),
      classifiers=classifiers,
      author='Rick Mak',
      author_email='rick.mak@gmail.com',
      url='https://github.com/oursky/py-skygear',
      license='MIT',
      install_requires=[
            'pyzmq==14.7',
            'psycopg2==2.6.1',
            'SQLAlchemy==1.0.8',
            'strict-rfc3339==0.5',
            'requests==2.7.0',
      ],
      entry_points={
          'console_scripts': [
              'py-skygear = skygear.bin:main'
          ]
      },
)
