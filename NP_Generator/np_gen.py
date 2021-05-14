"""Nanoparticle generator
======================

This routine provides capability of generating nanoparticle(s) from
provided RMC6F configuration file as input. This script has been
embodied into the RMCProfile release package, so that one can launch
the RMCProfile terminal and then execute

.. code:: sh

    np_gen RMC6F_FILE_FULL_NAME

to run the generator.

Here following are the major features of this program,

* Generate spherical particle(s) from RMC6F config.
* Generate particles with facets, assuming cubic symmetry, or no symmetry.
* Keep the surface terminated.
* Generate randomly packed multiple particles in box.

.. Attention::

    We need to generate a huge RMC6f configuration \
    (using, e.g. data2config), say, with the dimension of 50x50x50.

.. Attention::

    The program will ask a bunch of questions during execution, as detailed below.

1. The generation scheme -- '0' for generating multiple particles (as close \
packing as possible), '1' for generating a single nanoparticle.
    `If '1' is selected`
        2. Particle shape -- '0' for sphere, '1' for polygon.

            `If '0' is selected`
                2.1. Particle radius

            `If '1' is selected`
                2.1. Roughly estimated particle quasi-radius (of the polygon).

                2.2. Input file containing the facets list.

                    Here follows is provided an example facet list file,

                    :download:`Example facet list file <../../../NP_Generator/facets_list.inp>`

                    Explanation for entries is provided below,

                    =================  =================================================
                    Entry              Description
                    =================  =================================================
                    DISTANCE_MEAN_VAL  | Expected perpendicular distance from the
                                       | center to each facet
                    DISTANCE_VAR_VAL   Variation of the aforementioned distance
                    CUBIC_SYMMETRY     | By specifying cubic symmetry for the system,
                                       | equivalent facets will be generated automatically
                    FACETS             | The number of facets to be specified in the list.
                                       | List of facets should be provided following this
                                       | line, consecutively
                    =================  =================================================

        3. Location of the particle center. A list will be given here, we only need to refer to the list for input options.

        4. Estimated surface layer thickness in angstrom. This is for the purpose of searching for \
        surface termination bonding later on. Usually, ‘3.0’ is a good estimation.

        5. Atom type to be fully coordinated. Usually, we may just want to guarantee metal atoms \
        are fully coordinated and leave, e.g. oxygen dangling. Again, a list of options will be given here.

        6. Atom type we want to terminate the surface with, e.g. oxygen. Here, the utility can only \
        terminate the surface with atoms already existing in the original configuration.

        7. Lower limit to check for surface bonding.

        8. Upper limit to check for surface bonding.

    `If '0' is selected`
        2. Particle radius and its variation in angstrom.

        3. Minimum and maximum of the gap between particles.

        4. Estimated surface layer thickness.

        5. Atom type to be fully coordinated. Usually, we may just want to guarantee metal atoms \
        are fully coordinated and leave, e.g. oxygen dangling. Again, a list of options will be given here.

        6. Atom type we want to terminate the surface with, e.g. oxygen. Here, the utility can only \
        terminate the surface with atoms already existing in the original configuration.

        7. Lower limit to check for surface bonding.

        8. Upper limit to check for surface bonding.

Along with the output RMC6F file for the generated nanoparticle(s), there are
several other output files, as described below,

Single particle generation:
    np_single.out:
        Output information about the generated single nanoparticle and the file \
        content should be self-explanatory.

Multiple particles generation:
    np_rpm.out:
        Output information about the generated particles, where all relevant \
        coordinates are given in fractional form.

    np_rpm_cart.out:
        Output information about the generated particles, where all relevant \
        coordinates are given in Cartesian form.

    np_rpm_par_belong.out:
        Output information about to which particle a certain atom in the output \
        RMC6F configuration belongs.

    np_rpm_rot.out:
        Output information about the rotation angles for each generated particle, \
        as compared to their original orientation in the input RMC6F configuration.
"""
#
# -*- coding: utf-8 -*-
#
import sys
import numpy as np
from random import random
from math import ceil
from numpy.linalg import inv
import timeit
import matplotlib.pyplot as plt
import readline
import os
import atexit
import itertools
from numpy import linalg as LA

# Some metadata of current program.
version = "0.1"
features = """
 - Generate spherical particle(s) from RMC6F config.
 - Generate particles with facets, assuming cubic symmetry, or no symmetry.
 - Keep the surface terminated.
 - Generate randomly packed multiple particles in box.
"""

# Control parameter for generating randomly packed multiple particles.
# DO NOT change it UNLESS needed.
maxWalkTrials = 180

history_path = os.path.expanduser("~/.pyhistory")


def save_history(hist_path=history_path):
    import readline
    readline.write_history_file(hist_path)


if os.path.exists(history_path):
    readline.read_history_file(history_path)

atexit.register(save_history)


# Distance calculator - 1
def dist_calc(atomi, atomj, vectors, atomsCoord):
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
    x = x - 2. * int(x * 0.5) - 1.0
    y = y - 2. * int(y * 0.5) - 1.0
    z = z - 2. * int(z * 0.5) - 1.0
    sum_temp = metric[0][0] * x * x
    sum_temp += metric[1][1] * y * y
    sum_temp += metric[2][2] * z * z
    sum_temp += m12 * x * y
    sum_temp += m13 * x * z
    sum_temp += m23 * y * z
    dist_result = np.sqrt(sum_temp)

    return dist_result


# Distance calculator - 2
def dist_calc_cent(cent_coord, atomj, vectors, atomsCoord):
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
    xa = cent_coord[0] + 3.0
    ya = cent_coord[1] + 3.0
    za = cent_coord[2] + 3.0
    x = xa - atomsCoord[atomj][0]
    y = ya - atomsCoord[atomj][1]
    z = za - atomsCoord[atomj][2]
    x = x - 2.0 * int(x * 0.5) - 1.0
    y = y - 2.0 * int(y * 0.5) - 1.0
    z = z - 2.0 * int(z * 0.5) - 1.0
    sum_temp = metric[0][0] * x * x
    sum_temp += metric[1][1] * y * y
    sum_temp += metric[2][2] * z * z
    sum_temp += m12 * x * y
    sum_temp += m13 * x * z
    sum_temp += m23 * y * z
    dist_result = np.sqrt(sum_temp)

    return dist_result


# Distance calculator - 3
def dist_calc_coord(coord1, coord2, vectors):
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
    xa = coord1[0] + 3.0
    ya = coord1[1] + 3.0
    za = coord1[2] + 3.0
    x = xa - coord2[0]
    y = ya - coord2[1]
    z = za - coord2[2]
    x = x - 2.0 * int(x * 0.5) - 1.0
    y = y - 2.0 * int(y * 0.5) - 1.0
    z = z - 2.0 * int(z * 0.5) - 1.0
    sum_temp = metric[0][0] * x * x
    sum_temp += metric[1][1] * y * y
    sum_temp += metric[2][2] * z * z
    sum_temp += m12 * x * y
    sum_temp += m13 * x * z
    sum_temp += m23 * y * z
    dist_result = np.sqrt(sum_temp)

    return dist_result


def main():

    try:
        rmc6fFN = os.path.join(sys.argv[1], sys.argv[2])
        if sys.argv[2] == '' or sys.argv[2] is None:
            print("\nRMC6F configuration file needs to be provided.")
            sys.exit()
    except (OSError, IndexError):
        print("RMC6F configuration file needs to be provided.")
        sys.exit()

    if sys.argv[2] == "-version" or sys.argv[2] == "-v" or sys.argv[2] == "-V":
        print("===================")
        print("Version " + version)
        print("===================")
        print("\nFeatures available:")
        print(features)
        sys.exit()

    print("\n======================================================")
    print("===============Welcome to NP generator!===============")
    print("=====================Version:", version, "====================")
    print("================Author: Yuanpeng Zhang================")
    print("=============Contact: zyroc1990@gmail.com=============")
    print("======================================================")

    p_temp = "\nPlease input generation scheme (0->packing, 1->single): "
    numParticle = int(input(p_temp))
    if numParticle == 0:
        p_temp = "Please input particle radius and its variation in angstrom: "
        strTemp = input(p_temp)
        strUse = strTemp.replace(",", " ")
        [parSizeT, parSizeVarT] = strUse.split()
        parSize = float(parSizeT)
        parSizeVar = float(parSizeVarT)
        p_temp = "Please input min and max gap between particles in angstrom: "
        strTemp = input(p_temp)
        strUse = strTemp.replace(",", " ")
        [minGapT, maxGapT] = strUse.split()
        minGap = float(minGapT)
        maxGap = float(maxGapT)
        p_temp = "Please input estimated surface layer "
        p_temp += "thickness in angstrom (e.g. 3)"
        print(p_temp)
        p_temp = "(For the purpose of searching for "
        p_temp += "surface termination bonding): "
        SLThickness = float(input(p_temp))
    elif numParticle == 1:
        p_temp = "Please input the shape of NP to "
        p_temp += "generate (0->sphere, 1->poly):"
        shapeGen = int(input(p_temp))
        if shapeGen == 0:
            parSize = float(input("Please input particle radius in angstrom: "))
        elif shapeGen == 1:
            p_temp = "Please estimate the particle 'radius' "
            p_temp += "roughly in anstrom: "
            parSize = float(input(p_temp))
            facets_f = input("Please input the facets list file: ")
        else:
            print("Invalid input! 0->sphere, 1->poly! Please try again!")
            sys.exit()
    else:
        print("Invalid input! 0->packing, 1->single! Please try again!")
        sys.exit()

    start = timeit.default_timer()

    print("\nReading in the RMC6F configuration...")

    rmc6fConfig = open(rmc6fFN, "r")
    header = []
    line = rmc6fConfig.readline()
    header.append(line)
    ntaLineExist = False
    atpLineExist = False
    neatLineExist = False
    naLineExist = False
    sdLineExist = False
    cellLineExist = False
    lvLineExist = False
    denLineExist = False
    while "Atoms:" not in line:
        line = rmc6fConfig.readline()
        header.append(line)
        if "Number of types of atoms:" in line:
            ntaLineExist = True
            numTypeAtom = int(line.split(":")[1])
        if "Atom types present:" in line:
            atpLineExist = True
            atomTypes = line.split(":")[1].split()
        if "Number of each atom type:" in line:
            neatLineExist = True
            numAtomEachType = [int(x) for x in line.split(":")[1].split()]
        if "Number of atoms:" in line:
            naLineExist = True
            numAtoms = int(line.split(":")[1].split()[0])
        if "Supercell dimensions:" in line:
            sdLineExist = True
            scDim = [int(x) for x in line.split(":")[1].split()]
        if "Cell (Ang/deg):" in line:
            cellLineExist = True
            lattPara = [float(x) for x in line.split(":")[1].split()[0:3]]
        if "Number density (Ang^-3):" in line:
            denLineExist = True
            initNumRho = float(line.split(":")[1])
        if "Lattice vectors (Ang):" in line:
            lvLineExist = True
            vectors = []
            for i in range(3):
                line = rmc6fConfig.readline()
                header.append(line)
                vectors.append([float(x) for x in line.split()])
    if (not naLineExist) or (not sdLineExist) or \
            (not cellLineExist) or (not lvLineExist) or \
            (not denLineExist):
        print("Problems with header lines in the input RMC6F config file!")
        print("Please check lines containing supercell dimension, total ")
        print("number of atoms, number density and lattice parameters.")
        sys.exit()

    if numParticle == 1:
        # The important check here is to make sure atoms do not see those from
        # neighbouring cells. The condition is:
        # 2x-2*3 > 2(R+x)/2
        # where 'x' refers to the distance from NP surface to the supercell
        # boundary. 'R' refers to the particle radius. '3' on the left is for
        # the extra space to account for atoms move and surface bonding, etc.
        #
        # Or equivalently, we can think about the question in another way:
        # The empty space along each direction should be larger than half of
        # the overall box size, which gives:
        # BoxSize-(2R+2*3) > BoxSize/2
        # where again '3' is for the extra space to account for atoms move and
        # surface bonding, etc. The result is exactly the same as above.
        #
        # One more thing to mention: even when we have non-orthogonal lattice,
        # still things will work in the same way since what really matters for
        # whether atoms can see those from neighbouring cells is just the distance
        # parallel to the lattice.
        if not all(x > 4.0 * parSize + 12.0 for x in lattPara):
            suggestLM = [int(8 * parSize / (lattPara[i] / scDim[i]))
                         for i in range(3)]
            p_temp_1 = "\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            p_temp_1 += "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            p_temp_2 = "The supercell dimension of the input "
            p_temp_2 += "RMC6F config is not big enough!"
            p_temp_3 = "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            p_temp_3 += "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            print(p_temp_1)
            print(p_temp_2)
            print("The suggested supercell multipliers are", suggestLM)
            print(p_temp_3)
            sys.exit()

    atomsLine = []
    atomsEle = []
    atomsCoord = []
    atomsCoord_ext = []
    print("Progress: ")
    for i in range(numAtoms):
        line = rmc6fConfig.readline()
        atomsLine.append(line)
        atomsEle.append(line.split()[1])
        atomsCoord.append([2.0 * float(x) - 1.0 for x in line.split()[3:6]])
        atomsCoord_ext.append([float(x) for x in line.split()[3:6]])
        # Tracking progress.
        if (i + 1) % (int(numAtoms * 0.01)) == 0 and (i + 1) != numAtoms:
            if (i + 1) % (int(numAtoms * 0.01) * 5) == 0:
                print(str(ceil((i + 1) * 100.0 / numAtoms)) + "%",
                      end='', flush=True)
            else:
                print(".", end='', flush=True)
            if (i + 1) % (int(numAtoms * 0.01) * 20) == 0:
                print("")

    rmc6fConfig.close()

    stop = timeit.default_timer()

    print("\n------------------------------------------")
    print("RMC6F configuration successfully read in.")
    print("Time taken:{0:11.3F} s".format(stop - start))
    print("------------------------------------------")

    # Configure header lines.
    atomsOfType = []
    if ntaLineExist and atpLineExist and neatLineExist:
        for i in range(numTypeAtom):
            if i == 0:
                atomsOfType.append([x for x in range(numAtomEachType[i])])
            else:
                atomsOfType.append([x + sum(numAtomEachType[0:i])
                                    for x in range(numAtomEachType[i])])
    else:
        atomsEleSet = set(atomsEle)
        atomsEleUniq = list(atomsEleSet)
        for i in range(len(atomsEleUniq)):
            atomsOfType.append([j for j in range(numAtoms)
                                if atomsEle[j] == atomsEleUniq[i]])
        numTypeAtom = len(atomsEleUniq)
        atomTypes = atomsEleUniq
        numAtomEachType = [len(atomsOfType[i]) for i in range(numTypeAtom)]

    # One particle generation, where we get rid of the periodic
    # boundary condition by default.
    if numParticle == 1:

        print("\n*************************************************")
        outString = "0 -> Random"
        for i in range(len(atomTypes)):
            outString += (", " + str(i + 1) + " -> " + atomTypes[i])
        print(outString)
        print("*************************************************")
        p_temp = "Please input location of the NP center (see list above): "
        npCent = int(input(p_temp))
        p_temp = "Please input estimated surface layer "
        p_temp += "thickness in angstrom (e.g. 3)"
        print(p_temp)
        p_temp = "(For the purpose of searching for "
        p_temp += "surface termination bonding): "
        SLThickness = float(input(p_temp))

        # Select center of the generated particle.
        print("\nSearching for suitable particle center...")
        start = timeit.default_timer()
        if npCent != 0:
            minD = 10
            minIndex = 0
            for item in atomsOfType[npCent - 1]:
                sum_temp = (atomsCoord[item][0] - 0.5) ** 2
                sum_temp += (atomsCoord[item][1] - 0.5) ** 2
                sum_temp += (atomsCoord[item][2] - 0.5) ** 2
                distTemp = np.sqrt(sum_temp)
                if distTemp <= minD:
                    minD = distTemp
                    minIndex = item
            npCentCoord = atomsCoord[minIndex]
        else:
            xCent = 2.0 * (2.0 * random() - 1.0) * parSize / lattPara[0]
            yCent = 2.0 * (2.0 * random() - 1.0) * parSize / lattPara[1]
            zCent = 2.0 * (2.0 * random() - 1.0) * parSize / lattPara[2]
            npCentCoord = [xCent, yCent, zCent]
            npCentCoord_ext = [(xCent + 1.0) / 2.0, (yCent + 1.0) / 2.0,
                               (zCent + 1.0) / 2.0]

        stop = timeit.default_timer()

        print("\n-------------------------------")
        print("Particle center found.")
        print("Time taken:{0:11.3F} s".format(stop - start))
        print("-------------------------------")

        if shapeGen == 0:
            atomsInclude = []
            atomsOfTypeInPar = []
            atomsOfTypeInSL = []
            atomsOfTypeInDSL = []
            for i in range(numTypeAtom):
                atomsOfTypeInPar.append([])
                atomsOfTypeInSL.append([])
                atomsOfTypeInDSL.append([])

            start = timeit.default_timer()

            print("\nGenerating initial particle...")
            print("Progress: ")
            for i in range(numAtoms):
                # Figure out atom type.
                j = 0
                while j < numTypeAtom:
                    if j == 0:
                        if i < numAtomEachType[j]:
                            iType = j
                            break
                    else:
                        if sum(numAtomEachType[0:j]) <= i < numAtomEachType[j]:
                            iType = j
                            break
                    j += 1

                # Figure out atoms included in the particle and the shell.
                # The shell is for speeding up the searching for surface
                # termination later.
                distTemp = dist_calc_cent(npCentCoord, i, vectors, atomsCoord)
                if distTemp < parSize:
                    atomsInclude.append(1)
                    atomsOfTypeInPar[iType].append(i)
                    if distTemp > parSize - SLThickness:
                        atomsOfTypeInDSL[iType].append(i)
                else:
                    atomsInclude.append(0)
                    if distTemp < parSize + SLThickness:
                        atomsOfTypeInSL[iType].append(i)

                # Tracking progress.
                if (i + 1) % (int(numAtoms * 0.01)) == 0 and (i + 1) != numAtoms:
                    if (i + 1) % (int(numAtoms * 0.01) * 5) == 0:
                        print(str(ceil((i + 1) * 100.0 / numAtoms)) + "%",
                              end='', flush=True)
                    else:
                        print(".", end='', flush=True)
                if (i + 1) % (int(numAtoms * 0.01) * 20) == 0:
                    print("")

            stop = timeit.default_timer()

            print("\n-----------------------------------------")
            print("Initial particle successfully generated.")
            print("Time taken:{0:11.3F} s".format(stop - start))
            print("-----------------------------------------")

            print("\n----------------------------------------------------")
            print("# of atoms included in the initial particle: ",
                  atomsInclude.count(1))
            print("# of atoms of each type in the initial particle: ")
            for i in range(numTypeAtom):
                print(str(i + 1) + " -> " + str(len(atomsOfTypeInPar[i])))
            print("# of atoms of each type within the surface shell: ")
            for i in range(numTypeAtom):
                print(str(i + 1) + " -> " + str(len(atomsOfTypeInSL[i])))
            print("----------------------------------------------------")
        else:
            facets_f_in = open(facets_f, "r")
            facets_f_lines = facets_f_in.readlines()
            dist_mean_found = False
            dist_var_found = False
            facets_found = False
            cubic_symm = False
            symmetry = False
            for line in facets_f_lines:
                if "DISTANCE_MEAN_VAL" in line:
                    dist_mean_found = True
                    dist_mean = float(line.split("::")[1])
                if "DISTANCE_VAR_VAL" in line:
                    dist_var_found = True
                    dist_var = float(line.split("::")[1])
                if "CUBIC_SYMMETRY" in line:
                    cubic_symm = True
                    symmetry = True
                if "FACETS" in line:
                    if line.split("::")[1].strip().isdigit():
                        facets_found = True
                        index_temp = facets_f_lines.index(line)
                        num_facets_init = int(line.split("::")[1])
                        facets_list_init = []
                        for i in range(num_facets_init):
                            line_temp = facets_f_lines[index_temp + i + 1]
                            facets_list_init.append([int(x) for x in
                                                     line_temp.split()])
            if not dist_mean_found:
                print("No 'DISTANCE_MEAN_VAL' keyword found!")
                sys.exit()
            if not dist_var_found:
                print("No 'DISTANCE_MEAN_VAL' keyword found!")
                sys.exit()
            if not facets_found:
                print("No 'FACETS' keyword found or no value follows 'FACETS'!")
                sys.exit()
            facets_list_uniq = []
            facets_list_full = []
            if not symmetry:
                facets_list_uniq = facets_list_init.copy()
            else:
                if cubic_symm:
                    for item in facets_list_init:
                        list_temp = list(itertools.permutations(item))
                        set_temp = set(tuple(x) for x in list_temp)
                        facets_gen = [list(x) for x in set_temp]
                        for each_one in facets_gen:
                            facets_list_uniq.append(each_one)
                    for item in facets_list_uniq:
                        for i in range(2):
                            multi_i = (-1)**(i + 1)
                            for j in range(2):
                                multi_j = (-1)**(j + 1)
                                for k in range(2):
                                    multi_k = (-1)**(k + 1)
                                    mem_temp = [multi_i * item[0],
                                                multi_j * item[1],
                                                multi_k * item[2]]
                                    facets_list_full.append(mem_temp)
                    facets_list_final = [list(x) for x in
                                         set(tuple(x) for x in facets_list_full)]

            facets_dist = []
            for item in facets_list_final:
                dist_temp = dist_mean + (2 * random() - 1.0) * dist_var
                facets_dist.append(dist_temp)

            atomsInclude = []
            atomsOfTypeInPar = []
            atomsOfTypeInSL = []
            atomsOfTypeInDSL = []
            for i in range(numTypeAtom):
                atomsOfTypeInPar.append([])
                atomsOfTypeInSL.append([])
                atomsOfTypeInDSL.append([])

            start = timeit.default_timer()

            print("\nGenerating initial particle...")
            print("Progress: ")
            for i in range(numAtoms):
                # Figure out atom type.
                j = 0
                while j < numTypeAtom:
                    if j == 0:
                        if i < numAtomEachType[j]:
                            iType = j
                            break
                    else:
                        if sum(numAtomEachType[0:j]) <= i < numAtomEachType[j]:
                            iType = j
                            break
                    j += 1

                # Figure out atoms included in the particle and the shell.
                # The shell is for speeding up the searching for surface
                # termination later.
                in_par_temp = True
                in_outer = True
                in_inner = True
                temp_temp = 0

                for item in facets_list_final:
                    sum_temp = item[0] * np.asarray(vectors[0])
                    sum_temp += item[1] * np.asarray(vectors[1])
                    sum_temp += item[2] * np.asarray(vectors[2])
                    vec_0 = sum_temp
                    part1 = atomsCoord_ext[i][0] - npCentCoord_ext[0]
                    part1 *= np.asarray(vectors[0])
                    part2 = atomsCoord_ext[i][1] - npCentCoord_ext[1]
                    part2 *= np.asarray(vectors[1])
                    part3 = atomsCoord_ext[i][2] - npCentCoord_ext[2]
                    part3 *= np.asarray(vectors[2])
                    vec_1 = part1 + part2 + part3

                    vec_proj = np.dot(vec_0, vec_1) / LA.norm(vec_0)

                    if vec_proj > facets_dist[temp_temp]:
                        in_par_temp = False

                    if vec_proj > facets_dist[temp_temp] - SLThickness:
                        in_inner = False

                    if vec_proj > facets_dist[temp_temp] + SLThickness:
                        in_outer = False

                if in_par_temp:
                    atomsInclude.append(1)
                    atomsOfTypeInPar[iType].append(i)
                else:
                    atomsInclude.append(0)
                if in_outer and not in_par_temp:
                    atomsOfTypeInSL[iType].append(i)
                if in_par_temp and not in_inner:
                    atomsOfTypeInDSL[iType].append(i)

                # Tracking progress.
                if (i + 1) % (int(numAtoms * 0.01)) == 0 and (i + 1) != numAtoms:
                    if (i + 1) % (int(numAtoms * 0.01) * 5) == 0:
                        print(str(ceil((i + 1) * 100.0 / numAtoms)) + "%",
                              end='', flush=True)
                    else:
                        print(".", end='', flush=True)
                if (i + 1) % (int(numAtoms * 0.01) * 20) == 0:
                    print("")

            stop = timeit.default_timer()

            print("\n-----------------------------------------")
            print("Initial particle successfully generated.")
            print("Time taken:{0:11.3F} s".format(stop - start))
            print("-----------------------------------------")

            print("\n----------------------------------------------------")
            print("# of atoms included in the initial particle: ",
                  atomsInclude.count(1))
            print("# of atoms of each type in the initial particle: ")
            for i in range(numTypeAtom):
                print(str(i + 1) + " -> " + str(len(atomsOfTypeInPar[i])))
            print("# of atoms of each type within the surface shell: ")
            for i in range(numTypeAtom):
                print(str(i + 1) + " -> " + str(len(atomsOfTypeInSL[i])))
            print("----------------------------------------------------")

        # Next, we worry about surface termination.
        print("\n*************************************************")
        outString = "0 -> None"
        for i in range(len(atomTypes)):
            outString += (", " + str(i + 1) + " -> " + atomTypes[i])
        print(outString)
        print("*************************************************")
        p_temp = "Please input atom types to be fully "
        p_temp += "coordinated (see list above): "
        lineTemp = input(p_temp)
        lineTT = lineTemp.replace(",", " ")
        atomTypesFC = [int(x) for x in lineTT.split()]

        if 0 not in atomTypesFC:
            print("\n*************************************************")
            outString = "0 -> None"
            for i in range(len(atomTypes)):
                outString += (", " + str(i + 1) + " -> " + atomTypes[i])
            print(outString)
            print("*************************************************")
            p_temp = "Please input surface termination "
            p_temp += "atom types (see list above): "
            lineTemp = input(p_temp)
            lineTT = lineTemp.replace(",", " ")
            atomTypesST = [int(x) for x in lineTT.split()]

            if 0 not in atomTypesST:
                bondWinL = []
                bondWinH = []
                print("\n*************************************************")
                outString = ""
                totalNum = 0
                for item in atomTypesFC:
                    for item1 in atomTypesST:
                        totalNum += 1
                        if totalNum == len(atomTypesFC) * len(atomTypesST):
                            outString += (str(item) + "<->" + str(item1))
                        else:
                            outString += (str(item) + "<->" + str(item1) + ", ")
                print(outString)
                print("*************************************************")
                p_temp = "Please input lower limit for surface "
                p_temp += "bonding (see order above):\n"
                bondWinLTemp = input(p_temp)
                p_temp = "Please input upper limit for surface "
                p_temp += "bonding (see order above):\n"
                bondWinHTemp = input(p_temp)
                bondWinLTT = bondWinLTemp.replace(",", " ")
                bondWinHTT = bondWinHTemp.replace(",", " ")
                bondWInLTemp = [float(x) for x in bondWinLTT.split()]
                bondWInHTemp = [float(x) for x in bondWinHTT.split()]
                for i in range(len(atomTypesFC)):
                    bondWinL.append([])
                    bondWinH.append([])
                    for j in range(len(atomTypesST)):
                        bondWinL[i].append(bondWInLTemp[len(atomTypesST) * i + j])
                        bondWinH[i].append(bondWInHTemp[len(atomTypesST) * i + j])

                print("\nWorking on surface termination...")

                start = timeit.default_timer()

                total = 0
                total1 = 0
                for i in range(len(atomTypesST)):
                    total += len(atomsOfTypeInSL[atomTypesST[i] - 1])
                for j in range(len(atomTypesFC)):
                    total1 += len(atomsOfTypeInDSL[atomTypesFC[j] - 1])
                total *= total1
                processed = 0
                print("Progress: ")
                for i in range(len(atomTypesST)):
                    for item in atomsOfTypeInSL[atomTypesST[i] - 1]:
                        j = 0
                        while j < numTypeAtom:
                            if j == 0:
                                if item < numAtomEachType[j]:
                                    iType = j
                                    break
                            else:
                                if sum(numAtomEachType[0:j]) <= item \
                                        < numAtomEachType[j]:
                                    iType = j
                                    break
                            j += 1
                        for j in range(len(atomTypesFC)):
                            for item1 in atomsOfTypeInDSL[atomTypesFC[j] - 1]:
                                distCheck = dist_calc(item, item1, vectors, atomsCoord)
                                if bondWinL[j][i] <= distCheck <= bondWinH[j][i]:
                                    atomsInclude[item] = 1
                                    atomsOfTypeInPar[iType].append(item)
                                # Tracking progress.
                                processed += 1
                                if processed % (int(total * 0.01)) == 0 and \
                                        processed != total:
                                    if processed % (int(total * 0.01) * 5) == 0:
                                        val_temp = processed * 100.0 / total
                                        print(str(ceil(val_temp)) + "%",
                                              end='', flush=True)
                                    else:
                                        print(".", end='', flush=True)
                                if processed % (int(total * 0.01) * 20) == 0:
                                    print("")

                stop = timeit.default_timer()

                print("\n-------------------------------------------")
                print("Surface termination successfully executed.")
                print("Time taken:{0:11.3F} s".format(stop - start))
                print("-------------------------------------------")

        # Configure the number of atoms of each type and the total number of
        # atoms in the finally obtained NP system.
        atomsOfTypeInParUniq = []
        for i in range(numTypeAtom):
            atomsOfTypeInParUniq.append(list(set(atomsOfTypeInPar[i])))

        atomsInPar = []
        lineNum = 0
        for i in range(numAtoms):
            if atomsInclude[i] == 1:
                lineNum += 1
                lineTemp = atomsLine[i]
                str_temp = " ".join(lineTemp.split()[1:])
                lineNew = str(lineNum) + " " + str_temp + "\n"
                atomsInPar.append(lineNew)

        numRhoNew = atomsInclude.count(1) * 1.0 / numAtoms * initNumRho

        numAtomEachTypeNew = []
        for i in range(numTypeAtom):
            numAtomEachTypeNew.append(len(atomsOfTypeInParUniq[i]))
        numAtomEachTypeNewL = [str(x) for x in numAtomEachTypeNew]

        totalNumInParL = str(atomsInclude.count(1))

        for i in range(len(header)):
            if "Number of atoms:" in header[i]:
                header[i] = "Number of atoms: " + totalNumInParL + "\n"
            if "Number of each atom type:" in header[i]:
                str_temp = " ".join(numAtomEachTypeNewL) + "\n"
                header[i] = "Number of each atom type: " + str_temp
            if "Number density (Ang^-3):" in header[i]:
                str_temp = " {0:.6f}".format(numRhoNew) + "\n"
                header[i] = "Number density (Ang^-3):" + str_temp

        NPOutFN = rmc6fFN.split(".")[0] + "_NP.rmc6f"
        NPOut = open(NPOutFN, "w")
        for item in header:
            NPOut.write(item)
        for i in range(atomsInclude.count(1)):
            NPOut.write(atomsInPar[i])

        NPOut.close()

        spInfoOut = open("np_single.out", "w")
        if shapeGen == 0:
            str_temp = "Particle radius (in angstrom): "
            str_temp += "{0:10.3F}\n".format(parSize)
            spInfoOut.write(str_temp)
        else:
            str_temp = "Particle radius estimated as (in angstrom): "
            str_temp += "{0:10.3F}\n".format(parSize)
            spInfoOut.write(str_temp)

        str_temp = "Number of atoms in particle: "
        str_temp += "{0:10d}\n".format(atomsInclude.count(1))
        spInfoOut.write(str_temp)
        str_temp = "Particle center in fractional coordinate (in supercell):\n"
        str_temp += "{0:15.8F}{1:15.8F}{2:15.8F}\n".format(npCentCoord[0],
                                                           npCentCoord[1],
                                                           npCentCoord[2])
        spInfoOut.write(str_temp)
        if npCent == 0:
            spInfoOut.write("Center type: Random\n")
        else:
            spInfoOut.write("Center type: " + atomTypes[npCent - 1] + "\n")

        if shapeGen == 1:
            str_temp = "==============================="
            str_temp += "===========================\n"
            spInfoOut.write(str_temp)
            str_temp = "Facets and their distances (in angstrom) "
            str_temp += " to the center\n"
            spInfoOut.write(str_temp)
            str_temp = "==============================="
            str_temp += "===========================\n"
            spInfoOut.write(str_temp)
            for i in range(len(facets_dist)):
                spInfoOut.write("{0:5d}{1:5d}{2:5d}{3:>5s}{4:8.3F}\n".
                                format(facets_list_final[i][0],
                                       facets_list_final[i][1],
                                       facets_list_final[i][2],
                                       "=",
                                       facets_dist[i]))
            str_temp = "=============================="
            str_temp += "============================"
            spInfoOut.write(str_temp)

        spInfoOut.close()

        print("\n--------------------------------------------------")
        print("Single particle successfully generated.")
        print("The corresponding RMC6F configuration is saved to:")
        print("-----------------")
        print(NPOutFN)
        print("-----------------")
        print("Information of the generated particle is saved to:")
        print("-----------------")
        print("np_single.out")
        print("--------------------------------------------------")

    # Randomly packed multiple particles generation. First, we need to generate a
    # list of center positions. Then we build particles with those centers.
    else:
        # Initialize the 'seed' (starting point) of walker.
        parCentPos = []
        parRadius = []
        parCentPos.append([random(), random(), random()])
        parRadius.append(2 * parSizeVar * random() - parSizeVar + parSize)

        # For the purpose of coordination transformation between Cartesian and
        # crystallographic coordinate systems.
        vecArray = np.asarray(vectors)
        vecArrayInv = inv(vecArray)
        vecInv = vecArrayInv.tolist()

        start = timeit.default_timer()

        str_temp = "\n------------------------------"
        str_temp += "-----------------------------------"
        print(str_temp)
        print("Randomly walking through the box to generate particle positions.")
        print("Max trials at each walk step set to 180, which SHOULD WORK FINE.")
        print("In case one feels necessary to increase this limit, please email ")
        print("-----------------------------------------------------------------")
        print("-------------------------Yuanpeng Zhang--------------------------")
        print("-----------------------zyroc1990@gmail.com-----------------------")
        print("-----------------------------------------------------------------")

        print("Particle positions generated: ")
        print('.', end='', flush=True)

        stillAbleToFind = True
        while stillAbleToFind:
            # We will take each one in the already generated position list
            # as the starting point of the random walking. Therefore, at
            # the very beginning, we make a copy of the already generated
            # positions.
            ableToFind = []
            parCentPosT = parCentPos.copy()
            parRadiusT = parRadius.copy()
            lenBefore = len(parCentPos)
            for i in range(lenBefore):
                ableToFind.append(True)

            # For each cycle, we start from a certain position and keep
            # random walking until we cannot find space to walk
            # (maximum trials reached).
            for i in range(lenBefore):
                walkStep = 0
                while ableToFind[i]:
                    val_temp = 2 * parSizeVar * random()
                    parRadiusTemp = val_temp - parSizeVar + parSize
                    parGapTemp = (maxGap - minGap) * random() + minGap
                    limitReached = False
                    # Here is the walking trial.
                    for j in range(maxWalkTrials):
                        theta = np.pi * random()
                        phi = 2 * np.pi * random()
                        # If we are at the starting position.
                        if walkStep == 0:
                            val_temp = parGapTemp + 2 * SLThickness
                            walkDist = parRadiusTemp + parRadiusT[i] + val_temp
                            startPos = [(x + 1.0) / 2.0 for x in parCentPosT[i]]
                            # Transform RMC6F coordinate to Cartesian coordinate.
                            xTemp = sum(startPos[ii] * vectors[ii][0]
                                        for ii in range(3))
                            yTemp = sum(startPos[ii] * vectors[ii][1]
                                        for ii in range(3))
                            zTemp = sum(startPos[ii] * vectors[ii][2]
                                        for ii in range(3))
                        # If we have already walked away from the starting
                        # position, we just take the very last member (which
                        # is the one just generated before current trial)
                        # in the generated position list as our starting point.
                        else:
                            val_temp = parGapTemp + 2 * SLThickness
                            walkDist = parRadiusTemp + parRadius[-1] + val_temp
                            startPos = [(x + 1.0) / 2.0 for x in parCentPos[-1]]
                            xTemp = sum(startPos[ii] * vectors[ii][0]
                                        for ii in range(3))
                            yTemp = sum(startPos[ii] * vectors[ii][1]
                                        for ii in range(3))
                            zTemp = sum(startPos[ii] * vectors[ii][2]
                                        for ii in range(3))
                        walkVector = [walkDist * np.sin(theta) * np.cos(phi),
                                      walkDist * np.sin(theta) * np.sin(phi),
                                      walkDist * np.cos(theta)]
                        endx = xTemp + walkVector[0]
                        endy = yTemp + walkVector[1]
                        endz = zTemp + walkVector[2]
                        endTemp = [endx, endy, endz]
                        # Transform back to RMC6F coordinate.
                        endxCryst = sum(endTemp[ii] * vecInv[ii][0]
                                        for ii in range(3))
                        endyCryst = sum(endTemp[ii] * vecInv[ii][1]
                                        for ii in range(3))
                        endzCryst = sum(endTemp[ii] * vecInv[ii][2]
                                        for ii in range(3))
                        # Worry about walking out of box.
                        if endxCryst >= 1.0:
                            endxCryst -= 1.0
                        if endxCryst < 0.0:
                            endxCryst += 1.0
                        if endyCryst >= 1.0:
                            endyCryst -= 1.0
                        if endyCryst < 0.0:
                            endyCryst += 1.0
                        if endzCryst >= 1.0:
                            endzCryst -= 1.0
                        if endzCryst < 0.0:
                            endzCryst += 1.0
                        # Check whether there is enough room for
                        # current walk trial.
                        posToCheck = [2.0 * endxCryst - 1.0,
                                      2.0 * endyCryst - 1.0,
                                      2.0 * endzCryst - 1.0]
                        accept = True
                        for k in range(len(parCentPos)):
                            distTemp = dist_calc_coord(posToCheck, parCentPos[k])
                            distTempMin = parRadiusTemp + parRadius[k] + \
                                parGapTemp + 2 * SLThickness
                            if distTemp < distTempMin:
                                accept = False
                                break
                        # If enough room found, accept current trial and
                        # stop walking trials.
                        if accept:
                            break
                        if not accept and j == maxWalkTrials - 1:
                            limitReached = True

                    # If walking stops before reaching the trial limit, that means
                    # room can be found and we should continue walking trials.
                    # Otherwise, we come to an end for current walking with a
                    # certain starting point.
                    if limitReached:
                        ableToFind[i] = False
                    else:
                        walkStep += 1
                        parCentPos.append(posToCheck)
                        parRadius.append(parRadiusTemp)
                        print('.', end='', flush=True)
                        if len(parCentPos) % 10 == 0:
                            print("")

            # After walking trials with each one in the already generated position
            # list as the start point, if no new position is generated, that means
            # we cannot find spaces any more to fill in more particles. Therefore,
            # we should then stop and job is done for particle positions searching.
            lenAfter = len(parCentPos)
            if lenBefore == lenAfter:
                stillAbleToFind = False

        # Output particle centers and radius to file in
        # case of use for analysis later.
        rpmOut = open("np_rpm.out", "w")
        rpmOut.write("# Number of particles generated: {0:4d}.\n".
                     format(len(parCentPos)))
        str_temp = "# Position given in RMC coordinate and "
        str_temp += "radius given in angstrom.\n"
        rpmOut.write(str_temp)
        rpmOut.write("Lattice Vectors: \n")
        for i in range(3):
            rpmOut.write("{0:15.6F}{1:15.6F}{2:15.6F}\n".
                         format(vectors[i][0], vectors[i][1], vectors[i][2]))
        rpmOut.write("{0:4s}{1:>15s}{2:>15s}{3:>15s}{4:>15s}\n".
                     format(" ", "Cent_X", "Cent_Y", "Cent_Z", "Radius"))
        rpmOutCart = open("np_rpm_cart.out", "w")
        rpmOutCart.write("# Number of particles generated: {0:4d}.\n".
                         format(len(parCentPos)))
        str_temp = "# Position given in Cartesian coordinate"
        str_temp += " and all units are in angstrom.\n"
        rpmOutCart.write(str_temp)
        rpmOutCart.write("Lattice Vectors: \n")
        for i in range(3):
            rpmOutCart.write("{0:15.6F}{1:15.6F}{2:15.6F}\n".
                             format(vectors[i][0], vectors[i][1], vectors[i][2]))
        rpmOutCart.write("{0:4s}{1:>15s}{2:>15s}{3:>15s}{4:>15s}\n".
                         format(" ", "Cent_X", "Cent_Y", "Cent_Z", "Radius"))
        for i in range(len(parCentPos)):
            outCentPos = [(x + 1.0) / 2.0 for x in parCentPos[i]]
            # Transform RMC6F coordinate to Cartesian coordinate.
            xTemp = sum(outCentPos[ii] * vectors[ii][0] for ii in range(3))
            yTemp = sum(outCentPos[ii] * vectors[ii][1] for ii in range(3))
            zTemp = sum(outCentPos[ii] * vectors[ii][2] for ii in range(3))
            rpmOut.write("{0:4d}{1:15.6F}{2:15.6F}{3:15.6F}{4:15.6F}\n".
                         format(i + 1, (parCentPos[i][0] + 1.0) / 2.0,
                                (parCentPos[i][1] + 1.0) / 2.0,
                                (parCentPos[i][0] + 1.0) / 2.0, parRadius[i]))
            rpmOutCart.write("{0:4d}{1:15.6F}{2:15.6F}{3:15.6F}{4:15.6F}\n".
                             format(i + 1, xTemp, yTemp, zTemp, parRadius[i]))
        rpmOut.close()
        rpmOutCart.close()

        stop = timeit.default_timer()

        if len(parCentPos) % 10 == 0:
            print("\n-----------------------Output------------------------")
        else:
            print("\n\n-----------------------Output------------------------")
        print("{0:<5d} positions of particles successfully generated.".
              format(len(parCentPos)))
        print("Time taken:{0:11.3F} s".format(stop - start))
        print("Information of generated particles can be found here:")
        print("---------------------nps_rpm.out---------------------")

        print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!!Refer to the plot window for inspection!!!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        # Plot particle centers for inspection.
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        xPos = [(x[0] + 1.0) / 2.0 for x in parCentPos]
        yPos = [(x[1] + 1.0) / 2.0 for x in parCentPos]
        zPos = [(x[2] + 1.0) / 2.0 for x in parCentPos]

        ax.scatter(xPos, yPos, zPos, c='r', marker='o')

        ax.set_xlabel('X RMC Coordinate')
        ax.set_ylabel('Y RMC Coordinate')
        ax.set_zlabel('Z RMC Coordinate')

        plt.title('Center positions of generated particles\nClose to continue',
                  fontname='Comic Sans MS', fontsize=18, pad=24)

        plt.show()

        print("\n-----------------------------------")
        print("Now proceed to generate particles.")
        print("-----------------------------------")

        print("\n*************************************************")
        outString = "0 -> None"
        for i in range(len(atomTypes)):
            outString += (", " + str(i + 1) + " -> " + atomTypes[i])
        print(outString)
        print("*************************************************")
        str_temp = "Please input atom types to be fully "
        str_temp += "coordinated (see list above): "
        lineTemp = input(str_temp)
        lineTT = lineTemp.replace(",", " ")
        atomTypesFC = [int(x) for x in lineTT.split()]

        atomTypesST = [0]
        if 0 not in atomTypesFC:
            print("\n*************************************************")
            outString = "0 -> None"
            for i in range(len(atomTypes)):
                outString += (", " + str(i + 1) + " -> " + atomTypes[i])
            print(outString)
            print("*************************************************")
            str_temp = "Please input surface termination atom "
            str_temp += "types (see list above): "
            lineTemp = input(str_temp)
            lineTT = lineTemp.replace(",", " ")
            atomTypesST = [int(x) for x in lineTT.split()]

            if 0 not in atomTypesST:
                bondWinL = []
                bondWinH = []
                print("\n*************************************************")
                outString = ""
                totalNum = 0
                for item in atomTypesFC:
                    for item1 in atomTypesST:
                        totalNum += 1
                        if totalNum == len(atomTypesFC) * len(atomTypesST):
                            outString += (str(item) + "<->" + str(item1))
                        else:
                            outString += (str(item) + "<->" + str(item1) + ", ")
                print(outString)
                print("*************************************************")
                str_temp = "Please input lower limit for surface "
                str_temp += "bonding (see order above):\n"
                bondWinLTemp = input(str_temp)
                str_temp = "Please input upper limit for surface "
                str_temp += "bonding (see order above):\n"
                bondWinHTemp = input(str_temp)
                bondWinLTT = bondWinLTemp.replace(",", " ")
                bondWinHTT = bondWinHTemp.replace(",", " ")
                bondWInLTemp = [float(x) for x in bondWinLTT.split()]
                bondWInHTemp = [float(x) for x in bondWinHTT.split()]
                for i in range(len(atomTypesFC)):
                    bondWinL.append([])
                    bondWinH.append([])
                    for j in range(len(atomTypesST)):
                        bondWinL[i].append(bondWInLTemp[len(atomTypesST) * i + j])
                        bondWinH[i].append(bondWInHTemp[len(atomTypesST) * i + j])

        atomsInclude = [0 for i in range(numAtoms)]
        atomsToCheck = [i for i, x in enumerate(atomsInclude) if x == 0]
        atomsOfTypeInPar = []
        atomsOfTypeInSL = []
        atomsOfTypeInDSL = []
        parsBelong = [0 for i in range(numAtoms)]

        print("\nGenerating initial particles: ")
        print("Progress: ")

        start = timeit.default_timer()

        for parI in range(len(parCentPos)):
            if parI % 3 == 0:
                print(str(ceil(parI * 100.0 / len(parCentPos))) + "%",
                      end='', flush=True)
            else:
                print('.', end='', flush=True)
            if parI % 10 == 0 and parI != len(parCentPos) - 1 and parI != 0:
                print("")

            atomsOfTypeInPar.append([])
            atomsOfTypeInSL.append([])
            atomsOfTypeInDSL.append([])
            for i in range(numTypeAtom):
                atomsOfTypeInPar[parI].append([])
                atomsOfTypeInSL[parI].append([])
                atomsOfTypeInDSL[parI].append([])

            for i in atomsToCheck:
                # Figure out atom type.
                j = 0
                while j < numTypeAtom:
                    if j == 0:
                        if i < numAtomEachType[j]:
                            iType = j
                            break
                    else:
                        if sum(numAtomEachType[0:j]) <= i < numAtomEachType[j]:
                            iType = j
                            break
                    j += 1

                # Figure out atoms included in the particle and the shell.
                # The shell is for speeding up the searching for surface
                # termination later.
                distTemp = dist_calc_cent(parCentPos[parI], i, vectors, atomsCoord)
                if distTemp < parRadius[parI]:
                    atomsInclude[i] = 1
                    atomsOfTypeInPar[parI][iType].append(i)
                    parsBelong[i] = parI + 1
                    if distTemp > parRadius[parI] - SLThickness:
                        atomsOfTypeInDSL[parI][iType].append(i)
                else:
                    if distTemp < parRadius[parI] + SLThickness:
                        atomsOfTypeInSL[parI][iType].append(i)

            atomsToCheck = [i for i, x in enumerate(atomsInclude) if x == 0]

        print("100%")

        stop = timeit.default_timer()

        print("\n------------------------------------------")
        print("Initial particles successfully generated.")
        print("Time taken:{0:11.3F} s".format(stop - start))
        print("------------------------------------------")

        if 0 not in atomTypesFC and 0 not in atomTypesST:
            print("\nWorking on surface termination of particles: ")
            print("Progress: ")

            start = timeit.default_timer()

            for parI in range(len(parCentPos)):

                if parI % 3 == 0:
                    print(str(ceil(parI * 100.0 / len(parCentPos))) + "%",
                          end='', flush=True)
                else:
                    print('.', end='', flush=True)
                if parI % 10 == 0 and parI != len(parCentPos) - 1 and parI != 0:
                    print("")

                for i in range(len(atomTypesST)):
                    for item in atomsOfTypeInSL[parI][atomTypesST[i] - 1]:
                        j = 0
                        while j < numTypeAtom:
                            if j == 0:
                                if item < numAtomEachType[j]:
                                    iType = j
                                    break
                            else:
                                if sum(numAtomEachType[0:j]) <= item \
                                        < numAtomEachType[j]:
                                    iType = j
                                    break
                            j += 1
                        # When we check the surface termination, one atom in
                        # the surface layer can be possibly bonded to atom in
                        # the particle, which then brings in duplication in
                        # the list. Later on, we will get rid of such duplications.
                        for j in range(len(atomTypesFC)):
                            val_temp = atomsOfTypeInDSL[parI][atomTypesFC[j] - 1]
                            for item1 in val_temp:
                                distCheck = dist_calc(item, item1, vectors, atomsCoord)
                                if bondWinL[j][i] <= distCheck <= bondWinH[j][i]:
                                    atomsInclude[item] = 1
                                    atomsOfTypeInPar[parI][iType].append(item)
                                    parsBelong[item] = parI + 1

            print("100%")

            stop = timeit.default_timer()

            print("\n--------------------------------------------------------")
            print("Surface termination of particles successfully executed.")
            print("Time taken:{0:11.3F} s".format(stop - start))
            print("--------------------------------------------------------")

        # For to get rid of duplicate atoms in the list.
        atomsOfTypeInParUniq = []
        for parI in range(len(parCentPos)):
            atomsOfTypeInParUniq.append([])
            for iType in range(numTypeAtom):
                set_temp = set(atomsOfTypeInPar[parI][iType])
                atomsOfTypeInParUniq[parI].append(list(set_temp))

        # Randomly rotate each generated particle to get rid of correlation beyond
        # particle size.
        print("\nRotating particles to get rid of inter-particle correlation: ")
        print("Progress: ")

        start = timeit.default_timer()

        parRotX = []
        parRotY = []
        parRotZ = []
        for parI in range(len(parCentPos)):

            if parI % 3 == 0:
                print(str(ceil(parI * 100.0 / len(parCentPos))) + "%",
                      end='', flush=True)
            else:
                print('.', end='', flush=True)
            if parI % 10 == 0 and parI != len(parCentPos) - 1 and parI != 0:
                print("")

            thetaX = random() * 2 * np.pi
            thetaY = random() * 2 * np.pi
            thetaZ = random() * 2 * np.pi
            rotMatX = np.array([[1, 0, 0],
                                [0, np.cos(thetaX), -np.sin(thetaX)],
                                [0, np.sin(thetaX), np.cos(thetaX)]])
            rotMatY = np.array([[np.cos(thetaY), 0, np.sin(thetaY)],
                                [0, 1, 0],
                                [-np.sin(thetaY), 0, np.cos(thetaY)]])
            rotMatZ = np.array([[np.cos(thetaZ), -np.sin(thetaZ), 0],
                                [np.sin(thetaZ), np.cos(thetaZ), 0],
                                [0, 0, 1]])

            parRotX.append(thetaX)
            parRotY.append(thetaY)
            parRotZ.append(thetaZ)

            for iType in range(numTypeAtom):
                for atomI in atomsOfTypeInParUniq[parI][iType]:
                    # First, we calculate the vector away from the center.
                    vectorX = (atomsCoord[atomI][0] - parCentPos[parI][0]) / 2.0
                    vectorY = (atomsCoord[atomI][1] - parCentPos[parI][1]) / 2.0
                    vectorZ = (atomsCoord[atomI][2] - parCentPos[parI][2]) / 2.0

                    # Then we worry about the periodic boundary condition (PBC).
                    if vectorX > 0.5:
                        vectorX -= 1.0
                    if vectorX < -0.5:
                        vectorX += 1.0
                    if vectorY > 0.5:
                        vectorY -= 1.0
                    if vectorY < -0.5:
                        vectorY += 1.0
                    if vectorZ > 0.5:
                        vectorZ -= 1.0
                    if vectorZ < -0.5:
                        vectorZ += 1.0

                    # Transform the vector to Cartesian coordinate.
                    vectorTemp = [vectorX, vectorY, vectorZ]
                    vectorXCart = sum(vectorTemp[ii] * vectors[ii][0]
                                      for ii in range(3))
                    vectorYCart = sum(vectorTemp[ii] * vectors[ii][1]
                                      for ii in range(3))
                    vectorZCart = sum(vectorTemp[ii] * vectors[ii][2]
                                      for ii in range(3))

                    # Rotate the vector in Cartesian coordinate ->
                    # first with respect to z axis, then y, then x.
                    vectorCart = np.array([vectorXCart, vectorYCart, vectorZCart])
                    vectorCartN = np.matmul(np.matmul(np.matmul(rotMatX, rotMatY),
                                                      rotMatZ),
                                            vectorCart)

                    # Transform the vector back to RMC coordinate.
                    vectorXNCryst = sum(vectorCartN[ii] * vecInv[ii][0]
                                        for ii in range(3))
                    vectorYNCryst = sum(vectorCartN[ii] * vecInv[ii][1]
                                        for ii in range(3))
                    vectorZNCryst = sum(vectorCartN[ii] * vecInv[ii][2]
                                        for ii in range(3))

                    # Calculate the new position in RMC coordinate.
                    posXNew = vectorXNCryst + (parCentPos[parI][0] + 1.0) / 2.0
                    posYNew = vectorYNCryst + (parCentPos[parI][1] + 1.0) / 2.0
                    posZNew = vectorZNCryst + (parCentPos[parI][2] + 1.0) / 2.0

                    # Again, worry about the PBC.
                    if posXNew < 0:
                        posXNew += 1.0
                    if posXNew >= 1.0:
                        posXNew -= 1.0
                    if posYNew < 0:
                        posYNew += 1.0
                    if posYNew >= 1.0:
                        posYNew -= 1.0
                    if posZNew < 0:
                        posZNew += 1.0
                    if posZNew >= 1.0:
                        posZNew -= 1.0

                    atomsCoord[atomI] = [2.0 * posXNew - 1.0, 2.0 * posYNew - 1.0,
                                         2.0 * posZNew - 1.0]

        print("100%")

        # Output particle rotation in case of use for analysis later.
        rpmRotOut = open("np_rpm_rot.out", "w")
        rpmRotOut.write("# Number of particles generated: {0:4d}.\n".
                        format(len(parCentPos)))
        rpmRotOut.write("# Rotation angle given in radian.\n")
        rpmRotOut.write("{0:4s}{1:>15s}{2:>15s}{3:>15s}\n".
                        format(" ", "Theta_X", "Theta_Y", "Theta_Z"))
        for i in range(len(parCentPos)):
            rpmRotOut.write("{0:4d}{1:15.6F}{2:15.6F}{3:15.6F}\n".
                            format(i + 1, parRotX[i], parRotY[i], parRotZ[i]))
        rpmRotOut.close()

        stop = timeit.default_timer()

        print("\n-----------------Output------------------")
        print("Particles rotation successfully executed.")
        print("Time taken:{0:11.3F} s".format(stop - start))
        print("Information of ration can be found here:")
        print("-------------np_rpm_rot.out--------------")

        # Configure the number of atoms of each type and the total number of
        # atoms in the finally obtained NP system.
        atomsOfTypeInParExt = atomsOfTypeInPar[0]
        for i in range(len(parCentPos)):
            if i > 0:
                for j in range(numTypeAtom):
                    atomsOfTypeInParExt[j].extend(atomsOfTypeInPar[i][j])

        atomsOfTypeInParsUniq = []
        for i in range(numTypeAtom):
            atomsOfTypeInParsUniq.append(list(set(atomsOfTypeInParExt[i])))

        atomsInPar = []
        parsBelongOut = []
        lineNum = 0
        for i in range(numAtoms):
            if atomsInclude[i] == 1:
                lineNum += 1
                lineTemp = atomsLine[i]
                part1 = str(lineNum) + " "
                part2 = " ".join(lineTemp.split()[1:3])
                val_temp_1 = (atomsCoord[i][0] + 1.0) / 2.0
                val_temp_2 = (atomsCoord[i][1] + 1.0) / 2.0
                val_temp_3 = (atomsCoord[i][2] + 1.0) / 2.0
                part3 = "{0:10.7F}{1:10.7F}{2:10.7F}".format(val_temp_1,
                                                             val_temp_2,
                                                             val_temp_3)
                part4 = " " + " ".join(lineTemp.split()[6:]) + "\n"
                lineNew = part1 + part2 + part3 + part4
                atomsInPar.append(lineNew)
                parsBelongOut.append(parsBelong[i])

        numRhoNew = atomsInclude.count(1) * 1.0 / numAtoms * initNumRho

        numAtomEachTypeNew = []
        for i in range(numTypeAtom):
            numAtomEachTypeNew.append(len(atomsOfTypeInParsUniq[i]))
        numAtomEachTypeNewL = [str(x) for x in numAtomEachTypeNew]

        totalNumInParL = str(atomsInclude.count(1))

        for i in range(len(header)):
            if "Number of atoms:" in header[i]:
                header[i] = "Number of atoms: " + totalNumInParL + "\n"
            if "Number of each atom type:" in header[i]:
                str_temp = " ".join(numAtomEachTypeNewL) + "\n"
                header[i] = "Number of each atom type: " + str_temp
            if "Number density (Ang^-3):" in header[i]:
                str_temp = " {0:.6f}".format(numRhoNew) + "\n"
                header[i] = "Number density (Ang^-3):" + str_temp

        NPOutFN = rmc6fFN.split(".")[0] + "_NPs.rmc6f"
        NPOut = open(NPOutFN, "w")
        for item in header:
            NPOut.write(item)
        for i in range(atomsInclude.count(1)):
            NPOut.write(atomsInPar[i])

        NPOut.close()

        # Write out to which particle a certain atom belongs.
        parsBOut = open("np_rpm_par_belong.out", "w")
        str_temp = "# Information about to which particle "
        str_temp += "a certain atom belongs.\n"
        parsBOut.write(str_temp)
        parsBOut.write("# {0:>10s}{1:>10s}\n".format("Atom", "Particle"))
        for i in range(atomsInclude.count(1)):
            parsBOut.write("  {0:10d}{1:10d}\n".format(i + 1, parsBelongOut[i]))
        parsBOut.close()

        print("\n--------------------------------------------------")
        print("Randomly packing particles successfully generated.")
        print("The corresponding RMC6F configuration is saved to:")
        print("--------------------------------------------------")
        print(NPOutFN)
        print("--------------------------------------------------")
        print("Files containing useful information printed to:")
        print("--------------------------------------------------")
        print("np_rpm.out")
        print("np_rpm_cart.out")
        print("np_rpm_rot.out")
        print("np_rpm_par_belong.out")
        print("--------------------------------------------------")

    print("\n======================================================")
    print("======================Job Done!=======================")
    print("======================================================")


if __name__ == '__main__':
    main()
