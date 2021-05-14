import numpy as np
from numpy import linalg as la


def atomeye_to_rmc(ref_config, atomeye_config):

    header = ref_config.header

    cell_a = la.norm(np.asarray(atomeye_config.vectors[0]))
    cell_b = la.norm(np.asarray(atomeye_config.vectors[1]))
    cell_c = la.norm(np.asarray(atomeye_config.vectors[2]))
    alpha = np.arccos(np.dot(np.asarray(atomeye_config.vectors[1]),
                             np.asarray(atomeye_config.vectors[2])) /
                      (cell_b * cell_c)) * 180.0 / np.pi
    beta = np.arccos(np.dot(np.asarray(atomeye_config.vectors[0]),
                             np.asarray(atomeye_config.vectors[2])) /
                      (cell_a * cell_c)) * 180.0 / np.pi
    gamma = np.arccos(np.dot(np.asarray(atomeye_config.vectors[0]),
                             np.asarray(atomeye_config.vectors[1])) /
                      (cell_a * cell_b)) * 180.0 / np.pi

    volume = abs(atomeye_config.vectors[0][0] * atomeye_config.vectors[1][1] * 
                 atomeye_config.vectors[2][2] + atomeye_config.vectors[0][1] *
                 atomeye_config.vectors[1][2] * atomeye_config.vectors[2][0] +
                 atomeye_config.vectors[0][2] * atomeye_config.vectors[1][0] *
                 atomeye_config.vectors[2][1] - atomeye_config.vectors[0][2] *
                 atomeye_config.vectors[1][1] * atomeye_config.vectors[2][0] -
                 atomeye_config.vectors[0][1] * atomeye_config.vectors[1][0] *
                 atomeye_config.vectors[2][2] - atomeye_config.vectors[0][0] *
                 atomeye_config.vectors[1][2] * atomeye_config.vectors[2][1])

    num_rho = float(atomeye_config.atom_num) / volume

    for i in range(len(header)):
        if "Cell (Ang/deg):" in header[i]:
            header[i] = "Cell (Ang/deg):{0:11.6F}{1:11.6F}{2:11.6F}" \
                             "{3:11.6F}{4:11.6F}{5:11.6F}\n".\
                        format(cell_a, cell_b, cell_c, alpha, beta, gamma)
        if "Lattice vectors (Ang):" in header[i]:
            header[i + 1] = "{0:11.6F}{1:11.6F}{2:11.6F}\n".\
                format(atomeye_config.vectors[0][0],
                       atomeye_config.vectors[0][1],
                       atomeye_config.vectors[0][2])
            header[i + 2] = "{0:11.6F}{1:11.6F}{2:11.6F}\n". \
                format(atomeye_config.vectors[1][0],
                       atomeye_config.vectors[1][1],
                       atomeye_config.vectors[1][2])
            header[i + 3] = "{0:11.6F}{1:11.6F}{2:11.6F}\n". \
                format(atomeye_config.vectors[2][0],
                       atomeye_config.vectors[2][1],
                       atomeye_config.vectors[2][2])
        if "Number density (Ang^-3):" in header[i]:
            header[i] = "Number density (Ang^-3):{0:10.6F}\n".format(num_rho)

    rmc_out = open(atomeye_config.fileName.split(".cfg")[0] + ".rmc6f", "w")
    for item in header:
        rmc_out.write(item)
    for i in range(atomeye_config.atom_num):
        line_temp = ref_config.atomsLine[i]
        line = " ".join(line_temp.split()[0:3]) + \
               "{0:11.6F}".format(atomeye_config.atom_coords[i][0]) + \
               "{0:11.6F}".format(atomeye_config.atom_coords[i][1]) + \
               "{0:11.6F}".format(atomeye_config.atom_coords[i][2]) + \
               " " + " ".join(line_temp.split()[6:]) + "\n"
        rmc_out.write(line)
    rmc_out.close()
