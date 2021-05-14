# -*- coding: utf-8 -*-
#
# tetras_env.py
#
# Python script for analyzing the connection and local environment
# of tetrahedrons in the RMC configuration obtained from fitting
# the LTNNbOF total scattering data.
#
# The capability includes:
#   - Statistics of different types of tetrahedrons, i. e. TM0,
#     TM1, TM2, TM3 and TM4.
#   - Mapping of tetrahedrons to a dummy atomic configuration
#     so that further correlation analysis between tetrahedrons
#     can be conducted.
#   - Distances between Li and the transition metals in each
#     different type of tetrahedron.
#   - Random walk approach for calculating the propagation
#     pathway for Li in the system, across the tetrahedrons.
#
# Yuanpeng Zhang @ Wed 15-Jul-20
# NIST & ORNL
#

import sys
from os import path
import datetime
from random import random
import math
import os
from rmc_tools import rmc6f_stuff
import numpy as np
import statistics


# Distance calculator.
def dist_calc(atomi, atomj, vectors, atomsCoord):
    # Index of list in Python starts from 0, whereas in RMC6F the starting
    # point is 1.
    atomi -= 1
    atomj -= 1
    vectors_temp = [[y / 2.0 for y in x] for x in vectors]
    metric = []
    for ii in range(3):
        metric.append([])
        for jj in range(3):
            metric[ii].append(0)
            for kk in range(3):
                metric[ii][jj] += (vectors_temp[ii][kk] * vectors_temp[jj][kk])
    m12 = metric[0][1] * 2.0
    m13 = metric[0][2] * 2.0
    m23 = metric[1][2] * 2.0
    xa = atomsCoord[atomi][0] + 3.0
    ya = atomsCoord[atomi][1] + 3.0
    za = atomsCoord[atomi][2] + 3.0
    x = xa - atomsCoord[atomj][0]
    y = ya - atomsCoord[atomj][1]
    z = za - atomsCoord[atomj][2]
    x = x - 2.0 * int(x * 0.5) - 1.0
    y = y - 2.0 * int(y * 0.5) - 1.0
    z = z - 2.0 * int(z * 0.5) - 1.0
    part1 = metric[0][0] * x * x + metric[1][1] * y * y + metric[2][2] * z * z
    part2 = m12 * x * y + m13 * x * z + m23 * y * z
    dist_result = np.sqrt(part1 + part2)

    return dist_result


def main(file_name):
    """
    tetra_env.py

    Usage:
        python tetra_env.py RMC6F_FILE_NAME
        - Typing 'python tetra_env.py -h' will print out current help.

    Update log:
        =============
        Fri 7-Aug-20
        =============
        Detailed statistics about local tetras analyzed - for each tetra type,
        count of tetras containing various types of TM's is also provided.

        Routine for analyzing TM types is changed, according to the indexes
        used in the old version of rmc6f file.
        =============
        Wed 15-Jul-20
        =============
        New functionality is added in to calculate the statistics of distances
        from Li to transition metals within the local tetrahedron environment.
        NO EXTRA INPUT is needed to enable this function. Corresponding out can
        be found in 'tetra_dists_LiTM_#.dat', where 'TM' represents a specific
        transition metal, e. g. Ni, and '#' is a sequential number starting
        from 1 corresponding to the number of times that current program has
        been run in current directory.

    Documentation:
        This script is created for analyzing the ratio of different types of
        tetrahedrons in the RMC configuration obtained from fitting the
        LTNNbOF total scattering data. Also, all the different types of
        tetrhedrons will be mapped to a dummy lattice so further analysis
        can be potentially carried out, e. g. analyzing the correlation between
        different types of tetrahedrons. Apart from that, the Li propagation
        pathway will also be analyzed. To do this, we use a random walk
        algorithm, for which we start from a random starting point and make
        random walk until we cannot walk anymore, based on the the energy
        barrier of different types of tetrahedrons. For the moment, we stay
        with the scheme that only TM0 (no transition metal surrounding the
        O-tetrahedron) allows Li to pass through.

        Given proper input, the analysis for ratio of different types of
        tetrahedron environment and the mapping of those tetrahedrons to
        dummy lattice will be conducted automatically.

        For the analysis of propagation path, i.e. the connectivity of those
        tetrahedrons, the program needs some input from user.
        The first pop-up question is the number of trials for selecting the
        starting point, i.e. which tetrahedron to start with for the random
        walk. Say, one inputs '50' for this, the program will try 50 different
        starting points randomly (there could possibly be duplicates,
        though).
        The second pop-up question is the number of random walking trials
        with each starting point. Say, one inputs 50 for this and assuming
        one input 50 in previous step, in total we will have 50*50=2500
        trials of random walking.
        The third pop-up question concerns the maximum walking steps to
        try out. Suppose we have a configuration where all tetrahedrons are
        TM0 and in this case if following our alogrithm, the random walker
        will keep walking and walking since it is supposed to go through
        all tetrahedrons along the way. We don't want that so we want to
        set a hard maximum limit of walking steps.

    Output:
        Output information will be printed out as the program runs. Specially,
        for the tetrahedron connectivity analysis, the resulted RMC6F file
        (which contains all the connected tetrahedrons) will be saved to the
        folder 'tetra_connect_#', where '#' represents a sequential number
        corresponding to the number of runs of this program in current
        directory. Trials with different starting point will be saved to
        corresponding subfolder in 'tetra_connect_#' and different trials
        with the same starting point will be saved into subfolders of their
        corresponding parent folder.
        All user inputs during the program runs will be written into the log
        file named 'tetra_inputs_#.log', where again '#' represents a
        sequential number corresponding to the number of runs of this program
        in current directory.

    ATTENTION:
        For the output tetrahedron connectivity files mentioned above, we
        should roughly get an idea about the size of each single file and
        pay attention to the total size of all potential output files!!!

    Author:
        Yuanpeng Zhang @ Wed 15-Jul-20
        National Institute of Standards and Technology
        Oak Ridge National Laboratory
    """

    input_config = rmc6f_stuff.RMC6FReader(file_name)

    # We need to use RMC6F internal coordinates for calculation of distances.
    atomsCoord = input_config.atomsCoordInt
    vectors = input_config.vectors

    tetra_map = {}
    tetra_map['coord'] = []
    tetra_map['type'] = []
    tetra_map['index'] = []
    tetra_map['unit_loc'] = []

    tm0_num = 0
    tm1_num = 0
    tm2_num = 0
    tm3_num = 0
    tm4_num = 0

    # Dictionaries for holding Li-TM distances in local tetrahedrons.
    tetra_dist_LiNi = {}
    tetra_dist_LiNb = {}
    tetra_dist_LiTi = {}
    tetra_dist_LiNi["TM1"] = []
    tetra_dist_LiNi["TM2"] = []
    tetra_dist_LiNi["TM3"] = []
    tetra_dist_LiNb["TM1"] = []
    tetra_dist_LiNb["TM2"] = []
    tetra_dist_LiNb["TM3"] = []
    tetra_dist_LiTi["TM1"] = []
    tetra_dist_LiTi["TM2"] = []
    tetra_dist_LiTi["TM3"] = []

    # Dicts for holding detailed statistics (type of TM's and its counts)
    # in local tetras.
    #
    # Here, we use the concatenation of TM name followed by the number of
    # times that it appears in a certain local tetra environment as our key
    # for the corresponding dictionary.
    #
    tm1_details = {"Ni1Nb0Ti0": 0, "Ni0Nb1Ti0": 0, "Ni0Nb0Ti1": 0}
    tm2_details = {}
    #
    # Cycle through all the possibilities. For example, for TM2 tetra, we
    # have 2 TM's, then we have 6 possibilities, as follows:
    # Ni0Nb0Ti2, Ni0Nb1Ti1, Ni0Nb2Ti0, Ni1Nb0Ti1, Ni1Nb1Ti0, Ni2Nb0Ti0.
    #
    for i in range(3):
        for j in range(3 - i):
            k = 2 - i - j
            key_temp = "Ni" + str(i) + "Nb" + str(j) + "Ti" + str(k)
            tm2_details[key_temp] = 0
    #
    tm3_details = {}
    for i in range(4):
        for j in range(4 - i):
            k = 3 - i - j
            key_temp = "Ni" + str(i) + "Nb" + str(j) + "Ti" + str(k)
            tm3_details[key_temp] = 0
    #
    tm4_details = {}
    for i in range(5):
        for j in range(5 - i):
            k = 4 - i - j
            key_temp = "Ni" + str(i) + "Nb" + str(j) + "Ti" + str(k)
            tm4_details[key_temp] = 0
    #
    for i in range(input_config.scDim[0]):
        for j in range(input_config.scDim[1]):
            for k in range(input_config.scDim[2]):

                unit_index_temp = i * input_config.scDim[1] * \
                    input_config.scDim[2] + \
                    j * input_config.scDim[2] + k

                # Process each of the 8 different tetrahedrons in a single
                # unit cell one by one.

                # 1st one.

                # Determine the type of the tetrahedron.
                li_num = sum([1 if item[0] == 'Li' else 0 for key, item in
                              input_config.unit_cell_info
                              [unit_index_temp].items()])
                if li_num == 4:
                    tm0_num += 1
                    tetra_map['type'].append('TM0')
                elif li_num == 3:
                    tm1_num += 1
                    tetra_map['type'].append('TM1')
                    dict_temp = input_config.unit_cell_info[unit_index_temp]
                    #
                    # Figure out number of each TM in this specific tetra and
                    # generate the corresponding key, with which we then
                    # determine where this tetra will be appended to (i. e.
                    # 1 will be added to the overall number of specific tetra
                    # type).
                    #
                    ni_num_temp = sum([1 if item[0] == "Ni" else 0
                                       for key, item in dict_temp.items()])
                    nb_num_temp = sum([1 if item[0] == "Nb" else 0
                                       for key, item in dict_temp.items()])
                    ti_num_temp = sum([1 if item[0] == "Ti" else 0
                                       for key, item in dict_temp.items()])
                    key_t1 = "Ni" + str(ni_num_temp)
                    key_t2 = "Nb" + str(nb_num_temp)
                    key_t3 = "Ti" + str(ti_num_temp)
                    key_t = key_t1 + key_t2 + key_t3
                    tm1_details[key_t] += 1

                    for key1, item1 in dict_temp.items():
                        if item1[0] == "Li":
                            for key2, item2 in dict_temp.items():
                                if item2[0] == "Ni":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNi["TM1"].append(dist_temp)
                                if item2[0] == "Nb":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNb["TM1"].append(dist_temp)
                                if item2[0] == "Ti":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiTi["TM1"].append(dist_temp)
                elif li_num == 2:
                    tm2_num += 1
                    tetra_map['type'].append('TM2')
                    dict_temp = input_config.unit_cell_info[unit_index_temp]

                    ni_num_temp = sum([1 if item[0] == "Ni" else 0
                                       for key, item in dict_temp.items()])
                    nb_num_temp = sum([1 if item[0] == "Nb" else 0
                                       for key, item in dict_temp.items()])
                    ti_num_temp = sum([1 if item[0] == "Ti" else 0
                                       for key, item in dict_temp.items()])
                    key_t1 = "Ni" + str(ni_num_temp)
                    key_t2 = "Nb" + str(nb_num_temp)
                    key_t3 = "Ti" + str(ti_num_temp)
                    key_t = key_t1 + key_t2 + key_t3
                    tm2_details[key_t] += 1

                    for key1, item1 in dict_temp.items():
                        if item1[0] == "Li":
                            for key2, item2 in dict_temp.items():
                                if item2[0] == "Ni":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNi["TM2"].append(dist_temp)
                                if item2[0] == "Nb":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNb["TM2"].append(dist_temp)
                                if item2[0] == "Ti":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiTi["TM2"].append(dist_temp)
                elif li_num == 1:
                    tm3_num += 1
                    tetra_map['type'].append('TM3')
                    dict_temp = input_config.unit_cell_info[unit_index_temp]

                    ni_num_temp = sum([1 if item[0] == "Ni" else 0
                                       for key, item in dict_temp.items()])
                    nb_num_temp = sum([1 if item[0] == "Nb" else 0
                                       for key, item in dict_temp.items()])
                    ti_num_temp = sum([1 if item[0] == "Ti" else 0
                                       for key, item in dict_temp.items()])
                    key_t1 = "Ni" + str(ni_num_temp)
                    key_t2 = "Nb" + str(nb_num_temp)
                    key_t3 = "Ti" + str(ti_num_temp)
                    key_t = key_t1 + key_t2 + key_t3
                    tm3_details[key_t] += 1

                    for key1, item1 in dict_temp.items():
                        if item1[0] == "Li":
                            for key2, item2 in dict_temp.items():
                                if item2[0] == "Ni":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNi["TM3"].append(dist_temp)
                                if item2[0] == "Nb":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNb["TM3"].append(dist_temp)
                                if item2[0] == "Ti":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiTi["TM3"].append(dist_temp)
                else:
                    tm4_num += 1
                    tetra_map['type'].append('TM4')
                    dict_temp = input_config.unit_cell_info[unit_index_temp]

                    ni_num_temp = sum([1 if item[0] == "Ni" else 0
                                       for key, item in dict_temp.items()])
                    nb_num_temp = sum([1 if item[0] == "Nb" else 0
                                       for key, item in dict_temp.items()])
                    ti_num_temp = sum([1 if item[0] == "Ti" else 0
                                       for key, item in dict_temp.items()])
                    key_t1 = "Ni" + str(ni_num_temp)
                    key_t2 = "Nb" + str(nb_num_temp)
                    key_t3 = "Ti" + str(ti_num_temp)
                    key_t = key_t1 + key_t2 + key_t3
                    tm4_details[key_t] += 1

                # Calculate the mapping coordinates.
                map_x = 2 * i + 0.5
                map_y = 2 * j + 0.5
                map_z = 2 * k + 0.5
                tetra_map['coord'].append([map_x, map_y, map_z])

                # Specify the index of the mapped point.
                tetra_map['index'].append(1)

                # Specify the location of the unit cell. This is the
                # same as that in the original atomic configuration.
                tetra_map['unit_loc'].append([i, j, k])

                # 2nd one.

                # Determine the type of the tetrahedron.
                if i < (input_config.scDim[0] - 1):
                    unit_index_temp_1 = (i + 1) * input_config.scDim[1] * \
                        input_config.scDim[2] + \
                        j * input_config.scDim[2] + k
                else:
                    unit_index_temp_1 = 0 * \
                        input_config.scDim[2] + \
                        j * input_config.scDim[2] + k
                unit_index_temp_3 = unit_index_temp_1

                li_num = 0
                if input_config.unit_cell_info[unit_index_temp][7][0] == 'Li':
                    li_num += 1
                if input_config.unit_cell_info[unit_index_temp][5][0] == 'Li':
                    li_num += 1
                dict_temp = input_config.unit_cell_info[unit_index_temp_1]
                if dict_temp[1][0] == 'Li':
                    li_num += 1
                dict_temp = input_config.unit_cell_info[unit_index_temp_3]
                if dict_temp[3][0] == 'Li':  # Update: dict[7][0] -> dict[3][0]
                    li_num += 1

                dict_temp = {}
                dict_temp[7] = input_config.unit_cell_info[unit_index_temp][7]
                dict_temp[5] = input_config.unit_cell_info[unit_index_temp][5]
                temp_temp = input_config.unit_cell_info[unit_index_temp_1]
                dict_temp[1] = temp_temp[1]
                temp_temp = input_config.unit_cell_info[unit_index_temp_3]
                dict_temp[3] = temp_temp[3]

                if li_num == 4:
                    tm0_num += 1
                    tetra_map['type'].append('TM0')
                elif li_num == 3:
                    tm1_num += 1
                    tetra_map['type'].append('TM1')

                    ni_num_temp = sum([1 if item[0] == "Ni" else 0
                                       for key, item in dict_temp.items()])
                    nb_num_temp = sum([1 if item[0] == "Nb" else 0
                                       for key, item in dict_temp.items()])
                    ti_num_temp = sum([1 if item[0] == "Ti" else 0
                                       for key, item in dict_temp.items()])
                    key_t1 = "Ni" + str(ni_num_temp)
                    key_t2 = "Nb" + str(nb_num_temp)
                    key_t3 = "Ti" + str(ti_num_temp)
                    key_t = key_t1 + key_t2 + key_t3
                    tm1_details[key_t] += 1

                    for key1, item1 in dict_temp.items():
                        if item1[0] == "Li":
                            for key2, item2 in dict_temp.items():
                                if item2[0] == "Ni":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNi["TM1"].append(dist_temp)
                                if item2[0] == "Nb":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNb["TM1"].append(dist_temp)
                                if item2[0] == "Ti":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiTi["TM1"].append(dist_temp)
                elif li_num == 2:
                    tm2_num += 1
                    tetra_map['type'].append('TM2')

                    ni_num_temp = sum([1 if item[0] == "Ni" else 0
                                       for key, item in dict_temp.items()])
                    nb_num_temp = sum([1 if item[0] == "Nb" else 0
                                       for key, item in dict_temp.items()])
                    ti_num_temp = sum([1 if item[0] == "Ti" else 0
                                       for key, item in dict_temp.items()])
                    key_t1 = "Ni" + str(ni_num_temp)
                    key_t2 = "Nb" + str(nb_num_temp)
                    key_t3 = "Ti" + str(ti_num_temp)
                    key_t = key_t1 + key_t2 + key_t3
                    tm2_details[key_t] += 1

                    for key1, item1 in dict_temp.items():
                        if item1[0] == "Li":
                            for key2, item2 in dict_temp.items():
                                if item2[0] == "Ni":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNi["TM2"].append(dist_temp)
                                if item2[0] == "Nb":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNb["TM2"].append(dist_temp)
                                if item2[0] == "Ti":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiTi["TM2"].append(dist_temp)
                elif li_num == 1:
                    tm3_num += 1
                    tetra_map['type'].append('TM3')

                    ni_num_temp = sum([1 if item[0] == "Ni" else 0
                                       for key, item in dict_temp.items()])
                    nb_num_temp = sum([1 if item[0] == "Nb" else 0
                                       for key, item in dict_temp.items()])
                    ti_num_temp = sum([1 if item[0] == "Ti" else 0
                                       for key, item in dict_temp.items()])
                    key_t1 = "Ni" + str(ni_num_temp)
                    key_t2 = "Nb" + str(nb_num_temp)
                    key_t3 = "Ti" + str(ti_num_temp)
                    key_t = key_t1 + key_t2 + key_t3
                    tm3_details[key_t] += 1

                    for key1, item1 in dict_temp.items():
                        if item1[0] == "Li":
                            for key2, item2 in dict_temp.items():
                                if item2[0] == "Ni":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNi["TM3"].append(dist_temp)
                                if item2[0] == "Nb":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNb["TM3"].append(dist_temp)
                                if item2[0] == "Ti":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiTi["TM3"].append(dist_temp)
                else:
                    tm4_num += 1
                    tetra_map['type'].append('TM4')

                    ni_num_temp = sum([1 if item[0] == "Ni" else 0
                                       for key, item in dict_temp.items()])
                    nb_num_temp = sum([1 if item[0] == "Nb" else 0
                                       for key, item in dict_temp.items()])
                    ti_num_temp = sum([1 if item[0] == "Ti" else 0
                                       for key, item in dict_temp.items()])
                    key_t1 = "Ni" + str(ni_num_temp)
                    key_t2 = "Nb" + str(nb_num_temp)
                    key_t3 = "Ti" + str(ti_num_temp)
                    key_t = key_t1 + key_t2 + key_t3
                    tm4_details[key_t] += 1

                # Calculate the mapping coordinates.
                map_x = 2 * i + 1.5
                map_y = 2 * j + 0.5
                map_z = 2 * k + 0.5
                tetra_map['coord'].append([map_x, map_y, map_z])

                # Specify the index of the mapped point.
                tetra_map['index'].append(2)

                # Specify the location of the unit cell. This is the
                # same as that in the original atomic configuration.
                tetra_map['unit_loc'].append([i, j, k])

                # 3rd one.

                # Determine the type of the tetrahedron.
                if j < (input_config.scDim[1] - 1):
                    unit_index_temp_1 = i * input_config.scDim[1] * \
                        input_config.scDim[2] + \
                        (j + 1) * input_config.scDim[2] + k
                else:
                    unit_index_temp_1 = i * input_config.scDim[1] * \
                        input_config.scDim[2] + \
                        0 * input_config.scDim[2] + k
                unit_index_temp_5 = unit_index_temp_1

                li_num = 0
                if input_config.unit_cell_info[unit_index_temp][3][0] == 'Li':
                    li_num += 1
                if input_config.unit_cell_info[unit_index_temp][7][0] == 'Li':
                    li_num += 1
                temp_temp = input_config.unit_cell_info[unit_index_temp_1][1]
                if temp_temp[0] == 'Li':
                    li_num += 1
                temp_temp = input_config.unit_cell_info[unit_index_temp_5][5]
                if temp_temp[0] == 'Li':
                    li_num += 1

                dict_temp = {}
                dict_temp[3] = input_config.unit_cell_info[unit_index_temp][3]
                dict_temp[7] = input_config.unit_cell_info[unit_index_temp][7]
                temp_temp = input_config.unit_cell_info[unit_index_temp_1]
                dict_temp[1] = temp_temp[1]
                temp_temp = input_config.unit_cell_info[unit_index_temp_5]
                dict_temp[5] = temp_temp[5]

                if li_num == 4:
                    tm0_num += 1
                    tetra_map['type'].append('TM0')
                elif li_num == 3:
                    tm1_num += 1
                    tetra_map['type'].append('TM1')

                    ni_num_temp = sum([1 if item[0] == "Ni" else 0
                                       for key, item in dict_temp.items()])
                    nb_num_temp = sum([1 if item[0] == "Nb" else 0
                                       for key, item in dict_temp.items()])
                    ti_num_temp = sum([1 if item[0] == "Ti" else 0
                                       for key, item in dict_temp.items()])
                    key_t1 = "Ni" + str(ni_num_temp)
                    key_t2 = "Nb" + str(nb_num_temp)
                    key_t3 = "Ti" + str(ti_num_temp)
                    key_t = key_t1 + key_t2 + key_t3
                    tm1_details[key_t] += 1

                    for key1, item1 in dict_temp.items():
                        if item1[0] == "Li":
                            for key2, item2 in dict_temp.items():
                                if item2[0] == "Ni":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNi["TM1"].append(dist_temp)
                                if item2[0] == "Nb":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNb["TM1"].append(dist_temp)
                                if item2[0] == "Ti":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiTi["TM1"].append(dist_temp)
                elif li_num == 2:
                    tm2_num += 1
                    tetra_map['type'].append('TM2')

                    ni_num_temp = sum([1 if item[0] == "Ni" else 0
                                       for key, item in dict_temp.items()])
                    nb_num_temp = sum([1 if item[0] == "Nb" else 0
                                       for key, item in dict_temp.items()])
                    ti_num_temp = sum([1 if item[0] == "Ti" else 0
                                       for key, item in dict_temp.items()])
                    key_t1 = "Ni" + str(ni_num_temp)
                    key_t2 = "Nb" + str(nb_num_temp)
                    key_t3 = "Ti" + str(ti_num_temp)
                    key_t = key_t1 + key_t2 + key_t3
                    tm2_details[key_t] += 1

                    for key1, item1 in dict_temp.items():
                        if item1[0] == "Li":
                            for key2, item2 in dict_temp.items():
                                if item2[0] == "Ni":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNi["TM2"].append(dist_temp)
                                if item2[0] == "Nb":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNb["TM2"].append(dist_temp)
                                if item2[0] == "Ti":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiTi["TM2"].append(dist_temp)
                elif li_num == 1:
                    tm3_num += 1
                    tetra_map['type'].append('TM3')

                    ni_num_temp = sum([1 if item[0] == "Ni" else 0
                                       for key, item in dict_temp.items()])
                    nb_num_temp = sum([1 if item[0] == "Nb" else 0
                                       for key, item in dict_temp.items()])
                    ti_num_temp = sum([1 if item[0] == "Ti" else 0
                                       for key, item in dict_temp.items()])
                    key_t1 = "Ni" + str(ni_num_temp)
                    key_t2 = "Nb" + str(nb_num_temp)
                    key_t3 = "Ti" + str(ti_num_temp)
                    key_t = key_t1 + key_t2 + key_t3
                    tm3_details[key_t] += 1

                    for key1, item1 in dict_temp.items():
                        if item1[0] == "Li":
                            for key2, item2 in dict_temp.items():
                                if item2[0] == "Ni":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNi["TM3"].append(dist_temp)
                                if item2[0] == "Nb":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNb["TM3"].append(dist_temp)
                                if item2[0] == "Ti":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiTi["TM3"].append(dist_temp)
                else:
                    tm4_num += 1
                    tetra_map['type'].append('TM4')

                    ni_num_temp = sum([1 if item[0] == "Ni" else 0
                                       for key, item in dict_temp.items()])
                    nb_num_temp = sum([1 if item[0] == "Nb" else 0
                                       for key, item in dict_temp.items()])
                    ti_num_temp = sum([1 if item[0] == "Ti" else 0
                                       for key, item in dict_temp.items()])
                    key_t1 = "Ni" + str(ni_num_temp)
                    key_t2 = "Nb" + str(nb_num_temp)
                    key_t3 = "Ti" + str(ti_num_temp)
                    key_t = key_t1 + key_t2 + key_t3
                    tm4_details[key_t] += 1

                # Calculate the mapping coordinates.
                map_x = 2 * i + 0.5
                map_y = 2 * j + 1.5
                map_z = 2 * k + 0.5
                tetra_map['coord'].append([map_x, map_y, map_z])

                # Specify the index of the mapped point.
                tetra_map['index'].append(3)

                # Specify the location of the unit cell. This is the
                # same as that in the original atomic configuration.
                tetra_map['unit_loc'].append([i, j, k])

                # 4th one.

                # Determine the type of the tetrahedron.
                if k < (input_config.scDim[2] - 1):
                    unit_index_temp_1 = i * input_config.scDim[1] * \
                        input_config.scDim[2] + \
                        j * input_config.scDim[2] + (k + 1)
                else:
                    unit_index_temp_1 = i * input_config.scDim[1] * \
                        input_config.scDim[2] + \
                        j * input_config.scDim[2] + 0
                unit_index_temp_7 = unit_index_temp_1

                li_num = 0
                if input_config.unit_cell_info[unit_index_temp][5][0] == 'Li':
                    li_num += 1
                if input_config.unit_cell_info[unit_index_temp][3][0] == 'Li':
                    li_num += 1
                temp_temp = input_config.unit_cell_info[unit_index_temp_1][1]
                if temp_temp[0] == 'Li':
                    li_num += 1
                temp_temp = input_config.unit_cell_info[unit_index_temp_7][7]
                if temp_temp[0] == 'Li':
                    li_num += 1

                dict_temp = {}
                dict_temp[5] = input_config.unit_cell_info[unit_index_temp][5]
                dict_temp[3] = input_config.unit_cell_info[unit_index_temp][3]
                temp_temp = input_config.unit_cell_info[unit_index_temp_1]
                dict_temp[1] = temp_temp[1]
                temp_temp = input_config.unit_cell_info[unit_index_temp_7]
                dict_temp[7] = temp_temp[7]

                if li_num == 4:
                    tm0_num += 1
                    tetra_map['type'].append('TM0')
                elif li_num == 3:
                    tm1_num += 1
                    tetra_map['type'].append('TM1')

                    ni_num_temp = sum([1 if item[0] == "Ni" else 0
                                       for key, item in dict_temp.items()])
                    nb_num_temp = sum([1 if item[0] == "Nb" else 0
                                       for key, item in dict_temp.items()])
                    ti_num_temp = sum([1 if item[0] == "Ti" else 0
                                       for key, item in dict_temp.items()])
                    key_t1 = "Ni" + str(ni_num_temp)
                    key_t2 = "Nb" + str(nb_num_temp)
                    key_t3 = "Ti" + str(ti_num_temp)
                    key_t = key_t1 + key_t2 + key_t3
                    tm1_details[key_t] += 1

                    for key1, item1 in dict_temp.items():
                        if item1[0] == "Li":
                            for key2, item2 in dict_temp.items():
                                if item2[0] == "Ni":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNi["TM1"].append(dist_temp)
                                if item2[0] == "Nb":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNb["TM1"].append(dist_temp)
                                if item2[0] == "Ti":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiTi["TM1"].append(dist_temp)
                elif li_num == 2:
                    tm2_num += 1
                    tetra_map['type'].append('TM2')

                    ni_num_temp = sum([1 if item[0] == "Ni" else 0
                                       for key, item in dict_temp.items()])
                    nb_num_temp = sum([1 if item[0] == "Nb" else 0
                                       for key, item in dict_temp.items()])
                    ti_num_temp = sum([1 if item[0] == "Ti" else 0
                                       for key, item in dict_temp.items()])
                    key_t1 = "Ni" + str(ni_num_temp)
                    key_t2 = "Nb" + str(nb_num_temp)
                    key_t3 = "Ti" + str(ti_num_temp)
                    key_t = key_t1 + key_t2 + key_t3
                    tm2_details[key_t] += 1

                    for key1, item1 in dict_temp.items():
                        if item1[0] == "Li":
                            for key2, item2 in dict_temp.items():
                                if item2[0] == "Ni":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNi["TM2"].append(dist_temp)
                                if item2[0] == "Nb":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNb["TM2"].append(dist_temp)
                                if item2[0] == "Ti":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiTi["TM2"].append(dist_temp)
                elif li_num == 1:
                    tm3_num += 1
                    tetra_map['type'].append('TM3')

                    ni_num_temp = sum([1 if item[0] == "Ni" else 0
                                       for key, item in dict_temp.items()])
                    nb_num_temp = sum([1 if item[0] == "Nb" else 0
                                       for key, item in dict_temp.items()])
                    ti_num_temp = sum([1 if item[0] == "Ti" else 0
                                       for key, item in dict_temp.items()])
                    key_t1 = "Ni" + str(ni_num_temp)
                    key_t2 = "Nb" + str(nb_num_temp)
                    key_t3 = "Ti" + str(ti_num_temp)
                    key_t = key_t1 + key_t2 + key_t3
                    tm3_details[key_t] += 1

                    for key1, item1 in dict_temp.items():
                        if item1[0] == "Li":
                            for key2, item2 in dict_temp.items():
                                if item2[0] == "Ni":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNi["TM3"].append(dist_temp)
                                if item2[0] == "Nb":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNb["TM3"].append(dist_temp)
                                if item2[0] == "Ti":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiTi["TM3"].append(dist_temp)
                else:
                    tm4_num += 1
                    tetra_map['type'].append('TM4')

                    ni_num_temp = sum([1 if item[0] == "Ni" else 0
                                       for key, item in dict_temp.items()])
                    nb_num_temp = sum([1 if item[0] == "Nb" else 0
                                       for key, item in dict_temp.items()])
                    ti_num_temp = sum([1 if item[0] == "Ti" else 0
                                       for key, item in dict_temp.items()])
                    key_t1 = "Ni" + str(ni_num_temp)
                    key_t2 = "Nb" + str(nb_num_temp)
                    key_t3 = "Ti" + str(ti_num_temp)
                    key_t = key_t1 + key_t2 + key_t3
                    tm4_details[key_t] += 1

                # Calculate the mapping coordinates.
                map_x = 2 * i + 0.5
                map_y = 2 * j + 0.5
                map_z = 2 * k + 1.5
                tetra_map['coord'].append([map_x, map_y, map_z])

                # Specify the index of the mapped point.
                tetra_map['index'].append(4)

                # Specify the location of the unit cell. This is the
                # same as that in the original atomic configuration.
                tetra_map['unit_loc'].append([i, j, k])

                # 5th one.

                # Determine the type of the tetrahedron.
                if (i < (input_config.scDim[0] - 1)) and \
                        (k < (input_config.scDim[2] - 1)):
                    unit_index_temp_1 = (i + 1) * input_config.scDim[1] * \
                        input_config.scDim[2] + \
                        j * input_config.scDim[2] + (k + 1)
                elif (i == (input_config.scDim[0] - 1)) \
                        and (k < (input_config.scDim[2] - 1)):
                    unit_index_temp_1 = 0 * input_config.scDim[1] * \
                        input_config.scDim[2] + \
                        j * input_config.scDim[2] + (k + 1)
                elif (i < (input_config.scDim[0] - 1)) \
                        and (k == (input_config.scDim[2] - 1)):
                    unit_index_temp_1 = (i + 1) * input_config.scDim[1] * \
                        input_config.scDim[2] + \
                        j * input_config.scDim[2] + 0
                else:
                    unit_index_temp_1 = 0 * input_config.scDim[1] * \
                        input_config.scDim[2] + \
                        j * input_config.scDim[2] + 0
                if k < (input_config.scDim[2] - 1):
                    unit_index_temp_7 = i * input_config.scDim[1] * \
                        input_config.scDim[2] + \
                        j * input_config.scDim[2] + (k + 1)
                else:
                    unit_index_temp_7 = i * input_config.scDim[1] * \
                        input_config.scDim[2] + \
                        j * input_config.scDim[2] + 0
                if i < (input_config.scDim[0] - 1):
                    unit_index_temp_3 = (i + 1) * input_config.scDim[1] * \
                        input_config.scDim[2] + \
                        j * input_config.scDim[2] + k
                else:
                    unit_index_temp_3 = 0 * input_config.scDim[1] * \
                        input_config.scDim[2] + \
                        j * input_config.scDim[2] + k

                li_num = 0
                if input_config.unit_cell_info[unit_index_temp][5][0] == 'Li':
                    li_num += 1
                temp_temp = input_config.unit_cell_info[unit_index_temp_7][7]
                if temp_temp[0] == 'Li':
                    li_num += 1
                temp_temp = input_config.unit_cell_info[unit_index_temp_1][1]
                if temp_temp[0] == 'Li':
                    li_num += 1
                temp_temp = input_config.unit_cell_info[unit_index_temp_3][3]
                if temp_temp[0] == 'Li':
                    li_num += 1

                dict_temp = {}
                dict_temp[5] = input_config.unit_cell_info[unit_index_temp][5]
                temp_temp = input_config.unit_cell_info[unit_index_temp_7]
                dict_temp[7] = temp_temp[7]
                temp_temp = input_config.unit_cell_info[unit_index_temp_1]
                dict_temp[1] = temp_temp[1]
                temp_temp = input_config.unit_cell_info[unit_index_temp_3]
                dict_temp[3] = temp_temp[3]

                if li_num == 4:
                    tm0_num += 1
                    tetra_map['type'].append('TM0')
                elif li_num == 3:
                    tm1_num += 1
                    tetra_map['type'].append('TM1')

                    ni_num_temp = sum([1 if item[0] == "Ni" else 0
                                       for key, item in dict_temp.items()])
                    nb_num_temp = sum([1 if item[0] == "Nb" else 0
                                       for key, item in dict_temp.items()])
                    ti_num_temp = sum([1 if item[0] == "Ti" else 0
                                       for key, item in dict_temp.items()])
                    key_t1 = "Ni" + str(ni_num_temp)
                    key_t2 = "Nb" + str(nb_num_temp)
                    key_t3 = "Ti" + str(ti_num_temp)
                    key_t = key_t1 + key_t2 + key_t3
                    tm1_details[key_t] += 1

                    for key1, item1 in dict_temp.items():
                        if item1[0] == "Li":
                            for key2, item2 in dict_temp.items():
                                if item2[0] == "Ni":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNi["TM1"].append(dist_temp)
                                if item2[0] == "Nb":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNb["TM1"].append(dist_temp)
                                if item2[0] == "Ti":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiTi["TM1"].append(dist_temp)
                elif li_num == 2:
                    tm2_num += 1
                    tetra_map['type'].append('TM2')

                    ni_num_temp = sum([1 if item[0] == "Ni" else 0
                                       for key, item in dict_temp.items()])
                    nb_num_temp = sum([1 if item[0] == "Nb" else 0
                                       for key, item in dict_temp.items()])
                    ti_num_temp = sum([1 if item[0] == "Ti" else 0
                                       for key, item in dict_temp.items()])
                    key_t1 = "Ni" + str(ni_num_temp)
                    key_t2 = "Nb" + str(nb_num_temp)
                    key_t3 = "Ti" + str(ti_num_temp)
                    key_t = key_t1 + key_t2 + key_t3
                    tm2_details[key_t] += 1

                    for key1, item1 in dict_temp.items():
                        if item1[0] == "Li":
                            for key2, item2 in dict_temp.items():
                                if item2[0] == "Ni":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNi["TM2"].append(dist_temp)
                                if item2[0] == "Nb":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNb["TM2"].append(dist_temp)
                                if item2[0] == "Ti":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiTi["TM2"].append(dist_temp)
                elif li_num == 1:
                    tm3_num += 1
                    tetra_map['type'].append('TM3')

                    ni_num_temp = sum([1 if item[0] == "Ni" else 0
                                       for key, item in dict_temp.items()])
                    nb_num_temp = sum([1 if item[0] == "Nb" else 0
                                       for key, item in dict_temp.items()])
                    ti_num_temp = sum([1 if item[0] == "Ti" else 0
                                       for key, item in dict_temp.items()])
                    key_t1 = "Ni" + str(ni_num_temp)
                    key_t2 = "Nb" + str(nb_num_temp)
                    key_t3 = "Ti" + str(ti_num_temp)
                    key_t = key_t1 + key_t2 + key_t3
                    tm3_details[key_t] += 1

                    for key1, item1 in dict_temp.items():
                        if item1[0] == "Li":
                            for key2, item2 in dict_temp.items():
                                if item2[0] == "Ni":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNi["TM3"].append(dist_temp)
                                if item2[0] == "Nb":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNb["TM3"].append(dist_temp)
                                if item2[0] == "Ti":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiTi["TM3"].append(dist_temp)
                else:
                    tm4_num += 1
                    tetra_map['type'].append('TM4')

                    ni_num_temp = sum([1 if item[0] == "Ni" else 0
                                       for key, item in dict_temp.items()])
                    nb_num_temp = sum([1 if item[0] == "Nb" else 0
                                       for key, item in dict_temp.items()])
                    ti_num_temp = sum([1 if item[0] == "Ti" else 0
                                       for key, item in dict_temp.items()])
                    key_t1 = "Ni" + str(ni_num_temp)
                    key_t2 = "Nb" + str(nb_num_temp)
                    key_t3 = "Ti" + str(ti_num_temp)
                    key_t = key_t1 + key_t2 + key_t3
                    tm4_details[key_t] += 1

                # Calculate the mapping coordinates.
                map_x = 2 * i + 1.5
                map_y = 2 * j + 0.5
                map_z = 2 * k + 1.5
                tetra_map['coord'].append([map_x, map_y, map_z])

                # Specify the index of the mapped point.
                tetra_map['index'].append(5)

                # Specify the location of the unit cell. This is the
                # same as that in the original atomic configuration.
                tetra_map['unit_loc'].append([i, j, k])

                # 6th one.

                # Determine the type of the tetrahedron.
                if (i < (input_config.scDim[0] - 1)) and \
                        (j < (input_config.scDim[1] - 1)):
                    unit_index_temp_1 = (i + 1) * input_config.scDim[1] * \
                        input_config.scDim[2] + \
                        (j + 1) * input_config.scDim[2] + k
                elif (i == (input_config.scDim[0] - 1)) and \
                        (j < (input_config.scDim[1] - 1)):
                    unit_index_temp_1 = 0 * input_config.scDim[1] * \
                        input_config.scDim[2] + \
                        (j + 1) * input_config.scDim[2] + k
                elif (i < (input_config.scDim[0] - 1)) and \
                        (j == (input_config.scDim[1] - 1)):
                    unit_index_temp_1 = (i + 1) * input_config.scDim[1] * \
                        input_config.scDim[2] + \
                        0 * input_config.scDim[2] + k
                else:
                    unit_index_temp_1 = 0 * input_config.scDim[1] * \
                        input_config.scDim[2] + \
                        0 * input_config.scDim[2] + k
                if j < (input_config.scDim[1] - 1):
                    unit_index_temp_5 = i * input_config.scDim[1] * \
                        input_config.scDim[2] + \
                        (j + 1) * input_config.scDim[2] + k
                else:
                    unit_index_temp_5 = i * input_config.scDim[1] * \
                        input_config.scDim[2] + \
                        0 * input_config.scDim[2] + k
                if i < (input_config.scDim[0] - 1):
                    unit_index_temp_3 = (i + 1) * input_config.scDim[1] * \
                        input_config.scDim[2] + \
                        j * input_config.scDim[2] + k
                else:
                    unit_index_temp_3 = 0 * input_config.scDim[1] * \
                        input_config.scDim[2] + \
                        j * input_config.scDim[2] + k

                li_num = 0
                if input_config.unit_cell_info[unit_index_temp][7][0] == 'Li':
                    li_num += 1
                temp_temp = input_config.unit_cell_info[unit_index_temp_3][3]
                if temp_temp[0] == 'Li':
                    li_num += 1
                temp_temp = input_config.unit_cell_info[unit_index_temp_1][1]
                if temp_temp[0] == 'Li':
                    li_num += 1
                temp_temp = input_config.unit_cell_info[unit_index_temp_5][5]
                if temp_temp[0] == 'Li':
                    li_num += 1

                dict_temp = {}
                dict_temp[7] = input_config.unit_cell_info[unit_index_temp][7]
                temp_temp = input_config.unit_cell_info[unit_index_temp_3]
                dict_temp[3] = temp_temp[3]
                temp_temp = input_config.unit_cell_info[unit_index_temp_1]
                dict_temp[1] = temp_temp[1]
                temp_temp = input_config.unit_cell_info[unit_index_temp_5]
                dict_temp[5] = temp_temp[5]

                if li_num == 4:
                    tm0_num += 1
                    tetra_map['type'].append('TM0')
                elif li_num == 3:
                    tm1_num += 1
                    tetra_map['type'].append('TM1')

                    ni_num_temp = sum([1 if item[0] == "Ni" else 0
                                       for key, item in dict_temp.items()])
                    nb_num_temp = sum([1 if item[0] == "Nb" else 0
                                       for key, item in dict_temp.items()])
                    ti_num_temp = sum([1 if item[0] == "Ti" else 0
                                       for key, item in dict_temp.items()])
                    key_t1 = "Ni" + str(ni_num_temp)
                    key_t2 = "Nb" + str(nb_num_temp)
                    key_t3 = "Ti" + str(ti_num_temp)
                    key_t = key_t1 + key_t2 + key_t3
                    tm1_details[key_t] += 1

                    for key1, item1 in dict_temp.items():
                        if item1[0] == "Li":
                            for key2, item2 in dict_temp.items():
                                if item2[0] == "Ni":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNi["TM1"].append(dist_temp)
                                if item2[0] == "Nb":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNb["TM1"].append(dist_temp)
                                if item2[0] == "Ti":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiTi["TM1"].append(dist_temp)
                elif li_num == 2:
                    tm2_num += 1
                    tetra_map['type'].append('TM2')

                    ni_num_temp = sum([1 if item[0] == "Ni" else 0
                                       for key, item in dict_temp.items()])
                    nb_num_temp = sum([1 if item[0] == "Nb" else 0
                                       for key, item in dict_temp.items()])
                    ti_num_temp = sum([1 if item[0] == "Ti" else 0
                                       for key, item in dict_temp.items()])
                    key_t1 = "Ni" + str(ni_num_temp)
                    key_t2 = "Nb" + str(nb_num_temp)
                    key_t3 = "Ti" + str(ti_num_temp)
                    key_t = key_t1 + key_t2 + key_t3
                    tm2_details[key_t] += 1

                    for key1, item1 in dict_temp.items():
                        if item1[0] == "Li":
                            for key2, item2 in dict_temp.items():
                                if item2[0] == "Ni":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNi["TM2"].append(dist_temp)
                                if item2[0] == "Nb":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNb["TM2"].append(dist_temp)
                                if item2[0] == "Ti":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiTi["TM2"].append(dist_temp)
                elif li_num == 1:
                    tm3_num += 1
                    tetra_map['type'].append('TM3')

                    ni_num_temp = sum([1 if item[0] == "Ni" else 0
                                       for key, item in dict_temp.items()])
                    nb_num_temp = sum([1 if item[0] == "Nb" else 0
                                       for key, item in dict_temp.items()])
                    ti_num_temp = sum([1 if item[0] == "Ti" else 0
                                       for key, item in dict_temp.items()])
                    key_t1 = "Ni" + str(ni_num_temp)
                    key_t2 = "Nb" + str(nb_num_temp)
                    key_t3 = "Ti" + str(ti_num_temp)
                    key_t = key_t1 + key_t2 + key_t3
                    tm3_details[key_t] += 1

                    for key1, item1 in dict_temp.items():
                        if item1[0] == "Li":
                            for key2, item2 in dict_temp.items():
                                if item2[0] == "Ni":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNi["TM3"].append(dist_temp)
                                if item2[0] == "Nb":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNb["TM3"].append(dist_temp)
                                if item2[0] == "Ti":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiTi["TM3"].append(dist_temp)
                else:
                    tm4_num += 1
                    tetra_map['type'].append('TM4')

                    ni_num_temp = sum([1 if item[0] == "Ni" else 0
                                       for key, item in dict_temp.items()])
                    nb_num_temp = sum([1 if item[0] == "Nb" else 0
                                       for key, item in dict_temp.items()])
                    ti_num_temp = sum([1 if item[0] == "Ti" else 0
                                       for key, item in dict_temp.items()])
                    key_t1 = "Ni" + str(ni_num_temp)
                    key_t2 = "Nb" + str(nb_num_temp)
                    key_t3 = "Ti" + str(ti_num_temp)
                    key_t = key_t1 + key_t2 + key_t3
                    tm4_details[key_t] += 1

                # Calculate the mapping coordinates.
                map_x = 2 * i + 1.5
                map_y = 2 * j + 1.5
                map_z = 2 * k + 0.5
                tetra_map['coord'].append([map_x, map_y, map_z])

                # Specify the index of the mapped point.
                tetra_map['index'].append(6)

                # Specify the location of the unit cell. This is the
                # same as that in the original atomic configuration.
                tetra_map['unit_loc'].append([i, j, k])

                # 7th one.

                # Determine the type of the tetrahedron.
                i_t = -1 if i == (input_config.scDim[0] - 1) else i
                j_t = -1 if j == (input_config.scDim[1] - 1) else j
                k_t = -1 if k == (input_config.scDim[2] - 1) else k

                unit_index_temp_1 = i * input_config.scDim[1] * \
                    input_config.scDim[2] + \
                    (j_t + 1) * input_config.scDim[2] + (k_t + 1)
                unit_index_temp_7 = i * input_config.scDim[1] * \
                    input_config.scDim[2] + \
                    j * input_config.scDim[2] + (k_t + 1)
                unit_index_temp_5 = i * input_config.scDim[1] * \
                    input_config.scDim[2] + \
                    (j_t + 1) * input_config.scDim[2] + k

                li_num = 0
                if input_config.unit_cell_info[unit_index_temp][3][0] == 'Li':
                    li_num += 1
                temp_temp = input_config.unit_cell_info[unit_index_temp_5][5]
                if temp_temp[0] == 'Li':
                    li_num += 1
                temp_temp = input_config.unit_cell_info[unit_index_temp_1][1]
                if temp_temp[0] == 'Li':
                    li_num += 1
                temp_temp = input_config.unit_cell_info[unit_index_temp_7][7]
                if temp_temp[0] == 'Li':
                    li_num += 1

                dict_temp = {}
                dict_temp[3] = input_config.unit_cell_info[unit_index_temp][3]
                temp_temp = input_config.unit_cell_info[unit_index_temp_5]
                dict_temp[5] = temp_temp[5]
                temp_temp = input_config.unit_cell_info[unit_index_temp_1]
                dict_temp[1] = temp_temp[1]
                temp_temp = input_config.unit_cell_info[unit_index_temp_7]
                dict_temp[7] = temp_temp[7]

                if li_num == 4:
                    tm0_num += 1
                    tetra_map['type'].append('TM0')
                elif li_num == 3:
                    tm1_num += 1
                    tetra_map['type'].append('TM1')

                    ni_num_temp = sum([1 if item[0] == "Ni" else 0
                                       for key, item in dict_temp.items()])
                    nb_num_temp = sum([1 if item[0] == "Nb" else 0
                                       for key, item in dict_temp.items()])
                    ti_num_temp = sum([1 if item[0] == "Ti" else 0
                                       for key, item in dict_temp.items()])
                    key_t1 = "Ni" + str(ni_num_temp)
                    key_t2 = "Nb" + str(nb_num_temp)
                    key_t3 = "Ti" + str(ti_num_temp)
                    key_t = key_t1 + key_t2 + key_t3
                    tm1_details[key_t] += 1

                    for key1, item1 in dict_temp.items():
                        if item1[0] == "Li":
                            for key2, item2 in dict_temp.items():
                                if item2[0] == "Ni":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNi["TM1"].append(dist_temp)
                                if item2[0] == "Nb":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNb["TM1"].append(dist_temp)
                                if item2[0] == "Ti":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiTi["TM1"].append(dist_temp)
                elif li_num == 2:
                    tm2_num += 1
                    tetra_map['type'].append('TM2')

                    ni_num_temp = sum([1 if item[0] == "Ni" else 0
                                       for key, item in dict_temp.items()])
                    nb_num_temp = sum([1 if item[0] == "Nb" else 0
                                       for key, item in dict_temp.items()])
                    ti_num_temp = sum([1 if item[0] == "Ti" else 0
                                       for key, item in dict_temp.items()])
                    key_t1 = "Ni" + str(ni_num_temp)
                    key_t2 = "Nb" + str(nb_num_temp)
                    key_t3 = "Ti" + str(ti_num_temp)
                    key_t = key_t1 + key_t2 + key_t3
                    tm2_details[key_t] += 1

                    for key1, item1 in dict_temp.items():
                        if item1[0] == "Li":
                            for key2, item2 in dict_temp.items():
                                if item2[0] == "Ni":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNi["TM2"].append(dist_temp)
                                if item2[0] == "Nb":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNb["TM2"].append(dist_temp)
                                if item2[0] == "Ti":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiTi["TM2"].append(dist_temp)
                elif li_num == 1:
                    tm3_num += 1
                    tetra_map['type'].append('TM3')

                    ni_num_temp = sum([1 if item[0] == "Ni" else 0
                                       for key, item in dict_temp.items()])
                    nb_num_temp = sum([1 if item[0] == "Nb" else 0
                                       for key, item in dict_temp.items()])
                    ti_num_temp = sum([1 if item[0] == "Ti" else 0
                                       for key, item in dict_temp.items()])
                    key_t1 = "Ni" + str(ni_num_temp)
                    key_t2 = "Nb" + str(nb_num_temp)
                    key_t3 = "Ti" + str(ti_num_temp)
                    key_t = key_t1 + key_t2 + key_t3
                    tm3_details[key_t] += 1

                    for key1, item1 in dict_temp.items():
                        if item1[0] == "Li":
                            for key2, item2 in dict_temp.items():
                                if item2[0] == "Ni":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNi["TM3"].append(dist_temp)
                                if item2[0] == "Nb":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNb["TM3"].append(dist_temp)
                                if item2[0] == "Ti":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiTi["TM3"].append(dist_temp)
                else:
                    tm4_num += 1
                    tetra_map['type'].append('TM4')

                    ni_num_temp = sum([1 if item[0] == "Ni" else 0
                                       for key, item in dict_temp.items()])
                    nb_num_temp = sum([1 if item[0] == "Nb" else 0
                                       for key, item in dict_temp.items()])
                    ti_num_temp = sum([1 if item[0] == "Ti" else 0
                                       for key, item in dict_temp.items()])
                    key_t1 = "Ni" + str(ni_num_temp)
                    key_t2 = "Nb" + str(nb_num_temp)
                    key_t3 = "Ti" + str(ti_num_temp)
                    key_t = key_t1 + key_t2 + key_t3
                    tm4_details[key_t] += 1

                # Calculate the mapping coordinates.
                map_x = 2 * i + 0.5
                map_y = 2 * j + 1.5
                map_z = 2 * k + 1.5
                tetra_map['coord'].append([map_x, map_y, map_z])

                # Specify the index of the mapped point.
                tetra_map['index'].append(7)

                # Specify the location of the unit cell. This is the
                # same as that in the original atomic configuration.
                tetra_map['unit_loc'].append([i, j, k])

                # 8th one.

                # Determine the type of the tetrahedron.
                unit_index_temp_1 = (i_t + 1) * input_config.scDim[1] * \
                    input_config.scDim[2] + \
                    (j_t + 1) * input_config.scDim[2] + (k_t + 1)
                unit_index_temp_7 = i * input_config.scDim[1] * \
                    input_config.scDim[2] + \
                    j * input_config.scDim[2] + (k_t + 1)
                unit_index_temp_5 = i * input_config.scDim[1] * \
                    input_config.scDim[2] + \
                    (j_t + 1) * input_config.scDim[2] + k
                unit_index_temp_3 = (i_t + 1) * input_config.scDim[1] * \
                    input_config.scDim[2] + \
                    j * input_config.scDim[2] + k

                li_num = 0
                temp_temp = input_config.unit_cell_info[unit_index_temp_1][1]
                if temp_temp[0] == 'Li':
                    li_num += 1
                temp_temp = input_config.unit_cell_info[unit_index_temp_7][7]
                if temp_temp[0] == 'Li':
                    li_num += 1
                temp_temp = input_config.unit_cell_info[unit_index_temp_5][5]
                if temp_temp[0] == 'Li':
                    li_num += 1
                temp_temp = input_config.unit_cell_info[unit_index_temp_3][3]
                if temp_temp[0] == 'Li':
                    li_num += 1

                dict_temp = {}
                temp_temp = input_config.unit_cell_info[unit_index_temp_1]
                dict_temp[1] = temp_temp[1]
                temp_temp = input_config.unit_cell_info[unit_index_temp_7]
                dict_temp[7] = temp_temp[7]
                temp_temp = input_config.unit_cell_info[unit_index_temp_5]
                dict_temp[5] = temp_temp[5]
                temp_temp = input_config.unit_cell_info[unit_index_temp_3]
                dict_temp[3] = temp_temp[3]

                if li_num == 4:
                    tm0_num += 1
                    tetra_map['type'].append('TM0')
                elif li_num == 3:
                    tm1_num += 1
                    tetra_map['type'].append('TM1')

                    ni_num_temp = sum([1 if item[0] == "Ni" else 0
                                       for key, item in dict_temp.items()])
                    nb_num_temp = sum([1 if item[0] == "Nb" else 0
                                       for key, item in dict_temp.items()])
                    ti_num_temp = sum([1 if item[0] == "Ti" else 0
                                       for key, item in dict_temp.items()])
                    key_t1 = "Ni" + str(ni_num_temp)
                    key_t2 = "Nb" + str(nb_num_temp)
                    key_t3 = "Ti" + str(ti_num_temp)
                    key_t = key_t1 + key_t2 + key_t3
                    tm1_details[key_t] += 1

                    for key1, item1 in dict_temp.items():
                        if item1[0] == "Li":
                            for key2, item2 in dict_temp.items():
                                if item2[0] == "Ni":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNi["TM1"].append(dist_temp)
                                if item2[0] == "Nb":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNb["TM1"].append(dist_temp)
                                if item2[0] == "Ti":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiTi["TM1"].append(dist_temp)
                elif li_num == 2:
                    tm2_num += 1
                    tetra_map['type'].append('TM2')

                    ni_num_temp = sum([1 if item[0] == "Ni" else 0
                                       for key, item in dict_temp.items()])
                    nb_num_temp = sum([1 if item[0] == "Nb" else 0
                                       for key, item in dict_temp.items()])
                    ti_num_temp = sum([1 if item[0] == "Ti" else 0
                                       for key, item in dict_temp.items()])
                    key_t1 = "Ni" + str(ni_num_temp)
                    key_t2 = "Nb" + str(nb_num_temp)
                    key_t3 = "Ti" + str(ti_num_temp)
                    key_t = key_t1 + key_t2 + key_t3
                    tm2_details[key_t] += 1

                    for key1, item1 in dict_temp.items():
                        if item1[0] == "Li":
                            for key2, item2 in dict_temp.items():
                                if item2[0] == "Ni":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNi["TM2"].append(dist_temp)
                                if item2[0] == "Nb":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNb["TM2"].append(dist_temp)
                                if item2[0] == "Ti":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiTi["TM2"].append(dist_temp)
                elif li_num == 1:
                    tm3_num += 1
                    tetra_map['type'].append('TM3')

                    ni_num_temp = sum([1 if item[0] == "Ni" else 0
                                       for key, item in dict_temp.items()])
                    nb_num_temp = sum([1 if item[0] == "Nb" else 0
                                       for key, item in dict_temp.items()])
                    ti_num_temp = sum([1 if item[0] == "Ti" else 0
                                       for key, item in dict_temp.items()])
                    key_t1 = "Ni" + str(ni_num_temp)
                    key_t2 = "Nb" + str(nb_num_temp)
                    key_t3 = "Ti" + str(ti_num_temp)
                    key_t = key_t1 + key_t2 + key_t3
                    tm3_details[key_t] += 1

                    for key1, item1 in dict_temp.items():
                        if item1[0] == "Li":
                            for key2, item2 in dict_temp.items():
                                if item2[0] == "Ni":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNi["TM3"].append(dist_temp)
                                if item2[0] == "Nb":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiNb["TM3"].append(dist_temp)
                                if item2[0] == "Ti":
                                    dist_temp = dist_calc(item1[1], item2[1],
                                                          vectors, atomsCoord)
                                    tetra_dist_LiTi["TM3"].append(dist_temp)
                else:
                    tm4_num += 1
                    tetra_map['type'].append('TM4')

                    ni_num_temp = sum([1 if item[0] == "Ni" else 0
                                       for key, item in dict_temp.items()])
                    nb_num_temp = sum([1 if item[0] == "Nb" else 0
                                       for key, item in dict_temp.items()])
                    ti_num_temp = sum([1 if item[0] == "Ti" else 0
                                       for key, item in dict_temp.items()])
                    key_t1 = "Ni" + str(ni_num_temp)
                    key_t2 = "Nb" + str(nb_num_temp)
                    key_t3 = "Ti" + str(ti_num_temp)
                    key_t = key_t1 + key_t2 + key_t3
                    tm4_details[key_t] += 1

                # Calculate the mapping coordinates.
                map_x = 2 * i + 1.5
                map_y = 2 * j + 1.5
                map_z = 2 * k + 1.5
                tetra_map['coord'].append([map_x, map_y, map_z])

                # Specify the index of the mapped point.
                tetra_map['index'].append(8)

                # Specify the location of the unit cell. This is the
                # same as that in the original atomic configuration.
                tetra_map['unit_loc'].append([i, j, k])

    total_tetra_num = tm0_num + tm1_num + tm2_num + tm3_num + tm4_num

    # Now, output statistics of local tetrahedrons to file.
    #
    # First, details about tetra environment, i. e. which TM elements
    # are existing in a specific tetra.
    #
    file_num = 1
    while path.exists("TM1_details_" + str(file_num) + ".dat"):
        file_num += 1

    tm1_details_out = open("TM1_details_" + str(file_num) + ".dat", "w")

    file_num = 1
    while path.exists("TM2_details_" + str(file_num) + ".dat"):
        file_num += 1

    tm2_details_out = open("TM2_details_" + str(file_num) + ".dat", "w")

    file_num = 1
    while path.exists("TM3_details_" + str(file_num) + ".dat"):
        file_num += 1

    tm3_details_out = open("TM3_details_" + str(file_num) + ".dat", "w")

    file_num = 1
    while path.exists("TM4_details_" + str(file_num) + ".dat"):
        file_num += 1

    tm4_details_out = open("TM4_details_" + str(file_num) + ".dat", "w")

    tm1_details_out.write("==========================\n")
    tm1_details_out.write("Detailed statistics of TM1\n")
    tm1_details_out.write("==========================\n")
    for key, item in tm1_details.items():
        tm1_details_out.write("{0:<12s}{1:>8d}\n".format(key, item))
    tm1_details_out.write("==========================")

    tm2_details_out.write("==========================\n")
    tm2_details_out.write("Detailed statistics of TM2\n")
    tm2_details_out.write("==========================\n")
    for key, item in tm2_details.items():
        tm2_details_out.write("{0:<12s}{1:>8d}\n".format(key, item))
    tm2_details_out.write("==========================")

    tm3_details_out.write("==========================\n")
    tm3_details_out.write("Detailed statistics of TM3\n")
    tm3_details_out.write("==========================\n")
    for key, item in tm3_details.items():
        tm3_details_out.write("{0:<12s}{1:>8d}\n".format(key, item))
    tm3_details_out.write("==========================")

    tm4_details_out.write("==========================\n")
    tm4_details_out.write("Detailed statistics of TM4\n")
    tm4_details_out.write("==========================\n")
    for key, item in tm4_details.items():
        tm4_details_out.write("{0:<12s}{1:>8d}\n".format(key, item))
    tm4_details_out.write("==========================")

    tm1_details_out.close()
    tm2_details_out.close()
    tm3_details_out.close()
    tm4_details_out.close()

    # Next, output statistics of Li-Tm distances in tetra.
    file_num = 1
    while path.exists("tetra_dists_LiNi_" + str(file_num) + ".dat"):
        file_num += 1

    file_td_lini = open("tetra_dists_LiNi_" + str(file_num) + ".dat", "w")

    file_num = 1
    while path.exists("tetra_dists_LiNb_" + str(file_num) + ".dat"):
        file_num += 1

    file_td_linb = open("tetra_dists_LiNb_" + str(file_num) + ".dat", "w")

    file_num = 1
    while path.exists("tetra_dists_LiTi_" + str(file_num) + ".dat"):
        file_num += 1

    file_td_liti = open("tetra_dists_LiTi_" + str(file_num) + ".dat", "w")

    file_td_lini.write("======================\n")
    file_td_lini.write("Li-Ni distances in TM1\n")
    file_td_lini.write("======================\n")
    file_td_lini.write("Total # = " + str(len(tetra_dist_LiNi["TM1"])) + "\n")
    file_td_lini.write("======================\n")
    if len(tetra_dist_LiNi["TM1"]) > 0:
        file_td_lini.write("--------------------\n")
        file_td_lini.write("Statistics\n")
        file_td_lini.write("--------------------\n")
        file_td_lini.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Mean",
                                  statistics.mean(tetra_dist_LiNi["TM1"])))
        file_td_lini.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Std dev",
                                  statistics.stdev(tetra_dist_LiNi["TM1"])))
        file_td_lini.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Median",
                                  statistics.median(tetra_dist_LiNi["TM1"])))
        file_td_lini.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Min", min(tetra_dist_LiNi["TM1"])))
        file_td_lini.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Max", max(tetra_dist_LiNi["TM1"])))
        file_td_lini.write("======================\n")
        for item in tetra_dist_LiNi["TM1"]:
            file_td_lini.write("{0:10.6F}\n".format(item))
        file_td_lini.write("======================\n")
    file_td_lini.write("Li-Ni distances in TM2\n")
    file_td_lini.write("======================\n")
    file_td_lini.write("Total # = " + str(len(tetra_dist_LiNi["TM2"])) + "\n")
    file_td_lini.write("======================\n")
    if len(tetra_dist_LiNi["TM2"]) > 0:
        file_td_lini.write("--------------------\n")
        file_td_lini.write("Statistics\n")
        file_td_lini.write("--------------------\n")
        file_td_lini.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Mean",
                                  statistics.mean(tetra_dist_LiNi["TM2"])))
        file_td_lini.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Std dev",
                                  statistics.stdev(tetra_dist_LiNi["TM2"])))
        file_td_lini.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Median",
                                  statistics.median(tetra_dist_LiNi["TM2"])))
        file_td_lini.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Min", min(tetra_dist_LiNi["TM2"])))
        file_td_lini.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Max", max(tetra_dist_LiNi["TM2"])))
        file_td_lini.write("======================\n")
        for item in tetra_dist_LiNi["TM2"]:
            file_td_lini.write("{0:10.6F}\n".format(item))
        file_td_lini.write("======================\n")
    file_td_lini.write("Li-Ni distances in TM3\n")
    file_td_lini.write("======================\n")
    file_td_lini.write("Total # = " + str(len(tetra_dist_LiNi["TM3"])) + "\n")
    file_td_lini.write("======================\n")
    if len(tetra_dist_LiNi["TM3"]) > 0:
        file_td_lini.write("--------------------\n")
        file_td_lini.write("Statistics\n")
        file_td_lini.write("--------------------\n")
        file_td_lini.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Mean",
                                  statistics.mean(tetra_dist_LiNi["TM3"])))
        file_td_lini.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Std dev",
                                  statistics.stdev(tetra_dist_LiNi["TM3"])))
        file_td_lini.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Median",
                                  statistics.median(tetra_dist_LiNi["TM3"])))
        file_td_lini.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Min", min(tetra_dist_LiNi["TM3"])))
        file_td_lini.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Max", max(tetra_dist_LiNi["TM3"])))
        file_td_lini.write("======================\n")
        for item in tetra_dist_LiNi["TM3"]:
            file_td_lini.write("{0:10.6F}\n".format(item))
        file_td_lini.write("======================\n")

    file_td_lini.close()

    file_td_linb.write("======================\n")
    file_td_linb.write("Li-Nb distances in TM1\n")
    file_td_linb.write("======================\n")
    file_td_linb.write("Total # = " + str(len(tetra_dist_LiNb["TM1"])) + "\n")
    file_td_linb.write("======================\n")
    if len(tetra_dist_LiNb["TM1"]) > 0:
        file_td_linb.write("--------------------\n")
        file_td_linb.write("Statistics\n")
        file_td_linb.write("--------------------\n")
        file_td_linb.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Mean",
                                  statistics.mean(tetra_dist_LiNb["TM1"])))
        file_td_linb.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Std dev",
                                  statistics.stdev(tetra_dist_LiNb["TM1"])))
        file_td_linb.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Median",
                                  statistics.median(tetra_dist_LiNb["TM1"])))
        file_td_linb.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Min", min(tetra_dist_LiNb["TM1"])))
        file_td_linb.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Max", max(tetra_dist_LiNb["TM1"])))
        file_td_linb.write("======================\n")
        for item in tetra_dist_LiNb["TM1"]:
            file_td_linb.write("{0:10.6F}\n".format(item))
        file_td_linb.write("======================\n")
    file_td_linb.write("Li-Nb distances in TM2\n")
    file_td_linb.write("======================\n")
    file_td_linb.write("Total # = " + str(len(tetra_dist_LiNb["TM2"])) + "\n")
    file_td_linb.write("======================\n")
    if len(tetra_dist_LiNb["TM2"]):
        file_td_linb.write("--------------------\n")
        file_td_linb.write("Statistics\n")
        file_td_linb.write("--------------------\n")
        file_td_linb.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Mean",
                                  statistics.mean(tetra_dist_LiNb["TM2"])))
        file_td_linb.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Std dev",
                                  statistics.stdev(tetra_dist_LiNb["TM2"])))
        file_td_linb.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Median",
                                  statistics.median(tetra_dist_LiNb["TM2"])))
        file_td_linb.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Min", min(tetra_dist_LiNb["TM2"])))
        file_td_linb.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Max", max(tetra_dist_LiNb["TM2"])))
        file_td_linb.write("======================\n")
        for item in tetra_dist_LiNb["TM2"]:
            file_td_linb.write("{0:10.6F}\n".format(item))
        file_td_linb.write("======================\n")
    file_td_linb.write("Li-Nb distances in TM3\n")
    file_td_linb.write("======================\n")
    file_td_linb.write("Total # = " + str(len(tetra_dist_LiNb["TM3"])) + "\n")
    file_td_linb.write("======================\n")
    if len(tetra_dist_LiNb["TM3"]) > 0:
        file_td_linb.write("--------------------\n")
        file_td_linb.write("Statistics\n")
        file_td_linb.write("--------------------\n")
        file_td_linb.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Mean",
                                  statistics.mean(tetra_dist_LiNb["TM3"])))
        file_td_linb.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Std dev",
                                  statistics.stdev(tetra_dist_LiNb["TM3"])))
        file_td_linb.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Median",
                                  statistics.median(tetra_dist_LiNb["TM3"])))
        file_td_linb.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Min", min(tetra_dist_LiNb["TM3"])))
        file_td_linb.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Max", max(tetra_dist_LiNb["TM3"])))
        file_td_linb.write("======================\n")
        for item in tetra_dist_LiNb["TM3"]:
            file_td_linb.write("{0:10.6F}\n".format(item))
        file_td_linb.write("======================\n")

    file_td_linb.close()

    file_td_liti.write("======================\n")
    file_td_liti.write("Li-Ti distances in TM1\n")
    file_td_liti.write("======================\n")
    file_td_liti.write("Total # = " + str(len(tetra_dist_LiTi["TM1"])) + "\n")
    file_td_liti.write("======================\n")
    if len(tetra_dist_LiTi["TM1"]) > 0:
        file_td_liti.write("--------------------\n")
        file_td_liti.write("Statistics\n")
        file_td_liti.write("--------------------\n")
        file_td_liti.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Mean",
                                  statistics.mean(tetra_dist_LiTi["TM1"])))
        file_td_liti.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Std dev",
                                  statistics.stdev(tetra_dist_LiTi["TM1"])))
        file_td_liti.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Median",
                                  statistics.median(tetra_dist_LiTi["TM1"])))
        file_td_liti.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Min", min(tetra_dist_LiTi["TM1"])))
        file_td_liti.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Max", max(tetra_dist_LiTi["TM1"])))
        file_td_liti.write("======================\n")
        for item in tetra_dist_LiTi["TM1"]:
            file_td_liti.write("{0:10.6F}\n".format(item))
        file_td_liti.write("======================\n")
    file_td_liti.write("Li-Ti distances in TM2\n")
    file_td_liti.write("======================\n")
    file_td_liti.write("Total # = " + str(len(tetra_dist_LiTi["TM2"])) + "\n")
    file_td_liti.write("======================\n")
    if len(tetra_dist_LiTi["TM2"]):
        file_td_liti.write("--------------------\n")
        file_td_liti.write("Statistics\n")
        file_td_liti.write("--------------------\n")
        file_td_liti.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Mean",
                                  statistics.mean(tetra_dist_LiTi["TM2"])))
        file_td_liti.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Std dev",
                                  statistics.stdev(tetra_dist_LiTi["TM2"])))
        file_td_liti.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Median",
                                  statistics.median(tetra_dist_LiTi["TM2"])))
        file_td_liti.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Min", min(tetra_dist_LiTi["TM2"])))
        file_td_liti.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Max", max(tetra_dist_LiTi["TM2"])))
        file_td_liti.write("======================\n")
        for item in tetra_dist_LiTi["TM2"]:
            file_td_liti.write("{0:10.6F}\n".format(item))
        file_td_liti.write("======================\n")
    file_td_liti.write("Li-Ti distances in TM3\n")
    file_td_liti.write("======================\n")
    file_td_liti.write("Total # = " + str(len(tetra_dist_LiTi["TM3"])) + "\n")
    file_td_liti.write("======================\n")
    if len(tetra_dist_LiTi["TM3"]) > 0:
        file_td_liti.write("--------------------\n")
        file_td_liti.write("Statistics\n")
        file_td_liti.write("--------------------\n")
        file_td_liti.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Mean",
                                  statistics.mean(tetra_dist_LiTi["TM3"])))
        file_td_liti.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Std dev",
                                  statistics.stdev(tetra_dist_LiTi["TM3"])))
        file_td_liti.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Median",
                                  statistics.median(tetra_dist_LiTi["TM3"])))
        file_td_liti.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Min", min(tetra_dist_LiTi["TM3"])))
        file_td_liti.write("|{0:<7s}|{1:10.6F}|\n".
                           format("Max", max(tetra_dist_LiTi["TM3"])))
        file_td_liti.write("======================\n")
        for item in tetra_dist_LiTi["TM3"]:
            file_td_liti.write("{0:10.6F}\n".format(item))
        file_td_liti.write("======================\n")

    file_td_liti.close()

    # Finally, overall statistics of tetra's.
    file_num = 1
    while path.exists("tetra_report_" + str(file_num) + ".log"):
        file_num += 1

    file_out = open("tetra_report_" + str(file_num) + ".log", "w")

    file_num = 1
    while path.exists("tetra_inputs_" + str(file_num) + ".log"):
        file_num += 1

    file_rec = open("tetra_inputs_" + str(file_num) + ".log", "w")

    now = datetime.datetime.now()
    file_rec.write("================================\n")
    file_rec.write("Time stamp: " + str(now)[:19] + "\n")
    file_rec.write("================================\n")
    file_rec.write("Input RMC6F file: " + file_name + "\n")
    file_out.write("================================\n")
    file_out.write("Time stamp: " + str(now)[:19] + "\n")
    file_out.write("================================\n")
    file_out.write("Total # of tetrhedrons: {0:8d}\n".
                   format(total_tetra_num))
    file_out.write("================================\n\n")
    file_out.write("------------------------\n")
    file_out.write("Breakup of statistics\n")
    file_out.write("------------------------\n")
    file_out.write("{0:5s}|{1:7s}|{2:9s}|\n".
                   format("     ", "   #   ", "  Ratio  "))
    file_out.write("------------------------\n")
    file_out.write("{0:5s}|{1:6d} | {2:6.2F}% |\n".
                   format("TM0", tm0_num,
                          float(tm0_num) / float(total_tetra_num) * 100.0))
    file_out.write("------------------------\n")
    file_out.write("{0:5s}|{1:6d} | {2:6.2F}% |\n".
                   format("TM1", tm1_num,
                          float(tm1_num) / float(total_tetra_num) * 100.0))
    file_out.write("------------------------\n")
    file_out.write("{0:5s}|{1:6d} | {2:6.2F}% |\n".
                   format("TM2", tm2_num,
                          float(tm2_num) / float(total_tetra_num) * 100.0))
    file_out.write("------------------------\n")
    file_out.write("{0:5s}|{1:6d} | {2:6.2F}% |\n".
                   format("TM3", tm3_num,
                          float(tm3_num) / float(total_tetra_num) * 100.0))
    file_out.write("------------------------\n")
    file_out.write("{0:5s}|{1:6d} | {2:6.2F}% |\n".
                   format("TM4", tm4_num,
                          float(tm4_num) / float(total_tetra_num) * 100.0))
    file_out.write("------------------------")

    file_out.close()

    # Write out the mapped RMC6F file, in which each single local tetrahedron
    # is taken as a dummy atom.
    for i in range(total_tetra_num):
        tetra_map['coord'][i][0] /= (2.0 * input_config.scDim[0])
        tetra_map['coord'][i][1] /= (2.0 * input_config.scDim[1])
        tetra_map['coord'][i][2] /= (2.0 * input_config.scDim[2])

    mapped_rmc6f = open("tetra_mapped_" + str(file_num) + ".rmc6f", "w")

    mapped_rmc6f.write("(Version 6f format configuration file)\n")
    mapped_rmc6f.write("(Mapped different types of tetrahedrons)\n")
    mapped_rmc6f.write("Metadata date:        " + str(now)[:10] + "\n")
    mapped_rmc6f.write("Number of types of atoms:   5\n")
    mapped_rmc6f.write("Atom types present:         TM0 TM1 TM2 TM3 TM4\n")
    str_temp = "Number of each atom type:   "
    mapped_rmc6f.write(str_temp + "{0:0d} {1:0d} {2:0d} {3:0d} {4:0d}\n".
                       format(tm0_num, tm1_num,
                              tm2_num, tm3_num, tm4_num))
    mapped_rmc6f.write("Number of moves generated:           0\n")
    mapped_rmc6f.write("Number of moves tried:               0\n")
    mapped_rmc6f.write("Number of moves accepted:            0\n")
    mapped_rmc6f.write("Number of prior configuration saves: 0\n")
    str_temp = "Number of atoms:                     "
    mapped_rmc6f.write(str_temp + str(total_tetra_num) + "\n")
    str_temp = "Supercell dimensions:                "
    str_temp += str(input_config.scDim[0]) + " "
    str_temp += str(input_config.scDim[1]) + " "
    str_temp += str(input_config.scDim[2]) + "\n"
    mapped_rmc6f.write(str_temp)
    str_temp = "Number density (Ang^-3):                 "
    mapped_rmc6f.write(str_temp + "{0:8.6F}\n".format(1.0))
    str_temp = "{0:10.6F}{1:10.6F}{2:10.6F}\n".format(90.0, 90.0, 90.0)
    mapped_rmc6f.write("Cell (Ang/deg): {0:10.6F}{1:10.6F}{2:10.6F}".
                       format(2.0 * input_config.scDim[0],
                              2.0 * input_config.scDim[1],
                              2.0 * input_config.scDim[2]) + str_temp)
    mapped_rmc6f.write("Lattice vectors (Ang):\n")
    mapped_rmc6f.write("{0:10.6F}{1:10.6F}{2:10.6F}\n".
                       format(2.0 * input_config.scDim[0], 0, 0))
    mapped_rmc6f.write("{0:10.6F}{1:10.6F}{2:10.6F}\n".
                       format(0, 2.0 * input_config.scDim[1], 0))
    mapped_rmc6f.write("{0:10.6F}{1:10.6F}{2:10.6F}\n".
                       format(0, 0, 2.0 * input_config.scDim[0]))
    mapped_rmc6f.write("Atoms:\n")

    for i in range(total_tetra_num):
        str_temp = str(i + 1)
        str_temp += " {0:5s}".format(tetra_map['type'][i])
        str_temp += "[1]"
        str_temp += "{0:10.6F}".format(tetra_map['coord'][i][0])
        str_temp += "{0:10.6F}".format(tetra_map['coord'][i][1])
        str_temp += "{0:10.6F}".format(tetra_map['coord'][i][2])
        str_temp += (" " + str(tetra_map['index'][i]) + " ")
        str_temp += (str(tetra_map['unit_loc'][i][0]) + " ")
        str_temp += (str(tetra_map['unit_loc'][i][1]) + " ")
        str_temp += (str(tetra_map['unit_loc'][i][2]) + "\n")

    mapped_rmc6f.close()

    print("\n======================================================")
    print("Statistics about tetrahedrons output to the file:")
    print("tetra_report_" + str(file_num) + ".log")
    print("------------------------------------------------------")
    print("Detailed statistics about tetras output to the files:")
    print("TM1_details_" + str(file_num) + ".dat")
    print("TM2_details_" + str(file_num) + ".dat")
    print("TM3_details_" + str(file_num) + ".dat")
    print("TM4_details_" + str(file_num) + ".dat")
    print("------------------------------------------------------")
    print("Statistics about Li-TM distances output to the files:")
    print("tetra_dists_LiNi" + str(file_num) + ".dat")
    print("tetra_dists_LiNb" + str(file_num) + ".dat")
    print("tetra_dists_LiTi" + str(file_num) + ".dat")
    print("------------------------------------------------------")
    print("The mapped lattice is output in RMC6F format:")
    print("tetra_mapped_" + str(file_num) + ".rmc6f")
    print("======================================================\n")

    # Next, we start to worry about the connectivity of local tetrahedrons.
    if not os.path.isfile("tetra_connect_" + str(file_num)):
        os.mkdir("tetra_connect_" + str(file_num))

    sp_trials = int(input("Input # of trials for starting point: "))
    esp_trials = int(input("Input # of trials for each starting point: "))
    walk_step_lim = int(input("Input the maximum walk steps: ")) - 1

    file_rec.write("# of trials for starting point: " + str(sp_trials) + "\n")
    str_temp = "# of trials for each starting point: "
    file_rec.write(str_temp + str(esp_trials) + "\n")
    file_rec.write("Maximum walk steps: " + str(walk_step_lim + 1) + "\n")
    file_rec.write("================================")

    x_eff_walk = []
    y_eff_walk = []
    z_eff_walk = []
    starters = []

    print("\n==========================================================")
    print("Now, we proceed to analyze the tetrahedron connectivity...")
    print("==========================================================\n")

    for i in range(sp_trials):
        print("Processing starter-" + str(i + 1) + "...")
        x_eff_walk.append([])
        y_eff_walk.append([])
        z_eff_walk.append([])
        start_tetra_0 = math.floor(random() * float(total_tetra_num))
        starters.append(start_tetra_0)
        if not os.path.isfile(os.path.join("tetra_connect_" + str(file_num),
                                           "start" + str(i + 1))):
            os.mkdir(os.path.join("tetra_connect_" + str(file_num),
                                  "start_" + str(i + 1)))
        for j in range(esp_trials):
            start_tetra = start_tetra_0
            tetra_chain = []
            tetra_chain.append(start_tetra)
            x_eff_walk[i].append(0)
            y_eff_walk[i].append(0)
            z_eff_walk[i].append(0)

            x_walk_pos = (random() > 0.5)
            y_walk_pos = (random() > 0.5)
            z_walk_pos = (random() > 0.5)
            walk_step = 0
            walking = True
            while walking:
                dir_dice = random()
                if dir_dice > 2.0 / 3.0:
                    walk_dir = 2
                elif dir_dice > 1.0 / 3.0:
                    walk_dir = 1
                else:
                    walk_dir = 0
                new_tetra_coord = tetra_map['coord'][start_tetra].copy()
                if walk_dir == 0:
                    if x_walk_pos:
                        new_tetra_coord[walk_dir] += \
                            (1.0 / (2 * input_config.scDim[walk_dir]))
                    else:
                        new_tetra_coord[walk_dir] -= \
                            (1.0 / (2 * input_config.scDim[walk_dir]))
                elif walk_dir == 1:
                    if y_walk_pos:
                        new_tetra_coord[walk_dir] += \
                            (1.0 / (2 * input_config.scDim[walk_dir]))
                    else:
                        new_tetra_coord[walk_dir] -= \
                            (1.0 / (2 * input_config.scDim[walk_dir]))
                else:
                    if z_walk_pos:
                        new_tetra_coord[walk_dir] += \
                            (1.0 / (2 * input_config.scDim[walk_dir]))
                    else:
                        new_tetra_coord[walk_dir] -= \
                            (1.0 / (2 * input_config.scDim[walk_dir]))
                if new_tetra_coord[walk_dir] > 1.0:
                    new_tetra_coord[walk_dir] -= 1.0
                if new_tetra_coord[walk_dir] < 0.0:
                    new_tetra_coord[walk_dir] += 1.0
                check_tetra = -1
                for k in range(total_tetra_num):
                    x_diff = abs(tetra_map['coord'][k][0] - new_tetra_coord[0])
                    y_diff = abs(tetra_map['coord'][k][1] - new_tetra_coord[1])
                    z_diff = abs(tetra_map['coord'][k][2] - new_tetra_coord[2])
                    if x_diff < 1E-5 and y_diff < 1E-5 and z_diff < 1E-5:
                        check_tetra = k
                        break
                if check_tetra == -1:
                    print("No available next station found!")
                    print(" Hence we have to stop...")

                if tetra_map['type'][check_tetra] != "TM0":
                    through = False
                else:
                    through = True

                if through:
                    walk_step += 1
                    if walk_dir == 0:
                        x_eff_walk[i][j] += 1
                    elif walk_dir == 1:
                        y_eff_walk[i][j] += 1
                    else:
                        z_eff_walk[i][j] += 1
                    tetra_chain.append(check_tetra)
                    start_tetra = check_tetra

                if (not through) or (walk_step == walk_step_lim):
                    walking = False

            connect_rmc6f = open(os.path.join("tetra_connect_" + str(file_num),
                                              "start_" + str(i + 1),
                                              "walk_" + str(j + 1) + ".rmc6f"),
                                 "w")

            connect_rmc6f.write("(Version 6f format configuration file)\n")
            connect_rmc6f.write("(Mapped different types of tetrahedrons)\n")
            str_temp = "Metadata date:        "
            connect_rmc6f.write(str_temp + str(now)[:10] + "\n")
            connect_rmc6f.write("Number of types of atoms:   1\n")
            connect_rmc6f.write("Atom types present:         TM0\n")
            str_temp = "Number of each atom type:   "
            connect_rmc6f.write(str_temp + "{0:0d}\n".format(walk_step + 1))
            connect_rmc6f.write("Number of moves generated:           0\n")
            connect_rmc6f.write("Number of moves tried:               0\n")
            connect_rmc6f.write("Number of moves accepted:            0\n")
            connect_rmc6f.write("Number of prior configuration saves: 0\n")
            str_temp = "Number of atoms:                     "
            connect_rmc6f.write(str_temp + str(walk_step + 1) + "\n")
            str_temp = "Supercell dimensions:                "
            str_temp += str(input_config.scDim[0]) + " "
            str_temp += str(input_config.scDim[1]) + " "
            str_temp += str(input_config.scDim[2]) + "\n"
            connect_rmc6f.write(str_temp)
            str_temp = "Number density (Ang^-3):                 "
            num_temp = (walk_step + 1) / 8
            for k in range(3):
                num_temp /= input_config.scDim[k]
            connect_rmc6f.write(str_temp + "{0:8.6F}\n".format(num_temp))
            str_temp = "{0:10.6F}{1:10.6F}{2:10.6F}\n".format(90.0, 90.0, 90.0)
            connect_rmc6f.write("Cell (Ang/deg): {0:10.6F}{1:10.6F}{2:10.6F}".
                                format(2.0 * input_config.scDim[0],
                                       2.0 * input_config.scDim[1],
                                       2.0 * input_config.scDim[2]) + str_temp)
            connect_rmc6f.write("Lattice vectors (Ang):\n")
            connect_rmc6f.write("{0:10.6F}{1:10.6F}{2:10.6F}\n".
                                format(2.0 * input_config.scDim[0], 0, 0))
            connect_rmc6f.write("{0:10.6F}{1:10.6F}{2:10.6F}\n".
                                format(0, 2.0 * input_config.scDim[1], 0))
            connect_rmc6f.write("{0:10.6F}{1:10.6F}{2:10.6F}\n".
                                format(0, 0, 2.0 * input_config.scDim[2]))
            connect_rmc6f.write("Atoms:\n")

            for k in range(len(tetra_chain)):
                str_temp = str(k + 1)
                str_temp += " {0:5s}".format(tetra_map['type'][tetra_chain[k]])
                str_temp += "[1]"
                str_temp += "{0:10.6F}".format(tetra_map['coord']
                                               [tetra_chain[k]][0])
                str_temp += "{0:10.6F}".format(tetra_map['coord']
                                               [tetra_chain[k]][1])
                str_temp += "{0:10.6F}".format(tetra_map['coord']
                                               [tetra_chain[k]][2])
                str_temp += " " + str(tetra_map['index'][tetra_chain[k]])
                str_temp += " " + str(tetra_map['unit_loc'][tetra_chain[k]][0])
                str_temp += " " + str(tetra_map['unit_loc'][tetra_chain[k]][1])
                str_temp += " " + str(tetra_map['unit_loc'][tetra_chain[k]][2])
                str_temp += "\n"
                connect_rmc6f.write(str_temp)
            connect_rmc6f.close()

    x_walk_ave = []
    y_walk_ave = []
    z_walk_ave = []
    for i in range(sp_trials):
        num_temp = float(sum(x_eff_walk[i])) / float(len(x_eff_walk[i]))
        x_walk_ave.append(num_temp)
        num_temp = float(sum(y_eff_walk[i])) / float(len(y_eff_walk[i]))
        y_walk_ave.append(num_temp)
        num_temp = float(sum(z_eff_walk[i])) / float(len(z_eff_walk[i]))
        z_walk_ave.append(num_temp)

    tetra_connect_out = open("tetra_connect_" + str(file_num) + ".out", "w")
    str_temp = "('Starter' here means the index of dummy"
    str_temp += " atom in the mapped RMC6F file.)\n"
    tetra_connect_out.write(str_temp)
    tetra_connect_out.write("{0:>8s}{1:>8s}{2:>12s}{3:>12s}{4:>12s}\n".format(
                            "Index", "Starter", "Eff_X_Walk",
                            "Eff_Y_Walk", "Eff_Z_Walk"))
    for i in range(sp_trials):
        tetra_connect_out.write(
            "{0:8d}{1:8d}{2:12F}{3:12F}{4:12F}\n".format(i + 1, starters[i],
                                                         x_walk_ave[i],
                                                         y_walk_ave[i],
                                                         z_walk_ave[i]))
    tetra_connect_out.close()

    print("\n==========================================================")
    print("Statistics about connection of tetrahedrons (TM0) is here:")
    print("tetra_connect_" + str(file_num) + ".out")
    print("----------------------------------------------------------")
    print("The walking trace for each starter and each trial is here:")
    print("tetra_connect_" + str(file_num))
    print("==========================================================\n")

    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("All user inputs are output to the file:")
    print("tetra_inputs_" + str(file_num) + ".log")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")

    # Percolation network algorithm.
    init_rmc6f_name = input("Please input initial RMC6F file name: ")
    print("=====================")
    print("0 -> 0TM only")
    print("1 -> 0TM & 1TM")
    print("2 -> 0TM, 1TM and 2TM")
    print("=====================")
    perco_scheme = -1
    while perco_scheme != 0 or perco_scheme != 1 or perco_scheme != 2:
        perco_scheme = int(input("Please input percolation scheme: "))

    init_config = rmc6f_stuff.RMC6FReader(init_rmc6f_name)

    init_atomsCoord = init_config.atomsCoordInt
    init_vectors = init_config.vectors

    # Figure out neighbor list, based on the provided initial RMC6F
    # configuration.
    neigh = {}
    for key, item in init_config.site_info_dict.items():
        if item[1] != "O" and item[1] != "F":
            neigh[key] = []
            for key1, item1 in init_config.site_info_dict.items():
                if item1[1] != "O" and item1[1] != "F":
                    dist_temp = dist_calc(item[0], item[1], init_vectors,
                                          init_atomsCoord)
                    if 2.90 <= dist_temp <= 2.95:
                        neigh[key].append(key1)

    # Figure out the gate for each neighbour of a specific
    # centering atom.
    gate = {}
    for key, item in neigh.items():
        gate[key] = []
        for label in item:
            neigh_temp = neigh[label]
            common = list(set(item) & set(neigh_temp))
            common_sort = [common[0]]
            coord1 = init_config.site_info_dict[common[0]][2]
            for i in range(3):
                coord2 = init_config.site_info_dict[common[i + 1]][2]
                dist_temp = rmc6f_stuff.dist_calc_coord(coord1, coord2,
                                                        init_vectors)
                if 2.90 <= dist_temp <= 2.95:
                    common_sort.append(common[i + 1])
                    near = i + 1
            for i in range(4):
                if i != 0 and i != near:
                    common_sort.append(common[i])
            gate[key].append(common_sort)

    cluster_num = 0
    num_in_cluster = {}
    num_in_cluster[0] = 0
    site_cluster = {}
    prop_cluster = {}

    # Initialize site cluster info.
    for i in range(input_config.scDim[2]):
        for j in range(input_config.scDim[1]):
            for k in range(input_config.scDim[0]):
                for ref_num in [1, 3, 5, 7]:
                    label_temp = str(k) + "-"
                    label_temp += (str(j) + "-")
                    label_temp += (str(i) + "-")
                    label_temp += str(ref_num)
                    site_cluster[label_temp] = 0

    for i in range(input_config.scDim[2]):
        for j in range(input_config.scDim[1]):
            for k in range(input_config.scDim[0]):
                for ref_num in [1, 3, 5, 7]:
                    label_temp = str(k) + "-"
                    label_temp += (str(j) + "-")
                    label_temp += (str(i) + "-")
                    label_temp += str(ref_num)
                    if input_config.site_info_dict[label_temp][1] == "Li":
                        neigh_check = []
                        for i in range(len(neigh[label_temp])):
                            nb_temp = neigh[label_temp][i]
                            ele_temp = input_config.site_info_dict[nb_temp][1]
                            if ele_temp == "Li":
                                gate_ele = []
                                for item in gate[label_temp][i]:
                                    g_ele_temp = \
                                        input_config.site_info_dict[item]
                                    gate_ele.append(g_ele_temp)
                                if perco_scheme == 0:
                                    sub_cond1 = (gate_ele[0] == "Li")
                                    sub_cond2 = (gate_ele[1] == "Li")
                                    condition_1 = (sub_cond1 and sub_cond2)
                                    sub_cond1 = (gate_ele[2] == "Li")
                                    sub_cond2 = (gate_ele[3] == "Li")
                                    condition_2 = (sub_cond1 and sub_cond2)
                                    if condition_1 or condition_2:
                                        neigh_check.append(neigh[label_temp]
                                                                [i])
                                elif perco_scheme == 1:
                                    if "Li" in gate_ele:
                                        neigh_check.append(neigh[label_temp]
                                                                [i])
                                else:
                                    neigh_check.append(neigh[label_temp]
                                                            [i])
                        Li_neigh_found = False
                        neigh_check_temp = []
                        for neigh_temp in neigh_check:
                            if site_cluster[neigh_temp] != 0:
                                neigh_check_temp.append(neigh_temp)
                                Li_neigh_found = True

                                r = site_cluster[label_temp]
                                t = r
                                t = -num_in_cluster[t]

                                if t < 0:
                                    prop_cluster[neigh_temp] = r
                                else:
                                    r = t
                                    t = -num_in_cluster[t]
                                    if t < 0:
                                        prop_cluster[neigh_temp] = r
                                    else:
                                        while t > 0:
                                            r = t
                                            t = -num_in_cluster[t]
                                        cluster_temp = site_cluster[neigh_temp]
                                        num_in_cluster[cluster_temp] = -r
                                        prop_cluster[neigh_temp] = r
                        if not Li_neigh_found:
                            cluster_num += 1
                            site_cluster[label_temp] = cluster_num
                            num_in_cluster[cluster_num] = 1
                        else:
                            min_proper = 1E10
                            for item in neigh_check_temp:
                                if prop_cluster[item] < min_proper:
                                    min_proper = prop_cluster[item]
                            site_cluster[label_temp] = min_proper

                            prop_c_uniq = []
                            for item in neigh_check_temp:
                                if prop_cluster[item] not in prop_c_uniq:
                                    prop_c_uniq.append(prop_cluster[item])

                            temp_temp = 0
                            for item in prop_c_uniq:
                                temp_temp += num_in_cluster[item]

                            for item in prop_c_uniq:
                                if item == min_proper:
                                    num_in_cluster[item] = temp_temp + 1
                                else:
                                    num_in_cluster[item] = -min_proper

    site_prop = {}
    for i in range(input_config.scDim[2]):
        for j in range(input_config.scDim[1]):
            for k in range(input_config.scDim[0]):
                for ref_num in [1, 3, 5, 7]:
                    label_temp = str(k) + "-"
                    label_temp += (str(j) + "-")
                    label_temp += (str(i) + "-")
                    label_temp += str(ref_num)
                    num_temp = num_in_cluster[site_cluster[label_temp]]
                    if num_temp > 0:
                        site_prop[label_temp] = site_cluster[label_temp]
                    elif num_temp < 0:
                        site_prop[label_temp] = -num_temp

    max_num = -1E10
    for i in range(cluster_num):
        if num_in_cluster[i] > max_num:
            max_num = num_in_cluster[i]
            max_cluster = i

    Li_in_max_cluster = []
    for i in range(input_config.scDim[2]):
        for j in range(input_config.scDim[1]):
            for k in range(input_config.scDim[0]):
                for ref_num in [1, 3, 5, 7]:
                    label_temp = str(k) + "-"
                    label_temp += (str(j) + "-")
                    label_temp += (str(i) + "-")
                    label_temp += str(ref_num)
                    if site_prop[label_temp] == max_cluster:
                        to_append = input_config.site_info_dict[label_temp][3]
                        Li_in_max_cluster.append(to_append)

    cluster_out = open("perco_cluster.out", "w")
    for item in input_config.header():
        cluster_out.write(item)

    index = 0
    for item in Li_in_max_cluster:
        index += 1
        line_temp = str(index) + " " + " ".join(item.split()[1:])
        cluster_out.write(line_temp)
    cluster_out.close()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(main.__doc__)
    else:
        if "-h" in sys.argv:
            print(main.__doc__)
        else:
            file_name = sys.argv[1]
            main(file_name)
