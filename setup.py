from distutils.core import setup
from distutils.command.sdist import sdist as _sdist
import os

VERSION = '1.0'

datafiles = [('share/man/man1', ['smugtool.1'])]

class sdist(_sdist):
    """ custom sdist command, to prep smugapi.spec file for inclusion """

    def run(self):
        cmd = (""" sed -e "s/@VERSION@/%s/g" < smugapi.spec.in """ %
               VERSION) + " > smugapi.spec"
        os.system(cmd)

        _sdist.run(self)

setup(name='smugapi',
      version=VERSION,
      description='SmugMug API and utilities',
      author='Chris Lalancette',
      author_email='clalancette@gmail.com',
      license='GPL',
      url='http://github.com/smugapi/smugapi/tree/master',
      py_modules=['smugapi'],
      scripts=['smugtool'],
      data_files = datafiles,
      cmdclass = { 'sdist': sdist }
      )
