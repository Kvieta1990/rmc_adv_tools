"""
RMC config strain analyzer
==========================

Python script for strain field analysis for RMC6F configuration. The script has
been embodied into the RMCProfile release package so that it can be simply
executed as,

.. code-block:: sh

    rmc_strain RMC6F_CONFIG [OPTIONS]

The list of [OPTIONS] is presented below,

-h  Show current help information.

-i  [RMC6F config name] Input RMC6F configuration.

-t  [rms/dgt] Analysis type.

    -r  [Reference RMC6F config file] If 'dgt' analysis is selected,
        one needs to provide the reference RMC6F configuration for
        computing the deformation gradient tensor.

-v  Show version information.

"""
#
# -*- coding: utf-8 -*-
#
from rms_strain import rms_strain_calc
from dgt_tensor import dgt_tensor
from rmc_tools import rmc6f_stuff
import sys
import readline
import os
import atexit

# Some metadata of current program.
version = "0.1"
features = """
 - Microstrain analysis for RMC6F configuration.
 - Deformation gradient tensor analysis for RMC6F configuration.
"""
supported = ["rms", "dgt"]

history_path = os.path.expanduser("~/.pyhistory")


def save_history(hist_path=history_path):
    readline.write_history_file(hist_path)


if os.path.exists(history_path):
    readline.read_history_file(history_path)

atexit.register(save_history)


def doc():
    """
    rmc_strain.py

    Python script for strain field analysis for RMC6F configuration.

    Usage: python rmc_strain.py [OPTIONS]

    Options:

        -h  Show current help information.

        -i  [RMC6F config name] Input RMC6F configuration.

        -t  [rms/dgt] Analysis type.

            -r  [Reference RMC6F config file] If 'dgt' analysis is selected,
                one needs to provide the reference RMC6F configuration for
                computing the deformation gradient tensor.

        -v  Show version information.

    Author: Yuanpeng Zhang
    Email: zyroc1990@gmail.com
    NIST & ORNL
    """


if __name__ == '__main__':

    if (len(sys.argv) == 1) or (len(sys.argv) == 2 and sys.argv[1] == '-v'):
        print("\nVersion: " + str(version))
        print("Features: ", features)
        sys.exit()
    elif len(sys.argv) == 2 and sys.argv[1] == '-h':
        print(doc.__doc__)
        sys.exit()

    try:
        file_name_pos = int(sys.argv.index("-i"))
        file_name = sys.argv[file_name_pos + 1]
        if ".rmc6f" not in file_name:
            print("Input configuration not in RMC6F format!")
            sys.exit()
    except ValueError:
        print(doc.__doc__)
        sys.exit()
    except IndexError:
        print(doc.__doc__)
        sys.exit()

    if "-t" not in sys.argv:
        strain_analysis_type = "rms"
    else:
        strain_analysis_pos = int(sys.argv.index("-t"))
        strain_analysis_type = sys.argv[strain_analysis_pos + 1]

    if strain_analysis_type not in supported:
        print(strain_analysis_type + "not supported yet.")
        print("Only 'rms' and 'dgt' analyses are supported.")
        sys.exit()

    wk_dir = os.path.dirname(os.path.abspath(__file__))
    if strain_analysis_type == "dgt":
        if "-r" in sys.argv:
            ref_config_pos = int(sys.argv.index("-r"))
            file_temp = os.path.join(wk_dir, sys.argv[ref_config_pos + 1])
            ref_config = rmc6f_stuff.RMC6FReader(file_temp)
        else:
            print(doc.__doc__)
            sys.exit()

    file_name = os.path.join(wk_dir, file_name)

    rmc6f_config = rmc6f_stuff.RMC6FReader(file_name)

    if strain_analysis_type == "rms":
        rms_strain_calc.rms_strain_calc(rmc6f_config)
    elif strain_analysis_type == "dgt":
        dgt_tensor.dgt_tensor(ref_config, rmc6f_config)
