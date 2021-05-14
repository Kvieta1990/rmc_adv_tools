# -*- coding: utf-8 -*-
#
# dgt_tensor.py
#
# Module containing procedures for calculating the deformation
# gradient tensor. taking the initial and fitted RMC configuration
# as inputs.
#
# Yuanpeng Zhang @ 07/02/19 Tuesday
# NIST & ORNL
#
import numpy as np
from numpy.linalg import inv
import timeit
import datetime
from rmc_tools import rmc6f_stuff
from math import ceil
import os


def dgt_tensor(ref_config, rmc6f_config):

    r_cut = float(input("\nPlease input cutoff for neighbour analysis: "))

    start = timeit.default_timer()

    print("\nFiguring out neighbours of atoms...")

    atoms_neigh = []
    neigh_dist = []

    for i in range(ref_config.numAtoms):
        atoms_neigh.append({})
        neigh_dist.append([])

    total = int((ref_config.numAtoms - 1) * ref_config.numAtoms / 2)
    processed = 0
    print("Progress: ")
    for i in range(ref_config.numAtoms):
        for j in range(ref_config.numAtoms - (i + 1)):
            dist_temp = rmc6f_stuff.dist_calc_coord(ref_config.atomsCoordInt[i],
                                                    ref_config.atomsCoordInt[i + 1 + j],
                                                    ref_config.vectors)
            if dist_temp < r_cut:
                dist_in_neigh = False
                for item in neigh_dist[i]:
                    if abs(dist_temp - item) < 1E-3:
                        dist_in_neigh = True
                        atoms_neigh[i][item].append(i + 1 + j)
                        break
                if not dist_in_neigh:
                    neigh_dist[i].append(dist_temp)
                    atoms_neigh[i][dist_temp] = [i + 1 + j]
                dist_in_neigh = False
                for item in neigh_dist[i + 1 + j]:
                    if abs(dist_temp - item) < 1E-3:
                        dist_in_neigh = True
                        atoms_neigh[i + 1 + j][item].append(i)
                        break
                if not dist_in_neigh:
                    neigh_dist[i + 1 + j].append(dist_temp)
                    atoms_neigh[i + 1 + j][dist_temp] = [i]
            processed += 1
            if processed % (int(total * 0.01)) == 0 and processed != total:
                if processed % (int(total * 0.01) * 5) == 0:
                    print(str(ceil(processed * 100.0 / total)) + "%", end='', flush=True)
                else:
                    print(".", end='', flush=True)
                if processed % (int(total * 0.01) * 20) == 0:
                    print("")

    if (ceil(processed * 100.0 / total) == 100) and \
            (processed % (int(total * 0.01) * 5) == 0):
        print("100%")

    stop = timeit.default_timer()

    print("\n--------------------------------------------")
    print("Neighbours of atoms successfully configured.")
    print("Time taken:{0:11.3F} s".format(stop - start))
    print("--------------------------------------------")

    start = timeit.default_timer()

    print("\nCalculating the deformation gradient tensor...")

    total = sum(len(x) for x in atoms_neigh)

    processed = 0
    print("Progress: ")
    dgt_out = []
    for i in range(ref_config.numAtoms):
        d_mat = np.zeros([3, 3])
        a_mat = np.zeros([3, 3])
        for k in atoms_neigh[i]:
            for item in atoms_neigh[i][k]:
                vec_x_frac = []
                for j in range(3):
                    vec_temp = rmc6f_config.atomsCoord[item][j] - rmc6f_config.atomsCoord[i][j]
                    if vec_temp > 0.5:
                        vec_temp -= 1.0
                    elif vec_temp < -0.5:
                        vec_temp += 1.0
                    vec_x_frac.append(vec_temp)
                vec_xx_frac = []
                for j in range(3):
                    vec_temp = ref_config.atomsCoord[item][j] - ref_config.atomsCoord[i][j]
                    if vec_temp > 0.5:
                        vec_temp -= 1.0
                    elif vec_temp < -0.5:
                        vec_temp += 1.0
                    vec_xx_frac.append(vec_temp)

                vec_x_cart = [sum(vec_x_frac[ii] * ref_config.vectors[ii][iii] for ii
                                  in range(3)) for iii in range(3)]
                vec_xx_cart = [sum(vec_xx_frac[ii] * ref_config.vectors[ii][iii] for ii
                                   in range(3)) for iii in range(3)]

                r_temp = (k - min(neigh_dist[i])) / r_cut
                if r_temp <= 0.5:
                    w_temp = 1.0 - 6.0 * r_temp**2 + 6.0 * r_temp**3
                elif r_temp < 1.0:
                    w_temp = 2.0 - 6.0 * r_temp + 6.0 * r_temp**2 - 2.0 * r_temp**3
                else:
                    w_temp = 0
                d_temp = np.zeros([3, 3])
                a_temp = np.zeros([3, 3])
                for ii in range(3):
                    for jj in range(3):
                        d_temp[ii][jj] = vec_xx_cart[ii] * vec_xx_cart[jj] * w_temp
                        a_temp[ii][jj] = vec_x_cart[ii] * vec_xx_cart[jj] * w_temp

                d_mat += d_temp
                a_mat += a_temp

            processed += 1
            if processed % (int(total * 0.01)) == 0 and processed != total:
                if processed % (int(total * 0.01) * 5) == 0:
                    print(str(ceil(processed * 100.0 / total)) + "%", end='', flush=True)
                else:
                    print(".", end='', flush=True)
                if processed % (int(total * 0.01) * 20) == 0:
                    print("")

        dgt_out.append(np.matmul(a_mat, inv(d_mat)))

    if (ceil(processed * 100.0 / total) == 100) and \
            (processed % (int(total * 0.01) * 5) == 0):
        print("100%")

    epsilon_out = []
    omega_out = []
    for i in range(ref_config.numAtoms):
        epsilon_out.append(np.zeros([3, 3]))
        omega_out.append(np.zeros([3, 3]))

        epsilon_out[i][0][0] = dgt_out[i][0][0]
        epsilon_out[i][0][1] = (dgt_out[i][0][1] + dgt_out[i][1][0]) / 2.0
        epsilon_out[i][0][2] = (dgt_out[i][0][2] + dgt_out[i][2][0]) / 2.0
        epsilon_out[i][1][0] = epsilon_out[i][0][1]
        epsilon_out[i][1][1] = dgt_out[i][1][1]
        epsilon_out[i][1][2] = (dgt_out[i][1][2] + dgt_out[i][2][1]) / 2.0
        epsilon_out[i][2][0] = epsilon_out[i][0][2]
        epsilon_out[i][2][1] = epsilon_out[i][1][2]
        epsilon_out[i][2][2] = dgt_out[i][2][2]

        omega_out[i][0][0] = 0
        omega_out[i][0][1] = (dgt_out[i][0][1] - dgt_out[i][1][0]) / 2.0
        omega_out[i][0][2] = (dgt_out[i][0][2] - dgt_out[i][2][0]) / 2.0
        omega_out[i][1][0] = -omega_out[i][0][1]
        omega_out[i][1][1] = 0
        omega_out[i][1][2] = (dgt_out[i][1][2] - dgt_out[i][2][1]) / 2.0
        omega_out[i][2][0] = -omega_out[i][0][2]
        omega_out[i][2][1] = -omega_out[i][1][2]
        omega_out[i][2][2] = 0

    strain_invar1 = []
    strain_invar2 = []
    for i in range(ref_config.numAtoms):
        strain_invar1.append(sum([epsilon_out[i][j][j] for j in range(3)]))
        sum_temp = 0
        for j in range(3):
            for k in range(3):
                sum_temp += (epsilon_out[i][j][k] * epsilon_out[i][j][k] -
                             epsilon_out[i][j][j] * epsilon_out[i][k][k])
        strain_invar2.append(sum_temp / 2.0)

    base_name = os.path.basename(rmc6f_config.fileName)
    base_name = str(base_name.split(".rmc6f")[0])
    dgt_out_file = open(base_name + "_dgt.out", "w")
    now = datetime.datetime.now()
    dgt_out_file.write("=================================================================\n")
    dgt_out_file.write("Deformation gradient tensor for RMC6F config" +
                       os.path.basename(rmc6f_config.fileName) + "\n")
    dgt_out_file.write("=================================================================\n")
    dgt_out_file.write("Time stamp: " + str(now)[:19] + "\n")
    dgt_out_file.write("=================================================================\n")
    dgt_out_file.write("Total number of atoms: " + str(rmc6f_config.numAtoms) + "\n")
    dgt_out_file.write("=================================================================\n")
    dgt_out_file.write("{0:>10s}{1:>10s}{2:>10s}{3:>10s}{4:>10s}"
                       "{5:>10s}{6:>10s}{7:>10s}{8:>10s}{9:>10s}\n".format("Atoms", "e11", "e12",
                                                                           "e13", "e21", "e22", "e23",
                                                                           "e31", "e32", "e33"))
    for i in range(rmc6f_config.numAtoms):
        dgt_out_file.write("{0:>10d}{1:>10f}{2:>10f}{3:>10f}{4:>10f}"
                           "{5:>10f}{6:>10f}{7:>10f}{8:>10f}{9:>10f}\n".
                           format(i + 1, dgt_out[i][0][0], dgt_out[i][0][1], dgt_out[i][0][2],
                                  dgt_out[i][1][0], dgt_out[i][1][1], dgt_out[i][1][2],
                                  dgt_out[i][2][0], dgt_out[i][2][1], dgt_out[i][2][2]))
    dgt_out_file.write("=================================================================")

    dgt_out_file.close()

    strain_out_file = open(base_name + "_strain.out", "w")
    now = datetime.datetime.now()
    strain_out_file.write("=================================================================\n")
    strain_out_file.write("Strain tensor for RMC6F config" +
                          os.path.basename(rmc6f_config.fileName) + "\n")
    strain_out_file.write("=================================================================\n")
    strain_out_file.write("Time stamp: " + str(now)[:19] + "\n")
    strain_out_file.write("=================================================================\n")
    strain_out_file.write("Total number of atoms: " + str(rmc6f_config.numAtoms) + "\n")
    strain_out_file.write("=================================================================\n")
    strain_out_file.write("{0:>10s}{1:>10s}{2:>10s}{3:>10s}{4:>10s}"
                          "{5:>10s}{6:>10s}{7:>10s}{8:>10s}{9:>10s}\n".format("Atoms", "epsilon11", "epsilon12",
                                                                              "epsilon13", "epsilon21", "epsilon22",
                                                                              "epsilon23", "epsilon31", "epsilon32",
                                                                              "epsilon33"))
    for i in range(rmc6f_config.numAtoms):
        strain_out_file.write("{0:>10d}{1:>10f}{2:>10f}{3:>10f}{4:>10f}"
                              "{5:>10f}{6:>10f}{7:>10f}{8:>10f}{9:>10f}\n".
                              format(i + 1, epsilon_out[i][0][0], epsilon_out[i][0][1], epsilon_out[i][0][2],
                                     epsilon_out[i][1][0], epsilon_out[i][1][1], epsilon_out[i][1][2],
                                     epsilon_out[i][2][0], epsilon_out[i][2][1], epsilon_out[i][2][2]))
    strain_out_file.write("=================================================================")

    strain_out_file.close()

    rot_out_file = open(base_name + "_rot.out", "w")
    now = datetime.datetime.now()
    rot_out_file.write("=================================================================\n")
    rot_out_file.write("Rotation tensor for RMC6F config" +
                       os.path.basename(rmc6f_config.fileName) + "\n")
    rot_out_file.write("=================================================================\n")
    rot_out_file.write("Time stamp: " + str(now)[:19] + "\n")
    rot_out_file.write("=================================================================\n")
    rot_out_file.write("Total number of atoms: " + str(rmc6f_config.numAtoms) + "\n")
    rot_out_file.write("=================================================================\n")
    rot_out_file.write("{0:>10s}{1:>10s}{2:>10s}{3:>10s}{4:>10s}"
                       "{5:>10s}{6:>10s}{7:>10s}{8:>10s}{9:>10s}\n".format("Atoms", "omega11", "omega12",
                                                                           "omega13", "omega21", "omega22",
                                                                           "omega23", "omega31", "omega32",
                                                                           "omega33"))
    for i in range(rmc6f_config.numAtoms):
        rot_out_file.write("{0:>10d}{1:>10f}{2:>10f}{3:>10f}{4:>10f}"
                           "{5:>10f}{6:>10f}{7:>10f}{8:>10f}{9:>10f}\n".
                           format(i + 1, omega_out[i][0][0], omega_out[i][0][1], omega_out[i][0][2],
                                  omega_out[i][1][0], omega_out[i][1][1], omega_out[i][1][2],
                                  omega_out[i][2][0], omega_out[i][2][1], omega_out[i][2][2]))
    rot_out_file.write("=================================================================")

    rot_out_file.close()

    strain_invar_file = open(base_name + "_strain_invar.out", "w")
    now = datetime.datetime.now()
    strain_invar_file.write("=================================================================\n")
    strain_invar_file.write("Strain invariant for RMC6F config" +
                            os.path.basename(rmc6f_config.fileName) + "\n")
    strain_invar_file.write("=================================================================\n")
    strain_invar_file.write("Time stamp: " + str(now)[:19] + "\n")
    strain_invar_file.write("=================================================================\n")
    strain_invar_file.write("Total number of atoms: " + str(rmc6f_config.numAtoms) + "\n")
    strain_invar_file.write("=================================================================\n")
    strain_invar_file.write("{0:>10s}{1:>10s}{2:>10s}\n".format("Atoms", "Invar1", "Invar2"))
    for i in range(rmc6f_config.numAtoms):
        strain_invar_file.write("{0:>10d}{1:>10f}{2:>10f}\n".format(i + 1, strain_invar1[i],
                                                                    strain_invar2[i]))
    strain_invar_file.write("=================================================================")

    strain_invar_file.close()

    stop = timeit.default_timer()

    print("\n----------------------------------------------------")
    print("Deformation gradient tensor successfully calculated.")
    print("Time taken:{0:11.3F} s".format(stop - start))
    print("----------------------------------------------------")
    print("List of output files:")
    print("----------------------------------------------------")
    print("Deformation gradient tensor: " + base_name + "_dgt.out")
    print("Strain tensor: " + base_name + "_strain.out")
    print("Rotation tensor: " + base_name + "_rot.out")
    print("Strain invariants: " + base_name + "_strain_invar.out")
    print("----------------------------------------------------")
