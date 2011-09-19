from setuptools import setup, find_packages
import sys, os

version = '0.0'

setup(name='SilverLining',
      version=version,
      description="A multi-session, multi process python/javascript scriptable browser",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='python cloud browser javascript webkit',
      author='Ivo van der Wijk',
      author_email='silverlining@in.m3r.nl',
      url='http://vanderwijk.info/',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
      ],
      entry_points={
        "console_scripts":[
            "slbrowser=silverlining.main:main",
            "slstandalone=silverlining.standalone:main",
        ]
      },
      )
