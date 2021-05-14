"""
Nano RMC6F configuration processing
===================================

This modules holds stuff relevant to processing nano RMC6F configurations.

"""
#
# -*- coding: utf-8 -*-
#
from rmc_tools import rmc6f_stuff
from math import floor
import os
import timeit
import datetime


class NanoStuff(object):
    """
    RMC6F nano configuration processing class.

    This class contains methods for processing naon RMC6F configurations.
    """

    def __init__(self):
        self.centPos = []
        self.centPosInt = []
        self.NPRadius = 0
        self.shellThickness = 0

    def cent_r_rad_config(self, log_file, rmc6f_config):

        check_step = 0.02

        start = timeit.default_timer()

        file_i = open(log_file, "r")
        for i in range(7):
            file_i.readline()
        line = file_i.readline()
        self.centPos = [float(x) for x in line.split()[2:]]
        self.centPosInt = [2 * x - 1.0 for x in self.centPos]
        none_beyond = False
        check_rad = check_step
        while not none_beyond:
            some_beyond = False
            for atom in rmc6f_config.atomsCoordInt:
                dist_temp = rmc6f_stuff.dist_calc_coord(self.centPosInt, atom, rmc6f_config.vectors)
                if dist_temp > check_rad:
                    some_beyond = True
                    break
            if some_beyond:
                check_rad += check_step
            else:
                none_beyond = True

        self.NPRadius = check_rad

        stop = timeit.default_timer()

        print("\n--------------------------------------------------")
        print("Particle center and radius successfully extracted.")
        print("Time taken:{0:11.3F} s".format(stop - start))
        print("--------------------------------------------------")
        print("Particle radius = {0:10.2F} Angstrom".format(self.NPRadius))
        print("--------------------------------------------------")

    # Method for figuring out the center and radius of input nanoparticle.
    def cent_rad_config(self, rmc6f_config):
        """
        Method for figuring out the center and radius of the input RMC6F nano configuration.

        Provided nano RMC6F configuration, this method can extract information about the \
        center and radius of the input nanoparticle configuration.

        Arguments:
            rmc6f_config {Object} -- Instance of `RMC6FReader` class

        Output:
           The center and radius of input nanoparticle configuration can be accessed \
           from instance variable `centPos` and `NPRadius`.
        """
        check_step = 0.02

        start = timeit.default_timer()

        print("\nConfiguring particle center and radius...")

        x_temp = [p[0] for p in rmc6f_config.atomsCoord]
        y_temp = [p[1] for p in rmc6f_config.atomsCoord]
        z_temp = [p[2] for p in rmc6f_config.atomsCoord]

        self.centPos = [sum(x_temp) / rmc6f_config.numAtoms,
                        sum(y_temp) / rmc6f_config.numAtoms,
                        sum(z_temp) / rmc6f_config.numAtoms]

        self.centPosInt = [2 * x - 1.0 for x in self.centPos]

        none_beyond = False
        check_rad = check_step
        while not none_beyond:
            some_beyond = False
            for atom in rmc6f_config.atomsCoordInt:
                dist_temp = rmc6f_stuff.dist_calc_coord(self.centPosInt, atom, rmc6f_config.vectors)
                if dist_temp > check_rad:
                    some_beyond = True
                    break
            if some_beyond:
                check_rad += check_step
            else:
                none_beyond = True

        self.NPRadius = check_rad

        stop = timeit.default_timer()

        print("\n--------------------------------------------------")
        print("Particle center and radius successfully extracted.")
        print("Time taken:{0:11.3F} s".format(stop - start))
        print("--------------------------------------------------")
        print("Particle radius = {0:10.2F} Angstrom".format(self.NPRadius))
        print("--------------------------------------------------")

    # Method for dividing nanoparticle into various shells.
    def np_to_shells(self, rmc6f_config):
        """
        Method for grabbing shells from nano RMC6F configuration.

        Provided nano RMC6F configuration, this method can extract shells from it. \
        The center of the provided nanoparticle will be figured out automatically.

        Arguments:
            rmc6f_config {Object} -- Instance of `RMC6FReader` class

        Output:
            shell_X.rmc6f -- RMC6F configuration for generated shells.

            np_shell_gen.log -- Log information about shells generation.
        """
        print("\n****************************************************")
        print("1->by thickness, 2->by number of atoms")
        print("****************************************************")
        div_scheme = int(input("Please select a way to divide particle into shells: "))

        while div_scheme != 1 and div_scheme != 2:
            print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!!!!'1' and '2' are only accepted inputs!!!!")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

            print("\n****************************************************")
            print("1->by thickness, 2->by number of atoms")
            print("****************************************************")
            div_scheme = int(input("Please select a way to divide particle into shells: "))

        if div_scheme == 1:

            self.shellThickness = float(input("\nPlease input shell thickness for the analysis: "))

            start = timeit.default_timer()

            print("\nDividing particle to various shells...")

            atoms_include = [i * 0 for i in range(rmc6f_config.numAtoms)]
            atoms_to_check = [i for i, x in enumerate(atoms_include) if x == 0]

            num_shells = floor(self.NPRadius / self.shellThickness)
            shell_atoms = []

            print("\nShells to configure: ", end='', flush=True)
            for i in range(num_shells + 1):
                print("*", end='', flush=True)

            print("\nShells configured:   ", end='', flush=True)
            for i in range(num_shells):
                shell_atoms.append([])
                low_lim = i * self.shellThickness
                hi_lim = (i + 1) * self.shellThickness
                for ii in atoms_to_check:
                    dist_temp = rmc6f_stuff.dist_calc_coord(self.centPosInt, rmc6f_config.atomsCoordInt[ii],
                                                rmc6f_config.vectors)
                    if low_lim <= dist_temp < hi_lim:
                        shell_atoms[i].append(ii)
                        atoms_include[ii] = 1
                atoms_to_check = [i for i, x in enumerate(atoms_include) if x == 0]
                print(".", end='', flush=True)

            shell_atoms.append(atoms_to_check)
            num_shells += 1
            print(".")

            stop = timeit.default_timer()

            print("\n\n--------------------------------------------")
            print("Particle successfully divided to " + str(num_shells) + " shells.")
            print("Time taken:{0:11.3F} s".format(stop - start))
            print("--------------------------------------------")
        elif div_scheme == 2:

            print("\n*************************************************")
            for i in range(rmc6f_config.numTypeAtom):
                print(str(i+1) + "->" + rmc6f_config.atomTypes[i] + " ", end='', flush=True)
            print("\n*************************************************")
            at_to_focus = int(input("Please input an atom type to focus on: "))

            print("\n------------------------------------------")
            print("Total number of atoms selected: {0:10d}".
                  format(rmc6f_config.numAtomEachType[at_to_focus - 1]))
            print("------------------------------------------")

            surf_layer_thkness = float(input("\nPlease input an estimated surface layer thickness: "))
            min_num_in_shell = int(input("Please input minimum number of " +
                                         rmc6f_config.atomTypes[at_to_focus - 1] + " atoms in shell: "))

            start = timeit.default_timer()

            print("\nDividing particle to various shells...")

            atoms_include = [i * 0 for i in range(rmc6f_config.numAtoms)]
            atoms_to_check = [i for i, x in enumerate(atoms_include) if x == 0]

            low_lim = 0
            hi_lim = 0
            low_lim_out = []
            hi_lim_out = []
            check_step = 0.5
            shell_atoms = []
            shell_processed = 0
            enough_left = True
            print("Shells configured (represented by '.'): ", end='', flush=True)
            while (hi_lim < self.NPRadius - surf_layer_thkness) and enough_left:
                shell_atoms.append([])
                natoms_focus = 0
                while natoms_focus < min_num_in_shell:
                    hi_lim += check_step
                    list_temp = []
                    burst = False
                    for ii in atoms_to_check:
                        dist_temp = rmc6f_stuff.dist_calc_coord(self.centPosInt, rmc6f_config.atomsCoordInt[ii],
                                                    rmc6f_config.vectors)
                        if low_lim <= dist_temp < hi_lim:
                            list_temp.append(ii)
                    space_left = min_num_in_shell - natoms_focus
                    to_eat = 0
                    for item in list_temp:
                        if rmc6f_config.atomsEle[item] == rmc6f_config.atomTypes[at_to_focus - 1]:
                            to_eat += 1
                    if space_left < int(0.1 * float(min_num_in_shell)) and \
                       to_eat > int(0.15 * float(min_num_in_shell)):
                        burst = True
                    if not burst:
                        shell_atoms[shell_processed].extend(list_temp)
                        for item in list_temp:
                            atoms_include[item] = 1
                            if rmc6f_config.atomsEle[item] == rmc6f_config.atomTypes[at_to_focus - 1]:
                                natoms_focus += 1
                    else:
                        hi_lim -= check_step
                        break

                    atoms_to_check = [i for i, x in enumerate(atoms_include) if x == 0]

                low_lim_out.append(low_lim)
                hi_lim_out.append(hi_lim)

                shell_processed += 1
                low_lim = hi_lim

                atoms_left = 0
                for i in range(rmc6f_config.numAtoms):
                    if rmc6f_config.atomsEle[i] == rmc6f_config.atomTypes[at_to_focus - 1] and \
                       atoms_include[i] == 0:
                        atoms_left += 1
                if atoms_left < 2 * min_num_in_shell:
                    enough_left = False

                print(".", end='', flush=True)

            shell_atoms.append(atoms_to_check)
            hi_lim_out[shell_processed - 1] = self.NPRadius
            print(".")

            num_shells = shell_processed

            for i in range(num_shells):
                shell_atoms[i].sort()

            stop = timeit.default_timer()

            print("\n--------------------------------------------")
            print("Particle successfully divided to " + str(num_shells) + " shells.")
            print("Time taken:{0:11.3F} s".format(stop - start))
            print("--------------------------------------------")

        dir_exist = True
        i = 1
        while dir_exist:
            dir_check = rmc6f_config.fileName.split(".")[0] + "_np_shells_" + str(i)
            if not os.path.exists(dir_check):
                dir_exist = False
                dir_use = dir_check
            i += 1

        os.mkdir(dir_use)

        for i in range(num_shells):
            atoms_ele = []
            atoms_line = []
            line_num = 0
            for item in shell_atoms[i]:
                line_num += 1
                atoms_ele.append(rmc6f_config.atomsEle[item])
                line_temp = rmc6f_config.atomsLine[item]
                line_new = str(line_num) + " " + " ".join(line_temp.split()[1:]) + "\n"
                atoms_line.append(line_new)

            atoms_ele_uniq = sorted(set(atoms_ele), key=atoms_ele.index)

            num_each_type = []
            for j in range(len(atoms_ele_uniq)):
                num_each_type.append(str(atoms_ele.count(atoms_ele_uniq[j])))

            num_rho_new = rmc6f_config.initNumRho * \
                float(len(shell_atoms[i])) / \
                float(rmc6f_config.numAtoms)

            header = rmc6f_config.header.copy()
            for j in range(len(header)):
                if "Number of atoms:" in header[j]:
                    header[j] = "Number of atoms: " + str(len(shell_atoms[i])) + "\n"
                if "Atom types present:" in header[j]:
                    header[j] = "Atom types present: " + " ".join(atoms_ele_uniq) + "\n"
                if "Number of types of atoms:" in header[j]:
                    header[j] = "Number of types of atoms: " + str(len(atoms_ele_uniq)) + "\n"
                if "Number of each atom type:" in header[j]:
                    header[j] = "Number of each atom type: " + " ".join(num_each_type) + "\n"
                if "Number density (Ang^-3):" in header[j]:
                    header[j] = "Number density (Ang^-3):" + " {0:.6f}".format(num_rho_new) + "\n"

            file_out = open(os.path.join(dir_use, "shell_" + str(i)) + ".rmc6f", "w")
            for item in header:
                file_out.write(item)
            for item in atoms_line:
                file_out.write(item)
            file_out.close()

        now = datetime.datetime.now()
        log_file = open(os.path.join(dir_use, "np_shell_gen.log"), "w")
        log_file.write("==================================\n")
        log_file.write("Log file for np_to_shells routine.\n")
        log_file.write("==================================\n")
        log_file.write("Time stamp: " + str(now)[:19] + "\n")
        if div_scheme == 1:
            log_file.write("================================================\n")
            log_file.write("Particle divided into shells by equal thickness.\n")
            log_file.write("Shell thickness used: {0:10.1F}\n".format(self.shellThickness))
            log_file.write("Number of shells generated: {0:10d}\n".format(num_shells))
            log_file.write("================================================")
        else:
            log_file.write("================================================================\n")
            log_file.write("Particle divided into shells by equal (roughly) number of atoms.\n")
            log_file.write("Estimated surface shell thickness: {0:10.1F}\n".format(surf_layer_thkness))
            log_file.write("Atom type focused: {0:2s}\n".format(rmc6f_config.atomTypes[at_to_focus - 1]))
            log_file.write("Minimum number of {0:2s} atom in each shell: {1:10d}\n".
                           format(rmc6f_config.atomTypes[at_to_focus - 1], min_num_in_shell))
            log_file.write("Number of shells generated: {0:10d}\n".format(num_shells))
            log_file.write("================================================================\n")
            log_file.write("Lower and upper limit of each shell:\n")
            log_file.write("================================================================\n")
            log_file.write("{0:>10s}{1:>10s}\n".format("R_min", "R_max"))
            for i in range(num_shells):
                log_file.write("{0:10.2F}{1:10.2F}\n".format(low_lim_out[i], hi_lim_out[i]))
            log_file.write("================================================================")
        log_file.close()

        print("\n--------------------------------------------")
        print("RMC6F configs of shells output to directory:")
        print("--------------------------------------------")
        print(dir_use)
        print("--------------------------------------------")
