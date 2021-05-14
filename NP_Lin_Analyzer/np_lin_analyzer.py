"""
Nanoparticle linear expansion analyzer
======================================

This python routine takes the initial and fitted nano RMC6F configuration as
inputs and will analyze the linear expansion of lattice in the fitted nano
configuration. The goal is to find a lattice that best matches the initial
one through linear expansion of the fitted lattice. Input from command line
will be needed during execution and the CLI prompt should be already self-explaining.

The linear fitted configuration will be stored in whatever file name specified in \
the very last step. The linear fitting information can be found in a file named \
'np_lin_analyzer.out'. Specially, the diagonal elements of the inverse Hessian \
matrix will give the uncertainty of the corresponding fitted variable.
"""

from scipy.optimize import minimize
import sys
import numpy as np
from numpy.linalg import inv


def main():

    # Minimizer function definition.
    def targ_func(x):
        targ_res = 0.0
        for key, item in xFit.items():
            term_1 = (x[0] + x[1] * xFit[key] - xStart[key])**2
            term_2 = (x[2] + x[3] * yFit[key] - yStart[key])**2
            term_3 = (x[4] + x[5] * zFit[key] - zStart[key])**2
            targ_res += (term_1 + term_2 + term_3)
        return targ_res

    version = "0.1"

    print("\n======================================================")
    print("================Welcome to NP analyzer!===============")
    print("=====================Version:", version, "====================")
    print("================Author: Yuanpeng Zhang================")
    print("=============Contact: zyroc1990@gmail.com=============")
    print("======================================================")

    prompt_temp = "\nPlease input number of particles " + \
                  "to analyze (0->multiple, 1->single): "
    numParToAnalyze = int(input(prompt_temp))

    if numParToAnalyze == 1:
        print("\nAnalyzing single particle...\n")
        prompt_temp = "Please input the initial RMC6F configuration STEM name: "
        initConfigFN = input(prompt_temp) + ".rmc6f"
        prompt_temp = "Please input the fitted RMC6F configuration STEM name: "
        fitConfigFN = input(prompt_temp) + ".rmc6f"

        vectors = []
        xStart = {}
        yStart = {}
        zStart = {}
        header = []
        numAtomLineFound = False

        # Read in initial RMC6F configuration.
        initConfigF = open(initConfigFN, "r")
        line = initConfigF.readline()
        header.append(line)
        while "Atoms" not in line:
            line = initConfigF.readline()
            header.append(line)
            if "Lattice vectors" in line:
                for i in range(3):
                    line = initConfigF.readline()
                    header.append(line)
                    vectors.append([float(x) for x in line.split()])
            if "Number of atoms" in line:
                natoms = int(line.split(":")[1])
                numAtomLineFound = True
        if not numAtomLineFound:
            print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!!!!Line containing total number of atoms not found!!!!")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            sys.exit()

        # For the purpose of coordination transformation between Cartesian and
        # crystallographic coordinate systems.
        vecArray = np.asarray(vectors)
        vecArrayInv = inv(vecArray)
        vecInv = vecArrayInv.tolist()

        for i in range(natoms):
            line = initConfigF.readline()
            xTemp = float(line.split()[3])
            yTemp = float(line.split()[4])
            zTemp = float(line.split()[5])

            startCryst = [xTemp, yTemp, zTemp]
            xTemp = sum(startCryst[ii] * vectors[ii][0] for ii in range(3))
            yTemp = sum(startCryst[ii] * vectors[ii][1] for ii in range(3))
            zTemp = sum(startCryst[ii] * vectors[ii][2] for ii in range(3))
            key_temp = line.rstrip().split()[6] + "-" + \
                line.rstrip().split()[7] + "-" + \
                line.rstrip().split()[8] + "-" + \
                line.rstrip().split()[9]
            xStart[key_temp] = xTemp
            yStart[key_temp] = yTemp
            zStart[key_temp] = zTemp

        initConfigF.close()

        sum_temp = 0
        for key, item in xStart.items():
            sum_temp += item
        xStartMean = sum_temp / float(natoms)
        sum_temp = 0
        for key, item in yStart.items():
            sum_temp += item
        yStartMean = sum_temp / float(natoms)
        sum_temp = 0
        for key, item in zStart.items():
            sum_temp += item
        zStartMean = sum_temp / float(natoms)

        for key, item in xStart.items():
            xStart[key] = item - xStartMean
        for key, item in yStart.items():
            yStart[key] = item - yStartMean
        for key, item in zStart.items():
            zStart[key] = item - zStartMean

        xFit = {}
        yFit = {}
        zFit = {}
        atomLines = {}

        # Read in fitted RMC6F configuration.
        fitConfigF = open(fitConfigFN, "r")
        line = fitConfigF.readline()
        while "Atoms" not in line:
            line = fitConfigF.readline()

        for i in range(natoms):
            line = fitConfigF.readline()
            xTemp = float(line.split()[3])
            yTemp = float(line.split()[4])
            zTemp = float(line.split()[5])

            startCryst = [xTemp, yTemp, zTemp]
            xTemp = sum(startCryst[ii] * vectors[ii][0] for ii in range(3))
            yTemp = sum(startCryst[ii] * vectors[ii][1] for ii in range(3))
            zTemp = sum(startCryst[ii] * vectors[ii][2] for ii in range(3))

            key_temp = line.rstrip().split()[6] + "-" + \
                line.rstrip().split()[7] + "-" + \
                line.rstrip().split()[8] + "-" + \
                line.rstrip().split()[9]
            xFit[key_temp] = xTemp
            yFit[key_temp] = yTemp
            zFit[key_temp] = zTemp
            atomLines[key_temp] = line

        fitConfigF.close()

        sum_temp = 0
        for key, item in xFit.items():
            sum_temp += item
        xFitMean = sum_temp / float(natoms)
        sum_temp = 0
        for key, item in yFit.items():
            sum_temp += item
        yFitMean = sum_temp / float(natoms)
        sum_temp = 0
        for key, item in zFit.items():
            sum_temp += item
        zFitMean = sum_temp / float(natoms)

        for key, item in xFit.items():
            xFit[key] = item - xFitMean
        for key, item in yFit.items():
            yFit[key] = item - yFitMean
        for key, item in zFit.items():
            zFit[key] = item - zFitMean

        print_out = "\nExecute linear fitting for the " + \
                    "final RMC6F against the initial..."
        print(print_out)

        res = minimize(targ_func, (1, 1, 1, 1, 1, 1), method='BFGS')

        print("\nDone with the linear fitting!")

        xFit2 = {}
        yFit2 = {}
        zFit2 = {}
        for key, item in xFit.items():
            xFit2[key] = res.x[0] + res.x[1] * xFit[key]
            yFit2[key] = res.x[2] + res.x[3] * yFit[key]
            zFit2[key] = res.x[4] + res.x[5] * zFit[key]

        xFitOut = {}
        yFitOut = {}
        zFitOut = {}
        for key, item in xFit.items():
            xFitOutCart = xFit2[key] + xFitMean
            yFitOutCart = yFit2[key] + yFitMean
            zFitOutCart = zFit2[key] + zFitMean

            outTemp = [xFitOutCart, yFitOutCart, zFitOutCart]
            # Transform back to RMC6F coordinate.
            xFitOut[key] = sum(outTemp[ii] * vecInv[ii][0] for ii in range(3))
            yFitOut[key] = sum(outTemp[ii] * vecInv[ii][1] for ii in range(3))
            zFitOut[key] = sum(outTemp[ii] * vecInv[ii][2] for ii in range(3))

        fitOutFN = input("\nPlease input output configuration STEM name: ")
        fitOutF = open(fitOutFN + ".rmc6f", "w")
        for item in header:
            fitOutF.write(item)
        for key, item in xFit.items():
            lineTemp = atomLines[key]
            lineNew = " ".join(lineTemp.split()[0:3]) + \
                      "{0:19.15F}{1:19.15F}{2:19.15F}".format(xFitOut[key],
                                                              yFitOut[key],
                                                              zFitOut[key]) + \
                      " " + " ".join(lineTemp.split()[6:]) + "\n"
            fitOutF.write(lineNew)
        fitOutF.close()

        logOut = open("np_lin_analyzer.out", "w")
        line_temp = "===============================================" + \
            "===========================================\n"
        logOut.write(line_temp)
        logOut.write("{0:>15s}{1:>15s}{2:>15s}{3:>15s}{4:>15s}{5:>15s}\n".
                     format("X_Shift", "X_Coeff", "Y_Shift",
                            "Y_Coeff", "Z_Shift", "Z_Coeff"))
        logOut.write(line_temp)
        logOut.write("{0:15.6E}{1:15.6E}{2:15.6E}{3:15.6E}{4:15.6E}{5:15.6E}\n".
                     format(res.x[0], res.x[1], res.x[2],
                            res.x[3], res.x[4], res.x[5]))
        logOut.write(line_temp)
        logOut.write("Hessian Matrix Inverse\n")
        logOut.write(line_temp)
        for i in range(6):
            for j in range(6):
                logOut.write("{0:15.6E}".format(res.hess_inv[i][j]))
            logOut.write("\n")
        logOut.write(line_temp)

        logOut.close()

    elif numParToAnalyze == 0:
        print("\nAnalyzing multiple particles...\n")
    else:
        print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!!!'0' and '1' are only acceptable inputs!!!!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        sys.exit()


if __name__ == '__main__':
    main()
