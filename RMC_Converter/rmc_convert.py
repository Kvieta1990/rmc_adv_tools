import sys
import os

import readline
import atexit
from rmc_tools import rmc6f_stuff
from reader import atomeye_reader
from converter import to_lammps
from converter import atomeye_to_rmc

toConfigSupport = ["lammps"]
fromConfigSupport = ["atomeye"]

# Some metadata of current program.
version = "1.0"
features = """
 - Convert RMC6f configuration to LAMMPS format.
 - Convert atomeye configuration dumped from LAMMPS to RMC6F.
 - Specify '-h' flag to show the help information.
"""

history_path = os.path.expanduser("~/.pyhistory")


def save_history(hist_path=history_path):
    import readline
    readline.write_history_file(hist_path)


if os.path.exists(history_path):
    readline.read_history_file(history_path)

atexit.register(save_history)


def main():
    """
    rmc_convert

    Python script for converting between various types of configurations
    and RMC6F configuration.

    The script reads in the last argument as the input configuration file. It will
    analyse the extension to tell this is an RMC6F configuration or not. If yes,
    the script will take the input RMC6F configuration and convert it to specified
    configuration type. Otherwise, the program will take extra flags to tell in
    what format the input configuration is and convert it to RMC6F configuration.

    Options:

        -h  Show current help information.

        If input config is of RMC6F type:

            -o  Output configuration type. The supported inputs are:

                "lammps"

        If input config is not of RMC6F type:

            -i  Input configuration type. The supported inputs are:

                "atomeye"

        If input config is of atomeye type:

            -ref    Reference RMC6F configuration. For example, when we generate
                    the LAMMPS input data file from RMC6F configuration and dump
                    atomeye configuration at the LAMMPS run time. The reference
                    RMC6F configuration needs to be specified here is just the
                    one used to generate the LAMMPS data file.

            -header Number of header lines in the atomeye configuration.

            -from   The source of input atomeye configuration. Suppose it is
                    obtained from LAMMPS dumping, then one needs to specify
                    "lammps" follow current flag. The supported inputs are:

                    "lammps"

    Author: Yuanpeng Zhang
    Email: zyroc1990@gmail.com
    NIST & ORNL
    """

    print("\n======================================================")
    print("===============Welcome to RMC Converter!==============")
    print("=====================Version:", version, "====================")
    print("================Author: Yuanpeng Zhang================")
    print("=============Contact: zyroc1990@gmail.com=============")
    print("======================================================")

    if from_config == "rmc6f":
        rmc6f_config = rmc6f_stuff.RMC6FReader(input_fn)
        if to_config == "lammps":
            to_lammps.to_lammps(rmc6f_config)
    elif from_config == "atomeye":
        try:
            ref_conf_pos = int(sys.argv.index("-ref"))
            ref_config = rmc6f_stuff.RMC6FReader(sys.argv[ref_conf_pos + 1])
            header_pos = int(sys.argv.index("-header"))
            header_num = int(sys.argv[header_pos + 1])
            gen_from_pos = int(sys.argv.index("-from"))
            gen_from = sys.argv[gen_from_pos + 1]
        except ValueError:
            print("Flags error! Use '-h' flag for help.")
            sys.exit()

        atomeye_config = atomeye_reader.AtomeyeReader(gen_from, header_num, input_fn)

        atomeye_to_rmc.atomeye_to_rmc(ref_config, atomeye_config)


if __name__ == '__main__':

    if len(sys.argv) == 1:
        print("Version: " + str(version))
        print("Features: ", features)
        sys.exit()
    elif len(sys.argv) == 2 and sys.argv[1] == '-h':
        print(main.__doc__)
        sys.exit()

    try:
        input_fn = sys.argv[len(sys.argv) - 1]
        input_ext = input_fn.split(".")[1]
        if input_ext == "rmc6f":
            o_pos = sys.argv.index("-o")
            to_config = sys.argv[o_pos + 1]
            from_config = "rmc6f"
        else:
            i_pos = sys.argv.index("-i")
            from_config = sys.argv[i_pos + 1]
    except IndexError or ValueError:
        print("Use '-h' flag for help information!")
        sys.exit()

    main()

    print("\n======================================================")
    print("======================Job Done!=======================")
    print("======================================================")
