@echo off

anaconda upload --force C:\Users\yuanp\anaconda3\conda-bld\win-64\rmc_tools-0.0.1-py37_2.tar.bz2
anaconda upload --force .\linux-32\rmc_tools-0.0.1-py37_2.tar.bz2
anaconda upload --force .\linux-64\rmc_tools-0.0.1-py37_2.tar.bz2
anaconda upload --force .\linux-aarch64\rmc_tools-0.0.1-py37_2.tar.bz2
anaconda upload --force .\linux-armv6l\rmc_tools-0.0.1-py37_2.tar.bz2
anaconda upload --force .\linux-armv7l\rmc_tools-0.0.1-py37_2.tar.bz2
anaconda upload --force .\linux-ppc64le\rmc_tools-0.0.1-py37_2.tar.bz2
anaconda upload --force .\osx-64\rmc_tools-0.0.1-py37_2.tar.bz2
anaconda upload --force .\win-32\rmc_tools-0.0.1-py37_2.tar.bz2