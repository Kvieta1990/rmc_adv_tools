from math import gcd
import numpy as np
import sys
import os


def to_lammps(rmc6f_config):

    atom_style_support = ["atomic", "charge"]
    package_directory = os.path.dirname(os.path.abspath(__file__))

    gcd_temp = rmc6f_config.numAtomEachType[0]
    for item in rmc6f_config.numAtomEachType:
        gcd_temp = gcd(gcd_temp, item)
    gcd_divided = [int(x/gcd_temp) for x in rmc6f_config.numAtomEachType]

    a_vec = np.asarray(rmc6f_config.vectors[0])
    b_vec = np.asarray(rmc6f_config.vectors[1])
    c_vec = np.asarray(rmc6f_config.vectors[2])

    alpha = np.arccos(np.dot(b_vec, c_vec) / (np.linalg.norm(b_vec) * np.linalg.norm(c_vec)))
    beta = np.arccos(np.dot(a_vec, c_vec) / (np.linalg.norm(a_vec) * np.linalg.norm(c_vec)))
    gamma = np.arccos(np.dot(a_vec, b_vec) / (np.linalg.norm(a_vec) * np.linalg.norm(b_vec)))

    lx = np.linalg.norm(a_vec)
    xy = np.linalg.norm(b_vec) * np.cos(gamma)
    xz = np.linalg.norm(c_vec) * np.cos(beta)
    ly = np.sqrt((np.linalg.norm(b_vec))**2 - xy**2)
    yz = (np.linalg.norm(b_vec) * np.linalg.norm(c_vec) *
          np.cos(alpha) - xy * xz) / ly
    lz = np.sqrt(np.linalg.norm(c_vec)**2 - xz**2 - yz**2)

    x_lo = 0.0
    y_lo = 0.0
    z_lo = 0.0
    x_hi = x_lo + lx
    y_hi = y_lo + ly
    z_hi = z_lo + lz

    atoms_table = []
    ele_table = []
    atom_tf = open(os.path.join(package_directory, "atoms_table.dat"), "r")
    atoms = atom_tf.readlines()
    for item in atoms:
        if len(item) > 0:
            atoms_table.append(item.split())
            ele_table.append(item.split()[2])
    atom_mass = []
    for item in rmc6f_config.atomTypes:
        index_temp = ele_table.index(item)
        atom_mass.append(float(atoms_table[index_temp][0]))

    atom_style = input("\nPlease input atom style (atomic, charge): ")
    if atom_style not in atom_style_support:
        print("Atom style" + atom_style + "not supported yet. Hence we have to stop...")
        sys.exit()
    if atom_style == 'charge':
        print("\n---------------------------------")
        for i in range(rmc6f_config.numTypeAtom):
            print(str(i+1) + "->" + rmc6f_config.atomTypes[i] + " ", end='')
        print("\n---------------------------------")
        line_temp = input("Please input atomic charges (following the order above): ")
        line_temp = line_temp.replace(",", " ")
        atomic_charge = [float(x) for x in line_temp.split()]

    lammps_out = open(rmc6f_config.fileName.split(".")[0] + ".lmp", "w")
    lammps_out.write(" #")
    for i in range(rmc6f_config.numTypeAtom):
        lammps_out.write(" " + rmc6f_config.atomTypes[i] + str(gcd_divided[i]))
    lammps_out.write("\n\n")
    lammps_out.write("{0:>12d}  atoms\n".format(rmc6f_config.numAtoms))
    lammps_out.write("{0:>12d}  atom types\n\n".format(rmc6f_config.numTypeAtom))
    lammps_out.write("{0:>16.8F}{1:17.8F}  xlo xhi\n".format(x_lo, x_hi))
    lammps_out.write("{0:>16.8F}{1:17.8F}  ylo yhi\n".format(y_lo, y_hi))
    lammps_out.write("{0:>16.8F}{1:17.8F}  zlo zhi\n".format(z_lo, z_hi))
    if abs(xy - 0.0) > 1E-10 or abs(xz - 0.0) > 1E-10 or abs(yz - 0.0) > 1E-10:
        lammps_out.write("{0:>16.8F}{1:17.8F}{2:17.8F}  xy xz yz\n\n".
                         format(xy, xz, yz))
    else:
        lammps_out.write("\n")
    lammps_out.write("Masses\n\n")
    for i in range(rmc6f_config.numTypeAtom):
        lammps_out.write("{0:>12d}{1:14.8F}    # {2:2s}\n".
                         format(i + 1, atom_mass[i], rmc6f_config.atomTypes[i]))
    if atom_style == 'atomic':
        lammps_out.write("\nAtoms # atomic\n\n")
    elif atom_style == 'charge':
        lammps_out.write("\nAtoms # charge\n\n")
    for i in range(rmc6f_config.numAtoms):
        x_temp = sum(rmc6f_config.atomsCoord[i][ii] * rmc6f_config.vectors[ii][0] for ii in range(3))
        y_temp = sum(rmc6f_config.atomsCoord[i][ii] * rmc6f_config.vectors[ii][1] for ii in range(3))
        z_temp = sum(rmc6f_config.atomsCoord[i][ii] * rmc6f_config.vectors[ii][2] for ii in range(3))
        atom_type_temp = rmc6f_config.atomTypes.index(rmc6f_config.atomsEle[i]) + 1
        lammps_out.write("{0:>10d}{1:>5d}{2:>18.8F}{3:>17.8F}{4:>17.8F}{5:>17.8F}\n".
                         format(i + 1, atom_type_temp, atomic_charge[atom_type_temp - 1],
                               x_temp, y_temp, z_temp))
    lammps_out.close()

    print("\n=================================")
    print("LAMMPS config output to: ")
    print(rmc6f_config.fileName.split(".")[0] + ".lmp")
    print("=================================")
