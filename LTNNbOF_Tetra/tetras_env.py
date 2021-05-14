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
                unit_index_temp_7 = unit_index_temp_1

                li_num = 0
                if input_config.unit_cell_info[unit_index_temp][3][0] == 'Li':
                    li_num += 1
                if input_config.unit_cell_info[unit_index_temp][5][0] == 'Li':
                    li_num += 1
                dict_temp = input_config.unit_cell_info[unit_index_temp_1]
                if dict_temp[1][0] == 'Li':
                    li_num += 1
                dict_temp = input_config.unit_cell_info[unit_index_temp_7]
                if dict_temp[7][0] == 'Li':
                    li_num += 1

                dict_temp = {}
                dict_temp[3] = input_config.unit_cell_info[unit_index_temp][3]
                dict_temp[5] = input_config.unit_cell_info[unit_index_temp][5]
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
                unit_index_temp_3 = unit_index_temp_1

                li_num = 0
                if input_config.unit_cell_info[unit_index_temp][5][0] == 'Li':
                    li_num += 1
                if input_config.unit_cell_info[unit_index_temp][7][0] == 'Li':
                    li_num += 1
                temp_temp = input_config.unit_cell_info[unit_index_temp_1][1]
                if temp_temp[0] == 'Li':
                    li_num += 1
                temp_temp = input_config.unit_cell_info[unit_index_temp_3][3]
                if temp_temp[0] == 'Li':
                    li_num += 1

                dict_temp = {}
                dict_temp[5] = input_config.unit_cell_info[unit_index_temp][5]
                dict_temp[7] = input_config.unit_cell_info[unit_index_temp][7]
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
                    unit_index_temp_3 = i * input_config.scDim[1] * \
                        input_config.scDim[2] + \
                        j * input_config.scDim[2] + (k + 1)
                else:
                    unit_index_temp_3 = i * input_config.scDim[1] * \
                        input_config.scDim[2] + \
                        j * input_config.scDim[2] + 0
                if i < (input_config.scDim[0] - 1):
                    unit_index_temp_7 = (i + 1) * input_config.scDim[1] * \
                        input_config.scDim[2] + \
                        j * input_config.scDim[2] + k
                else:
                    unit_index_temp_7 = 0 * input_config.scDim[1] * \
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
                    unit_index_temp_7 = (i + 1) * input_config.scDim[1] * \
                        input_config.scDim[2] + \
                        j * input_config.scDim[2] + k
                else:
                    unit_index_temp_7 = 0 * input_config.scDim[1] * \
                        input_config.scDim[2] + \
                        j * input_config.scDim[2] + k

                li_num = 0
                if input_config.unit_cell_info[unit_index_temp][3][0] == 'Li':
                    li_num += 1
                temp_temp = input_config.unit_cell_info[unit_index_temp_7][7]
                if temp_temp[0] == 'Li':
                    li_num += 1
                temp_temp = input_config.unit_cell_info[unit_index_temp_1][1]
                if temp_temp[0] == 'Li':
                    li_num += 1
                temp_temp = input_config.unit_cell_info[unit_index_temp_5][5]
                if temp_temp[0] == 'Li':
                    li_num += 1

                dict_temp = {}
                dict_temp[3] = input_config.unit_cell_info[unit_index_temp][3]
                temp_temp = input_config.unit_cell_info[unit_index_temp_7]
                dict_temp[7] = temp_temp[7]
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
                unit_index_temp_3 = i * input_config.scDim[1] * \
                    input_config.scDim[2] + \
                    j * input_config.scDim[2] + (k_t + 1)
                unit_index_temp_5 = i * input_config.scDim[1] * \
                    input_config.scDim[2] + \
                    (j_t + 1) * input_config.scDim[2] + k

                li_num = 0
                if input_config.unit_cell_info[unit_index_temp][7][0] == 'Li':
                    li_num += 1
                temp_temp = input_config.unit_cell_info[unit_index_temp_5][5]
                if temp_temp[0] == 'Li':
                    li_num += 1
                temp_temp = input_config.unit_cell_info[unit_index_temp_1][1]
                if temp_temp[0] == 'Li':
                    li_num += 1
                temp_temp = input_config.unit_cell_info[unit_index_temp_3][3]
                if temp_temp[0] == 'Li':
                    li_num += 1

                dict_temp = {}
                dict_temp[7] = input_config.unit_cell_info[unit_index_temp][7]
                temp_temp = input_config.unit_cell_info[unit_index_temp_5]
                dict_temp[5] = temp_temp[5]
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
                unit_index_temp_3 = i * input_config.scDim[1] * \
                    input_config.scDim[2] + \
                    j * input_config.scDim[2] + (k_t + 1)
                unit_index_temp_5 = i * input_config.scDim[1] * \
                    input_config.scDim[2] + \
                    (j_t + 1) * input_config.scDim[2] + k
                unit_index_temp_7 = (i_t + 1) * input_config.scDim[1] * \
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


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(main.__doc__)
    else:
        if "-h" in sys.argv:
            print(main.__doc__)
        else:
            file_name = sys.argv[1]
            main(file_name)
