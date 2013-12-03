from setuptools import setup, find_packages
import sys, os

version = '0.6'

setup(name='rutherford',
      version=version,
      description="Atom feed for Tinkerer",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='atom feed tinkerer',
      author='Sean Gillies',
      author_email='sean.gillies@gmail.com',
      url='http://github.com/sgillies/rutherford',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'pytz', 'tzlocal'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
