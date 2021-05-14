from distutils.core import setup
import setuptools

setup(name='sofq_calib',
      version='1.0.0',
      author='Yuanpeng Zhang',
      author_email='zyroc1990@gmail.com',
      license='LICENSE.txt',
      description='Tools for calibrating S(Q) against Bragg.',
      long_description=open('README.txt').read(),
      package_data={'sofq_calib': ['stuff/*.txt', 'stuff/*.ico']},
      packages=['sofq_calib'],
      entry_points = {
      'gui_scripts': [
            'sofq_calib = sofq_calib.sofq_calib:main',
        ],
      }
      )
