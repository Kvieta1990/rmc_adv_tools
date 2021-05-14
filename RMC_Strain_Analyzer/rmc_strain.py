"""
RMC config strain analyzer
==========================

Python script for strain field analysis for RMC6F configuration. Details about
strain analysis theoretical description can be found in the following paper,

https://doi.org/10.1107/S1600576719000372

1.  For microstrain analysis (Eqn. 11 in the paper mentioned above), we need a
single RMC6F configuration as the input. For the deformation gradient tensor
analysis, we need the initial and fitted RMC6F configurations as inputs.

The script has been embodied into the RMCProfile release package so that it can
be simply executed as,

.. code-block:: sh

    rmc_strain RMC6F_CONFIG [OPTIONS]

For example, if we want to analyze the microstrain, we can type something like,

.. code-block:: sh

    rmc_strain -i ceriaNano_NP.rmc6f -t rms

If we want to analyze deformation gradient tensor, we can type something like,

.. code-block:: sh

    rmc_strain -i ceriaNano_NP.rmc6f -t dgt -r ceriaNano_NP_init.rmc6f

One can see a list of options by typing

.. code-block:: sh

    rmc_strain -h

The full list of [OPTIONS] is presented below,

-h  Show current help information.

-i  [RMC6F config name] Input RMC6F configuration.

-t  [rms/dgt] Analysis type.

    -r  [Reference RMC6F config file] If 'dgt' analysis is selected,
        one needs to provide the reference RMC6F configuration for
        computing the deformation gradient tensor.

-v  Show version information.

The program will then ask some questions interactively during execution,

a)  If 'rms' type of analysis is selected, the program will ask whether to do
the shell analysis. Then it will ask whether this is for bulk when executing
shell analysis. The program was originally designed for analyzing nanoparticle,
and for the analysis we need to figure out the center and radius of the particle
first. Sometimes, we may also want to run the program against bulk as well just
to make sure, with some confidence, what we obtain from nanoparticle shell
analysis is real. However, for bulk model, it may be tricky to figure out the
center and radius, so we need extra input here.

If we do want to do it for bulk,
we need to first generate a nanoparticle model from the bulk configuration.
To do this, we can use the 'bulk_shells.py' script in the 'NP_Shells' folder.
The usage is similar to 'np_shells.py', and here we only need to generate one
shell (by specifying 'by thickness' for particle generation and particle radius
as the shell thickness), which is actually a nanoparticle in the center. Then we
want to copy the 'shell_0.rmc6f' and 'np_shell_gen.log' to the same directory
where we execute the 'rmc_strain.py' script.

Then the program will ask the minimum number of cells in each shell. We may want
to figure out an estimation based on the total number of cells information
printed out in the log file (see list above).

b) If 'dgt' type of analysis is selected, the program will ask for the cutoff
(in angstrom) for the local deformation analysis. Usually, 10 angstrom should be
good enough. This analysis will take a while since figuring out all neighbors
for all atoms is time consuming.

The output is described as follows, assuming the input fitted RMC6F
configuration is with the name of 'ceriaNano_NP.rmc6f'.

`Output if 'rms' mode selected`,

------------------------------------------------------------

ceriaNano_NP_#.log -- Overall microstrain result

ceriaNano_NP_#_shells.log -- Microstrain for various shells.

------------------------------------------------------------

where '#' represents the smallest integer that is not already existing in the
output file names.

`Output if 'dgt' mode selected`,

-------------------------------------------------------------------------

ceriaNano_NP_dgt.out -- Deformation gradient tensor for each single atom.

ceriaNano_NP_rot.out -- Rotation tensor for each single atom.

ceriaNano_NP_strain.out -- Strain tensor for each single atom.

ceriaNano_NP_strain_invar.out -- Strain invariants for each single atom.

-------------------------------------------------------------------------

Explanation for the output quantities can be again found in the paper,
https://doi.org/10.1107/S1600576719000372.
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

    if (len(sys.argv) == 2) or (len(sys.argv) == 3 and sys.argv[2] == '-v'):
        print("\nVersion: " + str(version))
        print("Features: ", features)
        sys.exit()
    elif len(sys.argv) == 3 and sys.argv[2] == '-h':
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

    # wk_dir = os.path.dirname(os.path.abspath(__file__))
    wk_dir = sys.argv[1]
    print(wk_dir)
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
