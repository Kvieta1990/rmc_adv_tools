# -*- coding: utf-8 -*-
#
# atomeye_reader.py
#
# Module containing procedures for processing RMC6F configuration.
#
# Yuanpeng Zhang @ 06/24/19 Monday
# NIST & ORNL
#
import timeit
import sys


class AtomeyeReader(object):
    def __init__(self, gen_from, header_num, file_name):

        start = timeit.default_timer()

        print("\nReading in the atomeye configuration...")

        self.gen_from = gen_from
        self.header_num = header_num
        self.fileName = file_name

        self.atom_coords = []
        self.vectors = [[0 * i * j for i in range(3)] for j in range(3)]
        atomeye_config = open(self.fileName, "r")
        if self.gen_from == "lammps":
            for i in range(self.header_num):
                line = atomeye_config.readline()
                if i == 0:
                    self.atom_num = int(line.split()[-1])
                if "H0(1,1)" in line:
                    self.vectors[0][0] = float(line.split("=")[1].split("A")[0])
                if "H0(1,2)" in line:
                    self.vectors[0][1] = float(line.split("=")[1].split("A")[0])
                if "H0(1,3)" in line:
                    self.vectors[0][2] = float(line.split("=")[1].split("A")[0])
                if "H0(2,1)" in line:
                    self.vectors[1][0] = float(line.split("=")[1].split("A")[0])
                if "H0(2,2)" in line:
                    self.vectors[1][1] = float(line.split("=")[1].split("A")[0])
                if "H0(2,3)" in line:
                    self.vectors[1][2] = float(line.split("=")[1].split("A")[0])
                if "H0(3,1)" in line:
                    self.vectors[2][0] = float(line.split("=")[1].split("A")[0])
                if "H0(3,2)" in line:
                    self.vectors[2][1] = float(line.split("=")[1].split("A")[0])
                if "H0(3,3)" in line:
                    self.vectors[2][2] = float(line.split("=")[1].split("A")[0])

            for i in range(self.atom_num):
                for j in range(2):
                    atomeye_config.readline()
                line = atomeye_config.readline()
                self.atom_coords.append([float(x) for x in line.split()[0:3]])
            for i in range(self.atom_num):
                for j in range(3):
                    if self.atom_coords[i][j] < 0:
                        self.atom_coords[i][j] += 1.0
                    elif self.atom_coords[i][j] >= 1.0:
                        self.atom_coords[i][j] -= 1.0
        else:
            print("Only atomeye config dumped from LAMMPS is supported!")
            sys.exit()

        stop = timeit.default_timer()

        print("\n-------------------------------------------")
        print("Atomeye configuration successfully read in.")
        print("Time taken:{0:11.3F} s".format(stop - start))
        print("-------------------------------------------")
