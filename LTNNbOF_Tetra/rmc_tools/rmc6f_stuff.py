# -*- coding: utf-8 -*-
#
# rmc6f_stuff.py
#
# Module containing procedures for processing RMC6F configuration.
#
# Yuanpeng Zhang @ 06/17/19 Monday
# NIST & ORNL
#
from math import ceil
import numpy as np
import sys
import timeit


# Distance calculator.
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
    temp_val = metric[0][0] * x * x
    temp_val += metric[1][1] * y * y
    temp_val += metric[2][2] * z * z
    temp_val += (m12 * x * y + m13 * x * z + m23 * y * z)
    dist_result = np.sqrt(temp_val)

    return dist_result


# Does what the name says.
class RMC6FReader(object):
    def __init__(self, file_name):

        start = timeit.default_timer()

        print("\nReading in the RMC6F configuration...")

        self.fileName = file_name
        rmc6f_config = open(self.fileName, "r")
        self.header = []
        line = rmc6f_config.readline()
        self.header.append(line)
        nta_line_exist = False
        atp_line_exist = False
        neat_line_exist = False
        na_line_exist = False
        sd_line_exist = False
        cell_line_exist = False
        lv_line_exist = False
        den_line_exist = False
        while "Atoms:" not in line:
            line = rmc6f_config.readline()
            self.header.append(line)
            if "Number of types of atoms:" in line:
                nta_line_exist = True
                self.numTypeAtom = int(line.split(":")[1])
            if "Atom types present:" in line:
                atp_line_exist = True
                self.atomTypes = line.split(":")[1].split()
            if "Number of each atom type:" in line:
                neat_line_exist = True
                self.numAtomEachType = [int(x) for x in
                                        line.split(":")[1].split()]
            if "Number of atoms:" in line:
                na_line_exist = True
                self.numAtoms = int(line.split(":")[1].split()[0])
            if "Supercell dimensions:" in line:
                sd_line_exist = True
                self.scDim = [int(x) for x in line.split(":")[1].split()]
            if "Cell (Ang/deg):" in line:
                cell_line_exist = True
                self.lattPara = [float(x) for x in
                                 line.split(":")[1].split()[0:3]]
            if "Number density (Ang^-3):" in line:
                den_line_exist = True
                self.initNumRho = float(line.split(":")[1])
            if "Lattice vectors (Ang):" in line:
                lv_line_exist = True
                self.vectors = []
                for i in range(3):
                    line = rmc6f_config.readline()
                    self.header.append(line)
                    self.vectors.append([float(x) for x in line.split()])
        if (not na_line_exist) or (not sd_line_exist) or \
                (not cell_line_exist) or (not lv_line_exist) or \
                (not den_line_exist):
            print("Problems with header lines in the input RMC6F config file!")
            print("Please check lines containing supercell dimension, total ")
            print("number of atoms, number density and lattice parameters.")
            sys.exit()

        self.atomsLine = []
        self.atomsEle = []
        self.atomsCoord = []
        self.atomsCoordInt = []
        self.site_info_dict = {}

        self.unit_cell_info = []
        temp_val = self.scDim[0] + 1
        temp_val *= (self.scDim[1] + 1)
        temp_val *= (self.scDim[2] + 1)
        for i in range(temp_val):
            self.unit_cell_info.append({})

        print("Progress: ")
        for i in range(self.numAtoms):
            line = rmc6f_config.readline().strip()
            line_s = line.strip()
            self.atomsLine.append(line)
            self.atomsEle.append(line.split()[1])
            self.atomsCoord.append([float(x) for x in line.split()[3:6]])
            self.atomsCoordInt.append([2 * float(x) - 1.0 for
                                       x in line.split()[3:6]])

            unit_x = int(line.split()[-3])
            unit_y = int(line.split()[-2])
            unit_z = int(line.split()[-1])

            atom_index_temp = int(line.split()[-4])

            label_temp = line_s.split()[-3] + "-"
            label_temp += (line_s.split()[-2] + "-")
            label_temp += (line_s.split()[-1] + "-")
            label_temp += (line_s.split()[-4])

            self.site_info_dict[label_temp] = [int(line.split()[0]),
                                               self.atomsEle[i],
                                               self.atomsCoordInt[i],
                                               self.atomsLine[i]]

            index_temp = unit_x * self.scDim[1] * self.scDim[2] + \
                unit_y * self.scDim[2] + unit_z

            temp_val = [line.split()[1], int(line.split()[0])]
            self.unit_cell_info[index_temp][atom_index_temp] = temp_val

            # Tracking progress.
            condition_1 = ((i + 1) % (int(self.numAtoms * 0.01)) == 0)
            condition_2 = (i + 1) != self.numAtoms
            if condition_1 and condition_2:
                if (i + 1) % (int(self.numAtoms * 0.01) * 5) == 0:
                    print(str(ceil((i + 1) * 100.0 / self.numAtoms)) + "%",
                          end='', flush=True)
                else:
                    print(".", end='', flush=True)
                if (i + 1) % (int(self.numAtoms * 0.01) * 20) == 0:
                    print("")

        if ceil((i + 1) * 100.0 / self.numAtoms) == 100:
            print("100%")

        rmc6f_config.close()

        # Configure header lines.
        self.atomsOfType = []
        if nta_line_exist and atp_line_exist and neat_line_exist:
            for i in range(self.numTypeAtom):
                if i == 0:
                    self.atomsOfType.append([x for x in
                                             range(self.numAtomEachType[i])])
                else:
                    self.atomsOfType.append([x + sum(self.numAtomEachType[0:i])
                                             for x in
                                             range(self.numAtomEachType[i])])
        else:
            atoms_ele_set = set(self.atomsEle)
            atoms_ele_uniq = list(atoms_ele_set)
            for i in range(len(atoms_ele_uniq)):
                temp_val = atoms_ele_uniq[i]
                self.atomsOfType.append([j for j in range(self.numAtoms) if
                                         self.atomsEle[j] == temp_val])
            self.numTypeAtom = len(atoms_ele_uniq)
            self.atomTypes = atoms_ele_uniq
            self.numAtomEachType = [len(self.atomsOfType[i]) for i in
                                    range(self.numTypeAtom)]

        stop = timeit.default_timer()

        print("\n------------------------------------------")
        print("RMC6F configuration successfully read in.")
        print("Time taken:{0:11.3F} s".format(stop - start))
        print("------------------------------------------")
