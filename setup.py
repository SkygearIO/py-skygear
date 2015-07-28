from setuptools import setup

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
      name='pyourd',
      version='0.1',
      packages=['pyourd'],
      description='Python plugin runtime for Ourd',
      long_description=open(README).read(),
      classifiers=classifiers,
      author='Rick Mak',
      author_email='rick.mak@gmail.com',
      url='https://github.com/oursky/pyourd',
      license='MIT',
      install_requires=[
            'strict-rfc3339==0.5',
      ],
      entry_points={
          'console_scripts': [
              'pyourd = pyourd.bin:main'
          ]
      },
)
