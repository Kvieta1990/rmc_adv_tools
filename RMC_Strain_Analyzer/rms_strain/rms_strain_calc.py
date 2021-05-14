# -*- coding: utf-8 -*-
#
# rms_strain_calc.py
#
# Module containing procedures for calculating the root-mean-square strain,
# which is also termed as microstrain in whole pattern fitting.
#
# Yuanpeng Zhang @ 06/20/19 Thursday
# NIST & ORNL
#
import numpy as np
from numpy import linalg as la
import timeit
import os
import datetime
import sys
from rmc_tools import nano_stuff, rmc6f_stuff
from random import random


def rms_strain_calc(rmc6f_config):

    start = timeit.default_timer()

    print("\nCalculating micro strain...")

    print("\nFirst, figuring out unique cells existing...")

    # Figure out unique cell list.
    cells = []
    cell_num = 0

    for i in range(rmc6f_config.numAtoms):
        cell_temp = [int(x) for x in rmc6f_config.atomsLine[i].split()[7:]]
        ref_temp = int(rmc6f_config.atomsLine[i].split()[6])
        atom_i = i
        if i == 0:
            cell_exist = False
        else:
            cell_exist = False
            index = 0
            for item in cells:
                if cell_temp[0] == item[0][0] and \
                        cell_temp[1] == item[0][1] and \
                        cell_temp[2] == item[0][2]:
                    cell_exist = True
                    break
                index += 1

        if not cell_exist:
            cells.append([cell_temp, {}])
            cells[cell_num][1][ref_temp] = atom_i
            cell_num += 1
        else:
            cells[index][1][ref_temp] = atom_i

    # Store cell string for later search purpose. For example, cell '1 2 3' will
    # be stored as '123'.
    cells_string = []
    for item in cells:
        str_temp = str(item[0][0]) + "," + str(item[0][1]) + "," + str(item[0][2])
        cells_string.append(str_temp)

    # Configure number of atoms in one unit cell, assuming that we do have
    # at least one full unit cell.
    max_ref_num = 0
    for item in cells:
        if len(item[1]) > max_ref_num:
            max_ref_num = len(item[1])
    for i in range(len(cells)):
        if len(cells[i][1]) < max_ref_num:
            cells[i].append([0])
        else:
            cells[i].append([1])

    print("Unique cells successfully configured.")

    print("\nNow, figuring out neighbours of cells...")

    # Figure out neighbouring cells.
    for i in range(len(cells)):
        cells[i].append([])

        if cells[i][0][0] == 0:
            a_min_1 = rmc6f_config.scDim[0] - 1
        else:
            a_min_1 = cells[i][0][0] - 1
        str_temp = str(a_min_1) + "," + str(cells[i][0][1]) + "," + str(cells[i][0][2])
        if str_temp in cells_string:
            cells[i][3].append(cells_string.index(str_temp))

        if cells[i][0][0] == rmc6f_config.scDim[0] - 1:
            a_plus_1 = 0
        else:
            a_plus_1 = cells[i][0][0] + 1
        str_temp = str(a_plus_1) + "," + str(cells[i][0][1]) + "," + str(cells[i][0][2])
        if str_temp in cells_string:
            cells[i][3].append(cells_string.index(str_temp))

        if cells[i][0][1] == 0:
            b_min_1 = rmc6f_config.scDim[1] - 1
        else:
            b_min_1 = cells[i][0][1] - 1
        str_temp = str(cells[i][0][0]) + "," + str(b_min_1) + "," + str(cells[i][0][2])
        if str_temp in cells_string:
            cells[i][3].append(cells_string.index(str_temp))

        if cells[i][0][1] == rmc6f_config.scDim[1] - 1:
            b_plus_1 = 0
        else:
            b_plus_1 = cells[i][0][1] + 1
        str_temp = str(cells[i][0][0]) + "," + str(b_plus_1) + "," + str(cells[i][0][2])
        if str_temp in cells_string:
            cells[i][3].append(cells_string.index(str_temp))

        if cells[i][0][2] == 0:
            c_min_1 = rmc6f_config.scDim[2] - 1
        else:
            c_min_1 = cells[i][0][2] - 1
        str_temp = str(cells[i][0][0]) + "," + str(cells[i][0][1]) + "," + str(c_min_1)
        if str_temp in cells_string:
            cells[i][3].append(cells_string.index(str_temp))

        if cells[i][0][2] == rmc6f_config.scDim[2] - 1:
            c_plus_1 = 0
        else:
            c_plus_1 = cells[i][0][2] + 1
        str_temp = str(cells[i][0][0]) + "," + str(cells[i][0][1]) + "," + str(c_plus_1)
        if str_temp in cells_string:
            cells[i][3].append(cells_string.index(str_temp))

    print("Neighbours of cells successfully configured.")

    print("\nChecking completeness of cells...")

    # Checking whether a cell should be included in calculating the unit cell
    # parameter. There are three criteria here:
    # 1. The cell should be full, i.e. no atoms missing.
    # 2. All neighbours should be present, namely, up, down, left, right, forward and backward.
    # 3. The neighbouring cells should also be full.
    for i in range(len(cells)):
        cell_full = (cells[i][2][0] == 1)
        cell_neigh_full = (len(cells[i][3]) == 6)
        cell_neighs_full = True
        for item in cells[i][3]:
            if cells[item][2][0] == 0:
                cell_neighs_full = False
                break
        if cell_full and cell_neigh_full and cell_neighs_full:
            cells[i].append([1])
        else:
            cells[i].append([0])

    print("Cells completeness successfully configured.")

    print("\nCalculating cell parameters...")

    # Calculating the cell parameter.
    a_list = []
    valid_cell_num = 0
    for item in cells:
        if item[4][0] == 1:
            a_temp = 0.0
            valid_cell_num += 1
            for k in item[1]:
                atom_1 = item[1][k]
                for i in range(6):
                    atom_2 = cells[item[3][i]][1][k]
                    if i < 2:
                        vec_t = abs(rmc6f_config.atomsCoord[atom_1][0] -
                                    rmc6f_config.atomsCoord[atom_2][0])
                    elif i < 4:
                        vec_t = abs(rmc6f_config.atomsCoord[atom_1][1] -
                                    rmc6f_config.atomsCoord[atom_2][1])
                    else:
                        vec_t = abs(rmc6f_config.atomsCoord[atom_1][2] -
                                    rmc6f_config.atomsCoord[atom_2][2])
                    if vec_t > 0.5:
                        vec_t = 1 - vec_t
                    latt_a = np.asarray(rmc6f_config.vectors[0])
                    a_temp += (vec_t * la.norm(latt_a))
                    # if (vec_t * la.norm(latt_a) - 5.41046) > 1E-8:
                    #     print(item, k, i)

            a_list.append(a_temp/(float(len(item[1])) * 6.0))

    if valid_cell_num == 0:
        print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!!!!!!!!!!No valid cells found!!!!!!!!!!!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        sys.exit()

    print("Lattice parameters of cells successfully calculated.")

    # Calculate the micro strain.
    a_bar = sum(a_list) / len(a_list)

    sum_t = 0
    for item in a_list:
        sum_t += (item / a_bar - 1)**2
    micro_strain = np.sqrt(sum_t / float(len(a_list)))
    ms_s_err = np.sqrt(2 * micro_strain**4 / (float(len(a_list) - 1)))

    file_exist = True
    i = 1
    while file_exist:
        file_check = rmc6f_config.fileName.split(os.sep)[-1].split(".")[0] + "_" + str(i) + ".log"
        if not os.path.exists(file_check):
            file_exist = False
            file_use = file_check
        i += 1

    now = datetime.datetime.now()
    log_file = open(file_use, "w")
    log_file.write("==================================\n")
    log_file.write("Log file for microstrain analysis.\n")
    log_file.write("==================================\n")
    log_file.write("Time stamp: " + str(now)[:19] + "\n")
    log_file.write("==================================\n")
    log_file.write("Total number of cells: {0:10d}\n".format(len(cells)))
    log_file.write("Number of valid cells: {0:10d}\n".format(valid_cell_num))
    log_file.write("Microstrain: {0:8.6F} +/- {1:<8.6F}\n".format(micro_strain, ms_s_err))
    log_file.write("==================================")

    log_file.close()

    stop = timeit.default_timer()

    print("\n------------------------------------------")
    print("Microstrain = {0:8.6F} +/- {1:<8.6F}".format(micro_strain, ms_s_err))
    print("Time taken:{0:11.3F} s".format(stop - start))
    print("------------------------------------------")
    print("Log information can be found here:")
    print("------------------------------------------")
    print(file_use)
    print("------------------------------------------")

    shell_analysis = input("\nDo you want to carry out shell analysis ([y]/n)?")
    if shell_analysis.upper() == "N":
        sys.exit()

    print("\nAnalyzing microstrain for shells...")

    for i in range(len(cells)):
        cells[i].append([0])

    cell_shell = []

    nano_particle = nano_stuff.NanoStuff()
    test_bulk = input("\nIs this for bulk ([n]/y)?")
    if test_bulk.upper() == "Y":
        nano_particle.centPosInt = [2.0 * random() - 1.0, 2.0 * random() - 1.0,
                                    2.0 * random() - 1.0]
        print("\n-----------------------------------------------------")
        print("Center of the analysis sphere set to be (fractional):")
        print("{0:16.13F},{1:16.13F},{2:16.13F}".format((nano_particle.centPosInt[0] + 1.0) / 2.0,
                                                      (nano_particle.centPosInt[1] + 1.0) / 2.0,
                                                      (nano_particle.centPosInt[2] + 1.0) / 2.0))
        print("-----------------------------------------------------")
        nano_particle.NPRadius = float(input("\nPlease input radius of the analysis sphere (in angstrom): "))
    else:
        nano_particle.cent_rad_config(rmc6f_config)

    min_num_in_shell = int(input("\nPlease input minimum number of cells in shell: "))

    start = timeit.default_timer()

    low_lim = 0
    hi_lim = 0
    low_lim_out = []
    hi_lim_out = []
    check_step = 0.5
    shell_processed = 0
    cells_configured = 0
    enough_left = True

    while (hi_lim < nano_particle.NPRadius) and enough_left:
        cell_shell.append([])
        cell_num = 0
        while cell_num < min_num_in_shell:
            hi_lim += check_step
            list_temp = []
            burst = False
            for ii in range(len(cells)):
                if cells[ii][4][0] == 1:
                    dist_temp = rmc6f_stuff.dist_calc_coord(nano_particle.centPosInt,
                                                            rmc6f_config.atomsCoordInt[cells[ii][1][1]],
                                                            rmc6f_config.vectors)
                    if (low_lim <= dist_temp < hi_lim) and cells[ii][5][0] == 0:
                        list_temp.append(ii)
            space_left = min_num_in_shell - cell_num
            to_eat = len(list_temp)
            if space_left < int(0.1 * float(min_num_in_shell)) and \
                    to_eat > int(0.15 * float(min_num_in_shell)):
                burst = True
            if not burst:
                cell_shell[shell_processed].extend(list_temp)
                cells_configured += len(list_temp)
                for item in list_temp:
                    cells[item][5][0] = 1
                cell_num += len(list_temp)
            else:
                hi_lim -= check_step
                break

        low_lim_out.append(low_lim)
        hi_lim_out.append(hi_lim)

        shell_processed += 1
        low_lim = hi_lim

        cells_left = len(a_list) - cells_configured
        if cells_left < 2 * min_num_in_shell:
            enough_left = False

    cell_shell.append([])

    for i in range(len(cells)):
        if cells[i][4][0] == 1 and cells[i][5][0] == 0:
            cell_shell[shell_processed].append(i)
    hi_lim_out[shell_processed - 1] = nano_particle.NPRadius

    shell_ms = []
    for shell in cell_shell:
        a_list = []
        for item in shell:
            a_temp = 0.0
            for k in cells[item][1]:
                atom_1 = cells[item][1][k]
                for i in range(6):
                    atom_2 = cells[cells[item][3][i]][1][k]
                    if i < 2:
                        vec_t = abs(rmc6f_config.atomsCoord[atom_1][0] -
                                    rmc6f_config.atomsCoord[atom_2][0])
                    elif i < 4:
                        vec_t = abs(rmc6f_config.atomsCoord[atom_1][1] -
                                    rmc6f_config.atomsCoord[atom_2][1])
                    else:
                        vec_t = abs(rmc6f_config.atomsCoord[atom_1][2] -
                                    rmc6f_config.atomsCoord[atom_2][2])
                    if vec_t > 0.5:
                        vec_t = 1 - vec_t
                    latt_a = np.asarray(rmc6f_config.vectors[0])
                    a_temp += (vec_t * la.norm(latt_a))

            a_list.append(a_temp / (float(len(cells[item][1])) * 6.0))

        # Calculate the micro strain.
        a_bar = sum(a_list) / len(a_list)

        # Refer to the following discussion about the calculation
        # of variance of microstrain (which by itself is a variance).
        # In this case, we are calculating the variance of variance.
        sum_t = 0
        for item in a_list:
            sum_t += (item / a_bar - 1) ** 2
        micro_strain = np.sqrt(sum_t / float(len(a_list)))
        ms_s_err = np.sqrt(2 * micro_strain ** 4 / (float(len(a_list) - 1)))
        shell_ms.append([micro_strain, ms_s_err])

    now = datetime.datetime.now()
    file_use = file_use.split(".")[0] + "_shells.log"
    log_file = open(file_use, "w")
    log_file.write("=====================================================\n")
    log_file.write("Log file for nanoparticle shell microstrain analysis.\n")
    log_file.write("=====================================================\n")
    log_file.write("Time stamp: " + str(now)[:19] + "\n")
    log_file.write("=====================================================\n")
    log_file.write("Analysis sphere center location (fractional): \n")
    log_file.write("{0:16.13F},{1:16.13F},{2:16.13F}\n".format((nano_particle.centPosInt[0] + 1.0) / 2.0,
                                                               (nano_particle.centPosInt[1] + 1.0) / 2.0,
                                                               (nano_particle.centPosInt[2] + 1.0) / 2.0))
    log_file.write("=====================================================\n")
    log_file.write("Analysis sphere radius: {0:15.6F} angstrom.\n".format(nano_particle.NPRadius))
    log_file.write("=====================================================\n")
    log_file.write("{0:>10s}{1:>12s}{2:>10s}{3:>10s}\n".format("Shell", "# of cells", "MS", "Err"))
    log_file.write("=====================================================\n")
    if test_bulk.upper() == "Y":
        for i in range(len(cell_shell) - 1):
            log_file.write("{0:10d}{1:12d}{2:10.6f}{3:10.6f}\n".format(i + 1, len(cell_shell[i]),
                                                                       shell_ms[i][0], shell_ms[i][1]))
    else:
        for i in range(len(cell_shell)):
            log_file.write("{0:10d}{1:12d}{2:10.6f}{3:10.6f}\n".format(i + 1, len(cell_shell[i]),
                                                                       shell_ms[i][0], shell_ms[i][1]))
    log_file.write("=====================================================")

    log_file.close()

    stop = timeit.default_timer()

    print("\n--------------------------------------------")
    print("Particle successfully divided to " + str(shell_processed) + " shells.")
    print("Time taken:{0:11.3F} s".format(stop - start))
    print("--------------------------------------------")
    print("Log information can be found here:")
    print(file_use)
    print("--------------------------------------------")
