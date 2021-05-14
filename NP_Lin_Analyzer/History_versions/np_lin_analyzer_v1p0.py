from scipy.optimize import minimize
import sys
import numpy as np
from numpy.linalg import inv


# Minimizer function definition.
def targ_func(x):
    targ_res = 0.0
    for ii in range(natoms):
        targ_res += ((x[0] + x[1] * xFit[ii] - xStart[ii])**2 +
                     (x[2] + x[3] * yFit[ii] - yStart[ii])**2 +
                     (x[4] + x[5] * zFit[ii] - zStart[ii])**2)
    return targ_res


version = "1.0"

print("\n======================================================")
print("================Welcome to NP analyzer!===============")
print("=====================Version:", version, "====================")
print("================Author: Yuanpeng Zhang================")
print("=============Contact: zyroc1990@gmail.com=============")
print("======================================================")

numParToAnalyze = int(input("\nPlease input number of particles to analyze (0->multiple, 1->single): "))

if numParToAnalyze == 1:
    print("\nAnalyzing single particle...\n")
    initConfigFN = input("Please input the initial RMC6F configuration STEM name: ") + ".rmc6f"
    fitConfigFN = input("Please input the fitted RMC6F configuration STEM name: ") + ".rmc6f"

    vectors = []
    xStart = []
    yStart = []
    zStart = []
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
        xStart.append(xTemp)
        yStart.append(yTemp)
        zStart.append(zTemp)

    initConfigF.close()

    xStartMean = sum(xStart) / natoms
    yStartMean = sum(yStart) / natoms
    zStartMean = sum(zStart) / natoms

    xStart = [item - xStartMean for item in xStart]
    yStart = [item - yStartMean for item in yStart]
    zStart = [item - zStartMean for item in zStart]

    xFit = []
    yFit = []
    zFit = []
    atomLines = []

    # Read in fitted RMC6F configuration.
    fitConfigF = open(fitConfigFN, "r")
    line = fitConfigF.readline()
    while "Atoms" not in line:
        line = fitConfigF.readline()

    for i in range(natoms):
        line = fitConfigF.readline()
        atomLines.append(line)
        xTemp = float(line.split()[3])
        yTemp = float(line.split()[4])
        zTemp = float(line.split()[5])

        startCryst = [xTemp, yTemp, zTemp]
        xTemp = sum(startCryst[ii] * vectors[ii][0] for ii in range(3))
        yTemp = sum(startCryst[ii] * vectors[ii][1] for ii in range(3))
        zTemp = sum(startCryst[ii] * vectors[ii][2] for ii in range(3))
        xFit.append(xTemp)
        yFit.append(yTemp)
        zFit.append(zTemp)

    fitConfigF.close()

    xFitMean = sum(xFit) / natoms
    yFitMean = sum(yFit) / natoms
    zFitMean = sum(zFit) / natoms

    xFit = [item - xFitMean for item in xFit]
    yFit = [item - yFitMean for item in yFit]
    zFit = [item - zFitMean for item in zFit]

    print("\nExecute linear fitting for the final RMC6F against the initial...")

    res = minimize(targ_func, (1, 1, 1, 1, 1, 1), method='BFGS')

    print("\nDone with the linear fitting!")

    xFit2 = []
    yFit2 = []
    zFit2 = []
    for i in range(natoms):
        xFit2.append(res.x[0] + res.x[1] * xFit[i])
        yFit2.append(res.x[2] + res.x[3] * yFit[i])
        zFit2.append(res.x[4] + res.x[5] * zFit[i])

    xFitOut = []
    yFitOut = []
    zFitOut = []
    for i in range(natoms):
        xFitOutCart = xFit2[i] + xFitMean
        yFitOutCart = yFit2[i] + yFitMean
        zFitOutCart = zFit2[i] + zFitMean

        outTemp = [xFitOutCart, yFitOutCart, zFitOutCart]
        # Transform back to RMC6F coordinate.
        xFitOut.append(sum(outTemp[ii] * vecInv[ii][0] for ii in range(3)))
        yFitOut.append(sum(outTemp[ii] * vecInv[ii][1] for ii in range(3)))
        zFitOut.append(sum(outTemp[ii] * vecInv[ii][2] for ii in range(3)))

    fitOutFN = input("\nPlease input output configuration STEM name: ")
    fitOutF = open(fitOutFN + ".rmc6f", "w")
    for item in header:
        fitOutF.write(item)
    for i in range(natoms):
        lineTemp = atomLines[i]
        lineNew = " ".join(lineTemp.split()[0:3]) + \
                  "{0:10.7F}{1:10.7F}{2:10.7F}".format(xFitOut[i], yFitOut[i], zFitOut[i]) + \
                  " " + " ".join(lineTemp.split()[6:]) + "\n"
        fitOutF.write(lineNew)
    fitOutF.close()

    logOut = open("np_lin_analyzer.out", "w")
    logOut.write("==========================================================================================\n")
    logOut.write("{0:>15s}{1:>15s}{2:>15s}{3:>15s}{4:>15s}{5:>15s}\n".
                 format("X_Shift", "X_Coeff", "Y_Shift", "Y_Coeff", "Z_Shift", "Z_Coeff"))
    logOut.write("==========================================================================================\n")
    logOut.write("{0:15.6E}{1:15.6E}{2:15.6E}{3:15.6E}{4:15.6E}{5:15.6E}\n".
                 format(res.x[0], res.x[1], res.x[2], res.x[3], res.x[4], res.x[5]))
    logOut.write("==========================================================================================\n")
    logOut.write("Hessian Matrix Inverse\n")
    logOut.write("==========================================================================================\n")
    for i in range(6):
        for j in range(6):
            logOut.write("{0:15.6E}".format(res.hess_inv[i][j]))
        logOut.write("\n")
    logOut.write("==========================================================================================")

    logOut.close()

elif numParToAnalyze == 0:
    print("\nAnalyzing multiple particles...\n")
else:
    print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("!!!!'0' and '1' are only acceptable inputs!!!!")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    sys.exit()
