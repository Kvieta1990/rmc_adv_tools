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