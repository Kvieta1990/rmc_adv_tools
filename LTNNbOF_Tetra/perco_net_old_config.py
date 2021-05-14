# -*- coding: utf-8 -*-
#
# perco_net_old_config.py
#
# Python script for analyzing the Li percolation network.
#
# Yuanpeng Zhang @ Sun 6-Sep-20
# NIST & ORNL
#
import sys
from rmc_tools import rmc6f_stuff
import numpy as np


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
    perco_net_old_config.py

    Usage:
        python perco_net_old_config.py RMC6F_FILE_NAME
        - Typing 'python perco_net_old_config.py -h' will print out
        - current help.

    Documentation:
        This script is written based on the algorithm presented in the
        following citation:
        J. Hoshen and R. Kopclman, Phys. Rev. B, 14 (1976), 3438-3445.

    Output:
        All Li atoms involved in the largest cluster will be saved into
        a separate RMC6F file.

    ATTENTION:
        THE HEADER IN THE OUTPUT RMC6F FILE WAS NOT CONFIGURED AUTOMATICALLY.
        THEREFORE, USER HAS TO MANUALLY CHANGE THE HEADER!!!

    Author:
        Yuanpeng Zhang @ Sun 6-Sep-20
        Computational Instrument Scientist (CIS) @ ORNL
    """

    input_config = rmc6f_stuff.RMC6FReader(file_name)

    # Read in user inputs - initial RMC6F file and percolation scheme.
    init_rmc6f_name = input("Please input initial RMC6F file name: ")
    print("=====================")
    print("0 -> 0TM only")
    print("1 -> 0TM & 1TM")
    print("2 -> 0TM, 1TM and 2TM")
    print("=====================")
    perco_scheme = -1
    while perco_scheme != 0 or perco_scheme != 1 or perco_scheme != 2:
        perco_scheme = int(input("Please input percolation scheme: "))

    # Read in the initial RMC6F file - for the purpose of initializing
    # the neighbor list, purely based on distances between atoms.
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
                    # The 'dist_calc' function defined in current
                    # script was there for historic reason. Later on,
                    # I realized we have another more useful distance
                    # calculator defined in 'rmc6f_stuff' module (which
                    # is used below). Here I am lazy, so we still use
                    # the one defined in current script.
                    dist_temp = dist_calc(item[0], item1[0],
                                          init_vectors,
                                          init_atomsCoord)
                    if 2.90 <= dist_temp <= 2.95:
                        neigh[key].append(key1)

    # Figure out the gate for each neighbour. Focusing on one centering
    # atom, we have a few neighbors. Each neighbor has its own neighbor
    # list. We found that the gate for the centering atom and any of its
    # neighbor is just the common members of the neighbor list for both.
    # Among those common members (i. e. the final list of gate atoms for
    # each neighbor), we want to put those next to each other together,
    # for the purpose of further analysis for Li diffusion.
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
                    # Here for each centering Li atom, we want to figure out
                    # its real neighbors, i. e. those neighboring sites
                    # occupied actually by Li, but not TM's.
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
                        # Now we figured out the real neighbors, and the next
                        # step is just to follow Fig. 1 in J. Hoshen's paper
                        # (see the doc of current script). Here
                        # 'neigh_check_temp' list contains those neighboring
                        # Li sites which are already scanned (thus should be
                        # with a non-zero cluster number).
                        Li_neigh_found = False
                        neigh_check_temp = []
                        for neigh_temp in neigh_check:
                            if site_cluster[neigh_temp] != 0:
                                neigh_check_temp.append(neigh_temp)
                                Li_neigh_found = True

                                # Here is the algorithm presented in Fig. 2
                                # in J. Hoshen's (see the doc of current
                                # script).
                                r = site_cluster[neigh_temp]
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

    # Now, proceed to output stage. First, we figure out the proper
    # cluster for each site, based on their originally assigned
    # cluster number. Accoding to J. Hoshen, to figure out whether
    # a cluster number is a proper one or not is very simple - just
    # look at the number of atoms in the cluster. If it is positive,
    # then it is a proper cluster. Otherwise it is considered to be
    # connected to another proper cluster - the negative number then
    # specifies the connection (the corresponding positive number is
    # just the proper cluster that it is connected to).
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

    # Output the number of Li atoms contained in all clusters.
    num_of_li_atoms_in_c_f = open("Number_of_Li_Atoms_in_Cluster.out", "w")
    num_of_li_atoms_in_c_f.write("Cluster\t# of Li atoms\n")
    for i in range(cluster_num):
        if num_in_cluster[i] > 0:
            num_of_li_atoms_in_c_f.write("{0:5d}{1:10d}\n".format(i, num_in_cluster[i]))
    num_of_li_atoms_in_c_f.close()

    # Figure out which cluster contains the most Li atoms. According to
    # J. Hoshen, the 'num_in_cluster' here in current script already
    # contains the contribution from all connected clusters.
    max_num = -1E10
    for i in range(cluster_num):
        if num_in_cluster[i] > max_num:
            max_num = num_in_cluster[i]
            max_cluster = i

    # Find out all Li atoms contained in the largest cluster.
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

    # Write out RMC6F file.
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
