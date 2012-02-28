from setuptools import setup, find_packages

version = '0.4.3'

setup(name='extdirect.django',
      version=version,
      description="Ext.Direct implementation for Django",
      long_description=open("README.md").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Django",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Julien Bouquillon',
      author_email='julien@revolunet.com',
      url='http://github.com/revolunet/extdirect.django/tree/master',
      license='BSD',
      namespace_packages=['extdirect'],
      packages=find_packages(exclude=['ez_setup']),
      test_suite="extdirect.django.tests",
      include_package_data=True,
      package_data={
            'exdirect.django': [
                'extdirect/django/static/css/*',
                'extdirect/django/static/js/*',
                'extdirect/django/static/images/*',
          },
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'extdirect',
      ],
      )
