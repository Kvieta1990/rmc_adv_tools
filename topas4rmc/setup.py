from distutils.core import setup
import setuptools
import os


def dirglob(d, *patterns):
    from glob import glob
    rv = []
    for p in patterns:
        rv += glob(os.path.join(d, p))
    return rv


setup(name='topas4rmc',
      version='1.0.0',
      author='Yuanpeng Zhang',
      author_email='zyroc1990@gmail.com',
      license='LICENSE.txt',
      description='Tools for preparing Bragg profile for RMCProfile fitting.',
      long_description=open('README.txt').read(),
      package_data={'topas4rmc': ['stuff/*.txt', 'stuff/*.ico']},
      packages=['topas4rmc'],
      include_package_data=True,
      entry_points={'gui_scripts': ['topas4rmc = topas4rmc.topas4rmc:main']},
      data_files=[
          ('topas4rmc/examples/profile_extraction',
           dirglob('topas4rmc/examples/profile_extraction', '*')),
          ('topas4rmc/examples/resolution_matrix_cw',
           dirglob('topas4rmc/examples/resolution_matrix_cw', '*')),
          ('topas4rmc/examples/resolution_matrix_tof',
           dirglob('topas4rmc/examples/resolution_matrix_tof', '*')),
          ('topas4rmc/examples/rmc_Bragg/check',
           dirglob('topas4rmc/examples/rmc_Bragg/check', '*')),
          ('topas4rmc/examples/rmc_Bragg/config',
           dirglob('topas4rmc/examples/rmc_Bragg/config', '*')),
          ('topas4rmc/examples/rmc_Bragg/profile_prep',
           dirglob('topas4rmc/examples/rmc_Bragg/profile_prep', '*')),
          ('topas4rmc/examples/rmc_Bragg/run',
           dirglob('topas4rmc/examples/rmc_Bragg/run', '*'))
      ]
     )
