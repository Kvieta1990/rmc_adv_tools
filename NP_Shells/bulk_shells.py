"""
Bulk to shells
==============

This little Python script is basically just calling the method implemented in
`rmc_tools` for dividing bulk RMC6F configuration to shells. The script has been
embodied into RMCProfile release package so that it can be executed within
RMCProfile environment, simply as,

.. code-block:: sh

    bulk_shells RMC6F_CONFIG

Output:
    shell_X.rmc6f -- RMC6F configuration for generated shells.

    np_shell_gen.log -- Log information about shells generation.
"""
#
# -*- coding: utf-8 -*-
#
import sys
import readline
import os
import atexit
from rmc_tools import rmc6f_stuff
from rmc_tools import bulk_stuff

# Some metadata of current program.
version = "0.1"
features = """
 - Subdivide particle into shells.
 - Support single particle only.
"""

history_path = os.path.expanduser("~/.pyhistory")


def save_history(hist_path=history_path):
    import readline
    readline.write_history_file(hist_path)


if os.path.exists(history_path):
    readline.read_history_file(history_path)

atexit.register(save_history)


def main():

    try:
        rmc6fFN = os.path.join(sys.argv[1], sys.argv[2])
        if sys.argv[2] == '' or sys.argv[2] is None:
            print("\nRMC6F configuration file needs to be provided.")
            sys.exit()
    except (OSError, IndexError):
        print("RMC6F configuration file needs to be provided.")
        sys.exit()
    if sys.argv[2] == "-version" or sys.argv[2] == "-v" or sys.argv[2] == "-V":
        print("===================")
        print("Version " + version)
        print("===================")
        print("\nFeatures available:")
        print(features)
        sys.exit()

    print("\n======================================================")
    print("============Welcome to NP shell generator!============")
    print("=====================Version:", version, "====================")
    print("================Author: Yuanpeng Zhang================")
    print("=============Contact: zyroc1990@gmail.com=============")
    print("======================================================")

    rmc6f_config = rmc6f_stuff.RMC6FReader(rmc6fFN)

    bulk_config = bulk_stuff.BulkStuff()
    bulk_config.bulk_to_shells(rmc6f_config)


if __name__ == '__main__':
    main()

    print("\n======================================================")
    print("======================Job Done!=======================")
    print("======================================================")
