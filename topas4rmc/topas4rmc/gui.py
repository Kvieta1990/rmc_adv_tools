import wx
import wx.xrc
import sys
import subprocess as sp
import os
import glob
import copy
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d
import datetime
from threading import *

package_directory = os.path.dirname(os.path.abspath(__file__))

def shiftLbyn(arr, n=0):
    return arr[n::] + arr[:n:]

def shiftRbyn(arr, n=0):
    return arr[-n:] + arr[:-n]

def q_to_t(q_array,A,C,Z,t_array):
    for i in range(len(q_array)):
        t_array[i] = A*(2*np.pi/q_array[i])**2+C*(2*np.pi/q_array[i])+Z

def t_to_q(t_array,A,C,Z,q_array):
    for i in range(len(t_array)):
        q_array[i]=(4.0*A*np.pi)/(np.sqrt((C**2.0)+4.0*A*(t_array[i]-Z))-C)

# Define notification event for thread completion
EVT_RESULT_ID = wx.NewId()

def EVT_RESULT(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_RESULT_ID, func)

class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""
    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data

class cw_rm_thread(Thread):

    """Worker Thread Class."""
    def __init__(self, notify_window, i1, i2, i3, resMatDone,
                dataSectList, content, topasDirSpec, topasInpSpec,
                topasInpDir, topasExe):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self._notify_window = notify_window
        self._want_abort = 0
        
        self.i1 = i1
        self.i2 = i2
        self.i3 = i3
        self.resMatDone = resMatDone
        self.dataSectList = dataSectList
        self.content = content
        self.topasDirSpec = topasDirSpec
        self.topasInpSpec = topasInpSpec
        self.topasExe = topasExe
        self.topasInp = topasInp
        self.topasInpDir = topasInpDir
        self.stemName = stemName

        # This starts the thread running on creation, but you could
        # also make the GUI thread responsible for calling this
        self.start()

    def run(self):
        i1Val = self.i1.GetValue()
        i2Val = self.i2.GetValue()
        i3Val = self.i3.GetValue()
        self.resMatDone = False
        self.dataSectList = []
        self.content = []
        # Go ahead if all necessary input boxes are given values. Advanced features could
        # be added in the future, e.g. check input values are valid or not.
        if self.topasDirSpec and self.topasInpSpec and (len(i1Val)>0) and (len(i2Val)>0) \
          and (len(i3Val)>0):
            i1Val = float(i1Val)
            i2Val = float(i2Val)
            i3Val = float(i3Val)
            print("====================== Initial Topas running ======================")
            print("==================== Topas subprocess started =====================\n")
            sp.call([self.topasExe, self.topasInp])#, stdout=sp.DEVNULL, stderr=sp.STDOUT)
            print("==================== Topas subprocess ended ======================")
            print("============= Initial Topas running" +
                  " successfully executed =================\n")

            inpFileIn = open(self.topasInp, 'r')

            # Read the whole input file to a list.
            line = inpFileIn.readline()
            self.content.append(line)
            while line:
                line = inpFileIn.readline()
                if line:
                    self.content.append(line)
            inpFileIn.close()

            # Worry about 'iters' line. We want to force Topas to run 0 times.
            for i in range(len(self.content)):
                if "iters" in self.content[i]:
                    self.content[i] = "iters 0\n"
                    itersLineExist = True
                    break
                else:
                    itersLineExist = False

            if self._want_abort:
                wx.PostEvent(self._notify_window, ResultEvent(None))
                return

            if not itersLineExist:
                self.content.insert(2, "iters 0\n")

            for i in range(len(self.content)):
                if "x_calculation_step" in self.content[i]:
                    self.content[i] = "\tx_calculation_step 0.00001\n"

            for i in range(len(self.content)):
                if "Zero_Error(" in self.content[i]:
                    self.content[i] = "\tZero_Error(,0)\n"

            # Delete not defined block if "#ifdef" exists.
            defineLabels = []
            for i in range(len(self.content)):
                if self._want_abort:
                    wx.PostEvent(self._notify_window, ResultEvent(None))
                    return
                if "#define" in self.content[i] and "'" not in self.content[i]:
                    defineLabels.append(self.content[i].split()[1].strip())
            notdefinedB = []
            for i in range(len(self.content)):
                if self._want_abort:
                    wx.PostEvent(self._notify_window, ResultEvent(None))
                    return
                if "#ifdef" in self.content[i]:
                    labelT = self.content[i].split()[1].strip()
                    if labelT not in defineLabels:
                        notdefinedB.append(i)
            for i in range(len(notdefinedB)):
                if self._want_abort:
                    wx.PostEvent(self._notify_window, ResultEvent(None))
                    return
                line2Delete = notdefinedB[i]
                while True:
                    if self._want_abort:
                        wx.PostEvent(self._notify_window, ResultEvent(None))
                        return
                    if "#endif" not in self.content[line2Delete]:
                        self.content[line2Delete] = "\n"
                    else:
                        self.content[line2Delete] = "\n"
                        break
                    line2Delete += 1

            # Delete space group line if they exist. Therefore, this assumes a
            # successful Pawley refinement before running this program since we
            # need a list of hkl peaks but we don't want to update them during
            # running this program hence we delete all space group lines.
            self.content = [x for x in self.content if "space_group" not in x]

            # Grab all data sections.
            for i in range(len(self.content)):
                if self._want_abort:
                    wx.PostEvent(self._notify_window, ResultEvent(None))
                    return
                if "xdd" in self.content[i]:
                    self.dataSectList.append(data_sect(i))

            # Start and end line for each data section.
            for i in range(len(self.dataSectList)):
                if self._want_abort:
                    wx.PostEvent(self._notify_window, ResultEvent(None))
                    return
                if (i == (len(self.dataSectList) - 1)):
                    self.dataSectList[i].endP = len(self.content) - 1
                else:
                    self.dataSectList[i].endP = self.dataSectList[i + 1].startP - 1

                # Grab the number of the 'hkl_Is' line.
                self.dataSectList[i].hklIsPos = []
                for j in range(self.dataSectList[i].endP - self.dataSectList[i].startP + 1):
                    if self._want_abort:
                        wx.PostEvent(self._notify_window, ResultEvent(None))
                        return
                    if "hkl_Is" in self.content[self.dataSectList[i].startP + j]:
                        self.dataSectList[i].hklIsPos.append(self.dataSectList[i].startP + j)
                    if "#endif" in self.content[self.dataSectList[i].startP + j]:
                        self.dataSectList[i].endP = self.dataSectList[i].startP + j - 1
                        break
                    if "C_matrix_normalized" in self.content[self.dataSectList[i].startP + j]:
                        self.dataSectList[i].endP = self.dataSectList[i].startP + j - 1
                        break

                # Start and end line for each hkl block.
                self.dataSectList[i].hklSP = []
                self.dataSectList[i].hklEP = []
                for j in range(len(self.dataSectList[i].hklIsPos)):
                    if (j == (len(self.dataSectList[i].hklIsPos) - 1)):
                        for k in range(self.dataSectList[i].endP -
                                       self.dataSectList[i].hklIsPos[j] + 1):
                            if self._want_abort:
                                wx.PostEvent(self._notify_window, ResultEvent(None))
                                return
                            if "load hkl_m_d_th2 I" in self.content[
                                    self.dataSectList[i].hklIsPos[j] + k]:
                                tempIndex = self.dataSectList[i].hklIsPos[j] + k + 2
                                self.dataSectList[i].hklSP.append(tempIndex)
                                for l in range(self.dataSectList[i].endP - tempIndex + 1):
                                    if self._want_abort:
                                        wx.PostEvent(self._notify_window, ResultEvent(None))
                                        return
                                    if "}" in self.content[tempIndex + l]:
                                        self.dataSectList[i].hklEP.append(tempIndex + l - 1)
                                        break
                    else:
                        for k in range(self.dataSectList[i].hklIsPos[j + 1] -
                                       self.dataSectList[i].hklIsPos[j] + 1):
                            if "load hkl_m_d_th2 I" in self.content[
                                    self.dataSectList[i].hklIsPos[j] + k]:
                                tempIndex = self.dataSectList[i].hklIsPos[j] + k + 2
                                self.dataSectList[i].hklSP.append(tempIndex)
                                for l in range(self.dataSectList[i].hklIsPos[j + 1] -
                                               tempIndex + 1):
                                    if self._want_abort:
                                        wx.PostEvent(self._notify_window, ResultEvent(None))
                                        return
                                    if "}" in self.content[tempIndex + l]:
                                        self.dataSectList[i].hklEP.append(tempIndex + l - 1)
                                        break

            # Set the proper tempratory lambda. This is for the purpose of increasing the
            # Qmax to the requested upper limit of Q-space. In practice, the real Q-range
            # may be limited to a certain range. In that case, if we want to extract the
            # tabulated profiles beyond the real Q-limit, we want to extend the Q-range
            # artifially and use the peak profile parameters obtained from fitting the limited
            # Q-range to calculate the peak profiles beyond the Q-limit within Topas. It should
            # be pointed out that the experimental data now has already made no sense since the
            # changing of lambda has already changed the Q-space resolution completely. But that
            # does not matter since as the pre-step, we should have already got the peak profiles
            # parameters from the initial Pawley refinement.
            lamInit = []
            lamPos = []
            for i in range(len(self.dataSectList)):
                for j in range(self.dataSectList[i].startP, self.dataSectList[i].endP + 1):
                    if self._want_abort:
                        wx.PostEvent(self._notify_window, ResultEvent(None))
                        return
                    if "finish_X" in self.content[j]:
                        thetaMax = float(self.content[j].split()[1])
                    if "start_X" in self.content[j]:
                        atPos = self.content[j].find("start_X")
                        self.content[j] = self.content[j][:atPos] + "start_X 0\n"
                for j in range(self.dataSectList[i].startP, self.dataSectList[i].endP + 1):
                    if self._want_abort:
                        wx.PostEvent(self._notify_window, ResultEvent(None))
                        return
                    if ("la" in self.content[j]) and ("lo" in self.content[j]) and \
                      ("lh" in self.content[j]):
                        lamInit.append(float(self.content[j].split()[3]))
                        lamPos.append(j)
                        atPos = self.content[j].find("lo")
                        atPos1 = self.content[j].find("lh")
                        lamTemp = 4 * np.pi * np.sin(thetaMax * np.pi / 360.0) / i3Val
                        self.content[j] = self.content[j][:atPos] + "lo " + str(lamTemp) + " " \
                          + self.content[j][atPos1:]

            # Replace the original lattice with a tempratory cubic one for the
            # purpose of varying q continuously and easily.
            rmLinesNum = 0
            for i in range(len(self.dataSectList)):
                if self._want_abort:
                    wx.PostEvent(self._notify_window, ResultEvent(None))
                    return
                if (len(self.dataSectList[i].hklSP)==1):
                    del self.content[self.dataSectList[i].hklSP[0] - 2 -
                      rmLinesNum:self.dataSectList[i].endP - rmLinesNum + 1]
                    rmLinesNum += (self.dataSectList[i].endP - self.dataSectList[i].hklSP[0] + 3)
                else:
                    del self.content[self.dataSectList[i].hklSP[0] - 2 -
                      rmLinesNum:self.dataSectList[i].hklIsPos[1] - rmLinesNum]
                    rmLinesNum += (self.dataSectList[i].hklIsPos[1] - self.dataSectList[i].hklSP[0] + 2)
                if i > 0:
                    self.dataSectList[i].hklIsPos[0] -= rmLinesNum

            for i in range(len(self.dataSectList)):
                if self._want_abort:
                    wx.PostEvent(self._notify_window, ResultEvent(None))
                    return
                self.content.insert(self.dataSectList[i].hklIsPos[0] + 1, "space_group \"Fm-3m\"\n")
                self.content.insert(self.dataSectList[i].hklIsPos[0] + 2, "Cubic(1.0)\n")
                self.content.insert(self.dataSectList[i].hklIsPos[0] + 3, "scale 1.0\n")

            # After replacing the original peak list, we need a topas run to generate the
            # tempratory hkl list.
            preTempFile = open(os.path.join(self.topasInpDir, "temptemp.inp"),"w")
            for item in self.content:
                if self._want_abort:
                    wx.PostEvent(self._notify_window, ResultEvent(None))
                    return
                preTempFile.write(item)
            preTempFile.close()

            sp.call([self.topasExe, os.path.join(self.topasInpDir,
              "temptemp.inp")])#, stdout=sp.DEVNULL, stderr=sp.STDOUT)

            inpFileIn = open(os.path.join(self.topasInpDir, "temptemp.out"), 'r')

            self.content = []
            # Read the whole input file to a list.
            line = inpFileIn.readline()
            self.content.append(line)
            while line:
                if self._want_abort:
                    wx.PostEvent(self._notify_window, ResultEvent(None))
                    return
                line = inpFileIn.readline()
                if line:
                    self.content.append(line)
            inpFileIn.close()

            # Delete the report lines if they exist.
            self.content = [x for x in self.content if ("Out_X_Yobs" not in x) \
              and ("Out_X_Ycalc" not in x)]

            # Delete the scale_pks line if they exist.
            self.content = [x for x in self.content if "scale_pks" not in x]

            # Delete MVW line if they exist.
            self.content = [x for x in self.content if "MVW" not in x]

            # Insert 'MVW' line for all hkl_Is sections.
            hklIs_line = []
            hklIs_line_num = 0
            for i in range(len(self.content)):
                if self._want_abort:
                    wx.PostEvent(self._notify_window, ResultEvent(None))
                    return
                if "hkl_Is" in self.content[i]:
                    hklIs_line_num += 1
                    hklIs_line.append(i + hklIs_line_num)

            for item in hklIs_line:
                if self._want_abort:
                    wx.PostEvent(self._notify_window, ResultEvent(None))
                    return
                self.content.insert(item, "\t\tMVW(0,0,0)\n")

            # Insert new 'scale_pks' line for all xdd sections. For neutron CW data,
            # we have a default scaling. But the problem is the scaling diverges as
            # q approaches zero. So we want to get rid of such scaling. But current
            # way of doing this is too brutal since we get rid of the scaling everywhere
            # while in practice we may want to keep the scaling as q increases to large
            # values. However, the thing is we rarely have PDF beamlines with constant
            # wavelength neutron so we probably don't worry about this for the moment.
            # If necessary in the future, we may want to change this block accordingly.
            neutronD = False
            for item in self.content:
                if self._want_abort:
                    wx.PostEvent(self._notify_window, ResultEvent(None))
                    return
                if "neutron_data" in item:
                    neutronD = True
                    break
            if neutronD:
                scale_line = []
                scale_line_num = 0
                for i in range(len(self.content)):
                    if self._want_abort:
                        wx.PostEvent(self._notify_window, ResultEvent(None))
                        return
                    if "xdd" in self.content[i]:
                        self.content[i] = "xdd \".\\dataTemp" + str(scale_line_num) + ".xye\"\n"
                        scale_line_num += 1
                        scale_line.append(i + scale_line_num)

                for i in range(len(scale_line)):
                    if self._want_abort:
                        wx.PostEvent(self._notify_window, ResultEvent(None))
                        return
                    self.content.insert(scale_line[i], "\tscale_pks = (Sin(Th)^2 Cos(Th));\n")

            # Insert 'Out_Q_Ycalc' line for all hkl_Is sections.
            out_line = []
            out_line_num = 0
            for i in range(len(self.content)):
                if self._want_abort:
                    wx.PostEvent(self._notify_window, ResultEvent(None))
                    return
                if "xdd" in self.content[i]:
                    out_line_num += 1
                    out_line.append(i + out_line_num)

            for i in range(len(out_line)):
                if self._want_abort:
                    wx.PostEvent(self._notify_window, ResultEvent(None))
                    return
                self.content.insert(out_line[i], "\t" + \
                  "Out_Q_Ycalc(\"q_ycalc_resmat_cw" + str(i+1) + ".dat\")\n")

            self.content.append("\nmacro Out_Q_Ycalc(file)\n")
            self.content.append("{\n")
            self.content.append("xdd_out file load out_record out_fmt out_eqn\n")
            self.content.append("{\n")
            self.content.append("\"%11.6f \" = 4 Pi Sin(Pi X / 360) / Lam;\n")
            self.content.append("\"%11.6f\\n\" = Ycalc;\n")
            self.content.append("}\n")
            self.content.append("}")

            self.dataSectList = []
            # Grab all data sections.
            for i in range(len(self.content)):
                if self._want_abort:
                    wx.PostEvent(self._notify_window, ResultEvent(None))
                    return
                if ("xdd" in self.content[i]) and ("xdd_out" not in self.content[i]):
                    self.dataSectList.append(data_sect(i))

            # Start and end line for each data section.
            for i in range(len(self.dataSectList)):
                if self._want_abort:
                    wx.PostEvent(self._notify_window, ResultEvent(None))
                    return
                if (i == (len(self.dataSectList) - 1)):
                    self.dataSectList[i].endP = len(self.content) - 1
                else:
                    self.dataSectList[i].endP = self.dataSectList[i + 1].startP - 1

                # Grab the number of the 'hkl_Is' line.
                self.dataSectList[i].hklIsPos = []
                for j in range(self.dataSectList[i].endP - self.dataSectList[i].startP + 1):
                    if self._want_abort:
                        wx.PostEvent(self._notify_window, ResultEvent(None))
                        return
                    if "hkl_Is" in self.content[self.dataSectList[i].startP + j]:
                        self.dataSectList[i].hklIsPos.append(self.dataSectList[i].startP + j)
                    if "#endif" in self.content[self.dataSectList[i].startP + j]:
                        self.dataSectList[i].endP = self.dataSectList[i].startP + j - 1
                        break
                    if "C_matrix_normalized" in self.content[self.dataSectList[i].startP + j]:
                        self.dataSectList[i].endP = self.dataSectList[i].startP + j - 1
                        break

                # Start and end line for each hkl block.
                self.dataSectList[i].hklSP = []
                self.dataSectList[i].hklEP = []
                for j in range(len(self.dataSectList[i].hklIsPos)):
                    if (j == (len(self.dataSectList[i].hklIsPos) - 1)):
                        for k in range(self.dataSectList[i].endP -
                                       self.dataSectList[i].hklIsPos[j] + 1):
                            if self._want_abort:
                                wx.PostEvent(self._notify_window, ResultEvent(None))
                                return
                            if "load hkl_m_d_th2 I" in self.content[
                                    self.dataSectList[i].hklIsPos[j] + k]:
                                tempIndex = self.dataSectList[i].hklIsPos[j] + k + 2
                                self.dataSectList[i].hklSP.append(tempIndex)
                                for l in range(self.dataSectList[i].endP - tempIndex + 1):
                                    if self._want_abort:
                                        wx.PostEvent(self._notify_window, ResultEvent(None))
                                        return
                                    if "}" in self.content[tempIndex + l]:
                                        self.dataSectList[i].hklEP.append(tempIndex + l - 1)
                                        break
                    else:
                        for k in range(self.dataSectList[i].hklIsPos[j + 1] -
                                       self.dataSectList[i].hklIsPos[j] + 1):
                            if "load hkl_m_d_th2 I" in self.content[
                                    self.dataSectList[i].hklIsPos[j] + k]:
                                tempIndex = self.dataSectList[i].hklIsPos[j] + k + 2
                                self.dataSectList[i].hklSP.append(tempIndex)
                                for l in range(self.dataSectList[i].hklIsPos[j + 1] -
                                               tempIndex + 1):
                                    if self._want_abort:
                                        wx.PostEvent(self._notify_window, ResultEvent(None))
                                        return
                                    if "}" in self.content[tempIndex + l]:
                                        self.dataSectList[i].hklEP.append(tempIndex + l - 1)
                                        break

            # Set all hkl intensity to zero for extracting the background.
            lattPos = []
            lamTemp = []
            for i in range(len(self.dataSectList)):
                for j in range(self.dataSectList[i].startP, self.dataSectList[i].endP + 1):
                    if self._want_abort:
                        wx.PostEvent(self._notify_window, ResultEvent(None))
                        return
                    if "finish_X" in self.content[j]:
                        thetaMax = float(self.content[j].split()[1])
                    if "start_X" in self.content[j]:
                        atPos = self.content[j].find("start_X")
                        self.content[j] = self.content[j][:atPos] + "start_X 0\n"
                for j in range(self.dataSectList[i].startP, self.dataSectList[i].endP + 1):
                    if self._want_abort:
                        wx.PostEvent(self._notify_window, ResultEvent(None))
                        return
                    if ("la" in self.content[j]) and ("lo" in self.content[j]) and \
                      ("lh" in self.content[j]):
                        atPos = self.content[j].find("lo")
                        atPos1 = self.content[j].find("lh")
                        lamTemp.append(4 * np.pi * np.sin(thetaMax * np.pi / 360.0) / (2.2*i3Val))
                        self.content[j] = self.content[j][:atPos] + "lo " + str(lamTemp[i]) + " " \
                          + self.content[j][atPos1:]
                for j in range(len(self.dataSectList[i].hklIsPos)):
                    if j == 0:
                        for k in range(self.dataSectList[i].hklIsPos[j], self.dataSectList[i].endP + 1):
                            if "Cubic(" in self.content[k]:
                                lattPos.append(k)
                    for k in range(self.dataSectList[i].hklEP[j] - self.dataSectList[i].hklSP[j] + 1):
                        if self._want_abort:
                            wx.PostEvent(self._notify_window, ResultEvent(None))
                            return
                        atPos = self.content[self.dataSectList[i].hklSP[j] + k].find("@")
                        self.content[self.dataSectList[i].hklSP[j] + k] = \
                            self.content[self.dataSectList[i].hklSP[j] + k][:atPos] + " 0\n"

            # Generate dummy xye data, which will sit on the same q-grid with the
            # RMC q-space data. Without doing this, Topas will do and output the
            # calculation based on whatever Q-grid the real dataset sits on.
            qarray = np.arange(i1Val,2.2*i3Val,i2Val)
            for i in range(len(self.dataSectList)):
                dataTempFile = open(os.path.join(self.topasInpDir, \
                  "dataTemp" + str(i) + ".xye"), "w")
                for item in qarray:
                    if self._want_abort:
                        wx.PostEvent(self._notify_window, ResultEvent(None))
                        return
                    twoThetaTemp = np.arcsin(item * lamTemp[i] / (4 * np.pi)) * 2.0 * 180.0 / np.pi
                    dataTempFile.write("{0:11.3F}{1:11.3F}{2:11.3F}\n".format(twoThetaTemp, 500, 15))
                dataTempFile.close()

            bkgTempFile = open(os.path.join(self.topasInpDir, "bkg_extract_temp.inp"), "w")
            for item in self.content:
                bkgTempFile.write(item)
            bkgTempFile.close()
            sp.call([self.topasExe, os.path.join(self.topasInpDir, \
              "bkg_extract_temp.inp")])#, stdout=sp.DEVNULL, stderr=sp.STDOUT)
            bkgTempData = []
            for i in range(len(self.dataSectList)):
                bkgTempData.append([])
                bkgDataFile = open(os.path.join(self.topasInpDir, \
                  "q_ycalc_resmat_cw" + str(i+1) + ".dat"))
                line = bkgDataFile.readline()
                bkgValTemp = float(line.split()[1])
                bkgTempData[i].append(bkgValTemp)
                while line:
                    if self._want_abort:
                        wx.PostEvent(self._notify_window, ResultEvent(None))
                        return
                    line = bkgDataFile.readline()
                    if line:
                        bkgValTemp = float(line.split()[1])
                        bkgTempData[i].append(bkgValTemp)
                bkgDataFile.close()

            # Here when we extract the peak profiles, we divide them by the corresponding
            # multiplicity. However the peak profiles will be normalized anyway later.
            # Therefore whether or not dividing the intensity by the multiplicity does
            # not really matter that much.
            for i in range(len(self.dataSectList)):
                for j in range(len(self.dataSectList[i].hklIsPos)):
                    for k in range(self.dataSectList[i].hklEP[j] - self.dataSectList[i].hklSP[j] + 1):
                        if self._want_abort:
                            wx.PostEvent(self._notify_window, ResultEvent(None))
                            return
                        if (j == 0 and k == 0):
                            multi = float(self.content[self.dataSectList[i].hklSP[j] + k].split()[3])
                            atPos = len(self.content[self.dataSectList[i].hklSP[j] + k]) - 2
                            self.content[self.dataSectList[i].hklSP[j] + k] = \
                                self.content[self.dataSectList[i].hklSP[j] + k][:atPos] \
                                + str(1.0/multi) + "\n"
                        elif (j == 0):
                            self.content[self.dataSectList[i].hklSP[j] + k] = \
                              "'" + self.content[self.dataSectList[i].hklSP[j] + k]

            print("============== Proceed to generate resolution matrix ===================")
            print("================= Usually this will take tens of minutes =================")

            # Variables for calculating the progress.
            total = len(self.dataSectList) * int((i3Val+i2Val-i1Val)/i2Val+1)
            processed = 0
            # plt.ion()
            # fig = []
            # ax = []
            # The 'for' loop is here because of the old implementation required it. To avoid tedious
            # change to the codes, we just set the loop range to 1.
            for i in range(1):
                if self._want_abort:
                    wx.PostEvent(self._notify_window, ResultEvent(None))
                    return
                print("\n=================== Processing data section " + str(i+1) + " ====================")
                qarray = np.arange(i1Val,i3Val+i2Val,i2Val)
                # resMatData = np.zeros((len(qarray),len(qarray)))
                # fig.append(plt.figure())
                # fig[i].canvas.set_window_title("Data section-" + str(i + 1))
                # ax.append(fig[i].add_subplot(111))
                sumTemp = []
                for j in range(len(qarray)):
                    if self._want_abort:
                        wx.PostEvent(self._notify_window, ResultEvent(None))
                        return
                    aTemp = 2 * np.sqrt(3) * np.pi / qarray[j]
                    atPos = self.content[lattPos[i]].find("(")
                    self.content[lattPos[i]] = self.content[lattPos[i]][:atPos] + \
                      "(" + str(aTemp) + ")\n"
                    resFile = open(os.path.join(self.topasInpDir, "res_mat_prep_temp.inp"),"w")
                    for item in self.content:
                        if self._want_abort:
                            wx.PostEvent(self._notify_window, ResultEvent(None))
                            return
                        resFile.write(item)
                    resFile.close()
                    sp.call([self.topasExe, os.path.join(self.topasInpDir, \
                      "res_mat_prep_temp.inp")])#, stdout=sp.DEVNULL, stderr=sp.STDOUT)
                    yCalcTemp = []
                    qYFileTemp = open(os.path.join(self.topasInpDir, \
                      "q_ycalc_resmat_cw" + str(i+1) + ".dat"), "r")
                    line = qYFileTemp.readline()
                    yCalcTemp.append(float(line.split()[1]))
                    while line:
                        if self._want_abort:
                            wx.PostEvent(self._notify_window, ResultEvent(None))
                            return
                        line = qYFileTemp.readline()
                        if line:
                            yCalcTemp.append(float(line.split()[1]))
                    for k in range(len(yCalcTemp)):
                        if self._want_abort:
                            wx.PostEvent(self._notify_window, ResultEvent(None))
                            return
                        yCalcTemp[k] -= bkgTempData[i][k]
                    # leftTemp = []
                    # rightTemp = []
                    # if yCalcTemp[0] == 0:
                    #     for k in range(j):
                    #         leftTemp.append(yCalcTemp[k])
                    #         yCalcTemp[k] = 0
                    #     for k in range(len(yCalcTemp)-j-1):
                    #         rightTemp.append(yCalcTemp[j+k+1])
                    #         yCalcTemp[j+k+1] = 0
                    #     for k in range(j):
                    #         yCalcTemp[j-k-1] = rightTemp[k]
                    #         yCalcTemp[j+k+1] = leftTemp[-(k+1)]
                    # For normalization purpose.
                    sumTempTemp = 0
                    for k in range(len(qarray)):
                        if self._want_abort:
                            wx.PostEvent(self._notify_window, ResultEvent(None))
                            return
                        resMatData[j][k] = yCalcTemp[k]
                        sumTempTemp += resMatData[j][k]
                    sumTemp.append(sumTempTemp)
                    processed += 1
                    perct = float(processed) / float(total) * 100
                    if processed%(int(0.01*total)) == 0 or (processed==total):
                        print("================== Progress: {0:3.0F} % ==================".format(perct))
                    # ax[i].cla()
                    # ax[i].imshow(resMatData,cmap='BuGn')
                    # ax[i].set_title("Resolution matrix generation")
                    # ax[i].title.set_fontsize(15)
                    # ax[i].title.set_fontweight('bold')
                    # ax[i].xaxis.label.set_fontsize(17)
                    # ax[i].yaxis.label.set_fontweight('bold')
                    # ax[i].yaxis.label.set_fontsize(17)
                    # ax[i].xaxis.label.set_fontweight('bold')
                    # for itemitem in ax[i].get_xticklabels():
                    #     itemitem.set_fontsize(13)
                    # for itemitem in ax[i].get_yticklabels():
                    #     itemitem.set_fontsize(13)
                    # fig[i].canvas.flush_events()
                    # fig[i].canvas.draw()

                # Get rid of all zeros in the sparse matrix to reduce the output file size.
                resMatRed = []
                startPL = []
                endPL = []
                index = 0
                for item in resMatData:
                    resMatRed.append([x/sumTemp[index] for x in item if x != 0])
                    startPFound = False
                    endPFound = False
                    for k in range(len(item)):
                        if self._want_abort:
                            wx.PostEvent(self._notify_window, ResultEvent(None))
                            return
                        if item[k] != 0 and not startPFound:
                            startPFound = True
                            spTemp = k
                        if item[k] == 0 and startPFound:
                            endPFound = True
                            epTemp = k - 1
                            break
                    if startPFound and not endPFound:
                        epTemp = len(qarray) - 1
                    elif not startPFound and not endPFound:
                        spTemp = -1
                        epTemp = -1

                    if epTemp == -1:
                        startPL.append(0)
                        endPL.append(0)
                    else:
                        startPL.append(spTemp + 1)
                        endPL.append(epTemp + 1)

                    resMatRed[index].insert(0,startPL[index])
                    resMatRed[index].insert(1,endPL[index])
                    index += 1

                resMatFile = open(os.path.join(self.topasInpDir, "res_matrix.dat"), "w")
                resMatFile.write("{0:8d}\n".format(len(resMatRed)))
                for j in range(len(resMatRed)):
                    if self._want_abort:
                        wx.PostEvent(self._notify_window, ResultEvent(None))
                        return
                    resMatFile.write("{0:8d}{1:8d}".format(resMatRed[j][0], resMatRed[j][1]))
                    for k in range(2, len(resMatRed[j])):
                        resMatFile.write("{0:8.5F}".format(resMatRed[j][k]))
                    resMatFile.write("\n")
                resMatFile.close()

            print("============= Resolution matrix successfully generated ==================\n")
            self.resMatDone = True

            now = datetime.datetime.now()
            if not os.path.isfile(os.path.join(self.topasInpDir, "res_matrix.hist")):
                log_file = open(os.path.join(self.topasInpDir, "res_matrix.hist"), "w")
                log_file.write("=====================================================\n")
                log_file.write("History of resolution matrix generation.\n")
                log_file.write("=====================================================\n")
                log_file.write("\n")
                log_file.write("=====================================================\n")
                log_file.write("Time stamp: " + str(now)[:19] + "\n")
                log_file.write("=====================================================\n")
                log_file.write("Topas executable: " + self.topasExe + "\n")
                log_file.write("Topas working directory: " + self.topasInpDir + "\n")
                log_file.write("Topas input file: " + self.stemName + ".inp" + "\n")
                log_file.write("Input box-1: " + i1 + "\n")
                log_file.write("Input box-2: " + i2 + "\n")
                log_file.write("Input box-3: " + i3 + "\n")
                log_file.write("=====================================================")
            else:
                log_file = open(os.path.join(self.topasInpDir, "res_matrix.hist"), "w+")
                log_file.write("\n\n")
                log_file.write("=====================================================\n")
                log_file.write("Time stamp: " + str(now)[:19] + "\n")
                log_file.write("=====================================================\n")
                log_file.write("Topas executable: " + self.topasExe + "\n")
                log_file.write("Topas working directory: " + self.topasInpDir + "\n")
                log_file.write("Topas input file: " + self.stemName + ".inp" + "\n")
                log_file.write("Input box-1: " + i1 + "\n")
                log_file.write("Input box-2: " + i2 + "\n")
                log_file.write("Input box-3: " + i3 + "\n")
                log_file.write("=====================================================")
            
            log_file.close()

            # plt.ioff()
            # plt.show()
        else:
            wx.LogError('Specify the topas install dir, topas input file and q grid values first!!!')

    def abort(self):
        """abort worker thread."""
        # Method for use by main thread to signal an abort
        self._want_abort = 1

class profile_thread(Thread):

    """Worker Thread Class."""
    def __init__(self, notify_window, dmInput, profileOut, 
                dataSectList, content, contentBAK, contentTemp, 
                bkgDataF, topasDirSpec, topasInpSpec,
                refType, topasInpDir, stemName, topasExe):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self._notify_window = notify_window
        self._want_abort = 0
        
        self.dmInput = dmInput
        self.profileOut = profileOut
        self.dataSectList = dataSectList
        self.content = content
        self.contentBAK = contentBAK
        self.contentTemp = contentTemp
        self.bkgDataF = bkgDataF
        self.topasDirSpec = topasDirSpec
        self.topasInpSpec = topasInpSpec
        self.refType = refType
        self.topasInpDir = topasInpDir
        self.stemName = stemName
        self.topasExe = topasExe

        # This starts the thread running on creation, but you could
        # also make the GUI thread responsible for calling this
        self.start()

    def run(self):
        try:
            dmin = self.dmInput.GetValue()
            self.profileOut = False
            self.dataSectList = []
            self.content = []
            self.contentBAK = []
            self.contentTemp = []
            self.bkgDataF = []
            if self.topasDirSpec and self.topasInpSpec and \
              (not dmin.isspace()) and int(dmin.split(";")[0])!=1 or dmin.split(";")[0]!=2:
                self.profileOut = True

                self.refType = int(dmin.split(";")[0])
                gridFC = int(dmin.split(";")[2])
                dminTemp = dmin.split(";")[1].split(",")
                dmin = [float(x) for x in dminTemp]

                inpFileName = os.path.join(self.topasInpDir,
                                           self.stemName + ".inp")
                inpFileIn = open(inpFileName, 'r')

                # Read the whole input file to a list.
                self.content = []
                line = inpFileIn.readline()
                self.content.append(line)
                while line:
                    line = inpFileIn.readline()
                    if line:
                        self.content.append(line)
                inpFileIn.close()

                if self.refType==1:
                    # Worry about 'iters' line. We want to force Topas to run 0 times.
                    for i in range(len(self.content)):
                        if self._want_abort:
                            wx.PostEvent(self._notify_window, ResultEvent(None))
                            return
                        if "iters" in self.content[i]:
                            self.content[i] = "iters 0\n"
                            itersLineExist = True
                            break
                        else:
                            itersLineExist = False

                    if not itersLineExist:
                        self.content.insert(2, "iters 0\n")

                    for i in range(len(self.content)):
                        if self._want_abort:
                            wx.PostEvent(self._notify_window, ResultEvent(None))
                            return
                        if self.content[i].strip()=="str":
                            self.content[i] = "hkl_Is\n"
                        if "site" in self.content[i] and "x" in self.content[i] and \
                          "y" in self.content[i] and "z" in self.content[i]:
                            self.content[i] = "\n"

                    tempInpFN = os.path.join(self.topasInpDir,
                                               "temptemptemp" + ".inp")
                    tempInpFile = open(tempInpFN, "w")
                    for item in self.content:
                        if self._want_abort:
                            wx.PostEvent(self._notify_window, ResultEvent(None))
                            return
                        tempInpFile.write(item)
                    tempInpFile.close()

                    # Initial run for testing.
                    print("====================== Initial Topas running ======================")
                    print("==================== Topas subprocess started =====================\n")
                    sp.call([self.topasExe, tempInpFN])#, stdout=sp.DEVNULL, stderr=sp.STDOUT)
                    print("==================== Topas subprocess ended ======================")
                    print("============= Initial Topas running" +
                          " successfully executed =================\n")

                    tempOutFN = os.path.join(self.topasInpDir,
                                               "temptemptemp" + ".out")
                    tempOutFile = open(tempOutFN, "r")
                    self.content = []
                    line = tempOutFile.readline()
                    self.content.append(line)
                    while line:
                        if self._want_abort:
                            wx.PostEvent(self._notify_window, ResultEvent(None))
                            return
                        line = tempOutFile.readline()
                        if line:
                            self.content.append(line)
                    tempOutFile.close()

                # Determine the data type - constant wavelength or TOF.
                lambdaTT = []
                tofParas = []
                for item in self.content:
                    if self._want_abort:
                        wx.PostEvent(self._notify_window, ResultEvent(None))
                        return
                    if ("la" in item) and ("lo" in item) and ("lh" in item):
                        if "lam" in item and "ymin_on_ymax":
                            if ":" in item:
                                lambdaTT.append(float(item.split(":")[1].split()[0]))
                            else:
                                lambdaTT.append(float(item.split()[6].split("`")[0].split("_")[0]))
                        else:
                            if ":" in item:
                                lambdaTT.append(float(item.split(":")[1].split()[0]))
                            else:
                                lambdaTT.append(float(item.split()[3].split("`")[0].split("_")[0]))
                    if "TOF_x_axis_calibration" in item and "macro" not in item:
                        if "'" in item:
                            if item.lstrip().index("'") != 0:
                                tofParas.append([float(item.split(",")[1].split("_")[0].split("`")[0]),
                                    float(item.split(",")[3].split("_")[0].split("`")[0]),
                                    float(item.split(",")[5].split("_")[0].split("`")[0].split(")")[0])])
                        else:
                            tofParas.append([float(item.split(",")[1].split("_")[0].split("`")[0]),
                                float(item.split(",")[3].split("_")[0].split("`")[0]),
                                float(item.split(",")[5].split("_")[0].split("`")[0].split(")")[0])])

                if len(lambdaTT) > 0:
                    xrayData = True
                else:
                    xrayData = False
                if len(tofParas) > 0:
                    tofData = True
                else:
                    tofData = False

                if self._want_abort:
                    wx.PostEvent(self._notify_window, ResultEvent(None))
                    return

                if xrayData:
                    xraySecNum = 0
                    for i in range(len(self.content)):
                        if self._want_abort:
                            wx.PostEvent(self._notify_window, ResultEvent(None))
                            return
                        if ("finish_X" in self.content[i]) and \
                          ("," not in self.content[i]) and (self.content[i].lstrip()[0] != "'") and \
                          ("(" not in self.content[i]) and (")" not in self.content[i]):
                            xraySecNum += 1
                    if (xraySecNum < len(dmin)):
                        wx.LogWarning(str(xraySecNum) + ' "finish_X" keywords found. ' + \
                            str(len(dmin)) + ' minimum d-spacing values given.\nTailing values will be ignored.')
                    elif (xraySecNum > len(dmin)):
                        wx.LogWarning(str(xraySecNum) + ' data sections found. ' + \
                            str(len(dmin)) + ' minimum d-spacing values given.+ "\n" + The default minimum d-spacing 0.5 will be used for the rest.')
                        for i in range(xraySecNum-len(dmin)):
                            dmin.append(0.5)

                if tofData:
                    tofSecNum = 0
                    for i in range(len(self.content)):
                        if self._want_abort:
                            wx.PostEvent(self._notify_window, ResultEvent(None))
                            return
                        if ("start_X" in self.content[i]) and ("," not in self.content[i]) \
                          and (self.content[i].lstrip()[0] != "'") and \
                          ("(" not in self.content[i]) and (")" not in self.content[i]):
                            tofSecNum += 1
                    if (tofSecNum < len(dmin)):
                        wx.LogWarning(str(tofSecNum) + ' "start_X" keywords found. ' + \
                            str(len(dmin)) + 'minimum d-spacing values given.\nTailing values will be ignored.')
                    elif (tofSecNum > len(dmin)):
                        wx.LogWarning(str(tofSecNum) + ' data sections found. ' + \
                            str(len(dmin)) + ' minimum d-spacing values given.\nThe default minimum d-spacing 0.5 will be used for the rest.')
                        for i in range(tofSecNum-len(dmin)):
                            dmin.append(0.5)

                # Codes below was for the purpose of keeping consistence
                # between input dmin and that used in Topas refinement.
                # This turns out to be unnecessary. But we keep the codes 
                # here just in case needed in the future.
                if xrayData:
                    xraySecNum = 0
                    fXSuggest = []
                    for i in range(len(self.content)):
                        if ("finish_X" in self.content[i]) and \
                          ("," not in self.content[i]) and (self.content[i].lstrip()[0] != "'") and \
                          ("(" not in self.content[i]) and (")" not in self.content[i]):
                            fXInit = float(self.content[i].split()[1])
                            tempVal = min(lambdaTT[xraySecNum] / (2*float(dmin[xraySecNum])),1.0)
                            fXTemp = np.arcsin(tempVal) * 360 / np.pi
                            fXSuggest.append(min(fXTemp, fXInit))
                            xraySecNum += 1
                if tofData:
                    tofSecNum = 0
                    sXSuggest = []
                    for i in range(len(self.content)):
                        if ("start_X" in self.content[i]) and ("," not in self.content[i]) \
                          and (self.content[i].lstrip()[0] != "'") and \
                          ("(" not in self.content[i]) and (")" not in self.content[i]):
                            sXInit = float(self.content[i].split()[1])
                            sXTemp = tofParas[tofSecNum][2] * (float(dmin[tofSecNum]))**2 + \
                                     tofParas[tofSecNum][1] * float(dmin[tofSecNum]) + \
                                     tofParas[tofSecNum][0]
                            sXSuggest.append(max(sXTemp, sXInit))
                            tofSecNum += 1

                if self._want_abort:
                    wx.PostEvent(self._notify_window, ResultEvent(None))
                    return

                # Worry about 'iters' line. We want to force Topas to run 0 times.
                for i in range(len(self.content)):
                    if self._want_abort:
                        wx.PostEvent(self._notify_window, ResultEvent(None))
                        return
                    if "iters" in self.content[i]:
                        self.content[i] = "iters 0\n"
                        itersLineExist = True
                        break
                    else:
                        itersLineExist = False

                if not itersLineExist:
                    self.content.insert(2, "iters 0\n")

                if self._want_abort:
                    wx.PostEvent(self._notify_window, ResultEvent(None))
                    return

                # Delete not defined block if "#ifdef" exists.
                defineLabels = []
                for i in range(len(self.content)):
                    if self._want_abort:
                        wx.PostEvent(self._notify_window, ResultEvent(None))
                        return
                    if "#define" in self.content[i] and "'" not in self.content[i]:
                        defineLabels.append(self.content[i].split()[1].strip())
                notdefinedB = []
                for i in range(len(self.content)):
                    if self._want_abort:
                        wx.PostEvent(self._notify_window, ResultEvent(None))
                        return
                    if "#ifdef" in self.content[i]:
                        labelT = self.content[i].split()[1].strip()
                        if labelT not in defineLabels:
                            notdefinedB.append(i)
                for i in range(len(notdefinedB)):
                    if self._want_abort:
                        wx.PostEvent(self._notify_window, ResultEvent(None))
                        return
                    line2Delete = notdefinedB[i]
                    while True:
                        if "#endif" not in self.content[line2Delete]:
                            self.content[line2Delete] = "\n"
                        else:
                            self.content[line2Delete] = "\n"
                            break
                        line2Delete += 1

                # Delete the report lines if they exist.
                self.content = [x for x in self.content if ("Out_X_Yobs" not in x) \
                  and ("Out_X_Ycalc" not in x)]

                self.content.append("\nmacro Out_X_Ycalc_Fine(file)\n")
                self.content.append("{\n")
                self.content.append("xdd_out file load out_record out_fmt out_eqn\n")
                self.content.append("{\n")
                self.content.append("\"%11.6f \" = X;\n")
                self.content.append("\"%18.12f\\n\" = Ycalc;\n")
                self.content.append("}\n")
                self.content.append("}")

                self.content.append("\nmacro Out_X_Yobs_Fine(file)\n")
                self.content.append("{\n")
                self.content.append("xdd_out file load out_record out_fmt out_eqn\n")
                self.content.append("{\n")
                self.content.append("\"%11.6f \" = X;\n")
                self.content.append("\"%18.12f\\n\" = Yobs;\n")
                self.content.append("}\n")
                self.content.append("}")

                # Delete MVW line if they exist.
                # This is for the purpose of outputing cell volume later.
                self.content = [x for x in self.content if "MVW" not in x]

                # Insert 'MVW' line for all hkl_Is sections.
                hklIs_line = []
                hklIs_line_num = 0
                for i in range(len(self.content)):
                    if self._want_abort:
                        wx.PostEvent(self._notify_window, ResultEvent(None))
                        return
                    if "hkl_Is" in self.content[i]:
                        hklIs_line_num += 1
                        hklIs_line.append(i + hklIs_line_num)

                for item in hklIs_line:
                    if self._want_abort:
                        wx.PostEvent(self._notify_window, ResultEvent(None))
                        return
                    self.content.insert(item, "\t\tMVW(0,0,0)\n")

                # Grab all data sections.
                for i in range(len(self.content)):
                    if self._want_abort:
                        wx.PostEvent(self._notify_window, ResultEvent(None))
                        return
                    if ("xdd" in self.content[i]) and ("xdds" not in self.content[i]) \
                        and ("xdd_" not in self.content[i]):
                        self.dataSectList.append(data_sect(i))

                # Start and end line for each data section.
                for i in range(len(self.dataSectList)):
                    if self._want_abort:
                        wx.PostEvent(self._notify_window, ResultEvent(None))
                        return
                    if (i == (len(self.dataSectList) - 1)):
                        self.dataSectList[i].endP = len(self.content) - 1
                    else:
                        self.dataSectList[i].endP = self.dataSectList[i + 1].startP - 1

                    # Grab the number of the 'hkl_Is' line.
                    self.dataSectList[i].hklIsPos = []
                    for j in range(self.dataSectList[i].endP - self.dataSectList[i].startP + 1):
                        if self._want_abort:
                            wx.PostEvent(self._notify_window, ResultEvent(None))
                            return
                        if "hkl_Is" in self.content[self.dataSectList[i].startP + j]:
                            self.dataSectList[i].hklIsPos.append(self.dataSectList[i].startP + j)
                        if "#endif" in self.content[self.dataSectList[i].startP + j]:
                            self.dataSectList[i].endP = self.dataSectList[i].startP + j - 1
                            break
                        if "C_matrix_normalized" in self.content[self.dataSectList[i].startP + j]:
                            self.dataSectList[i].endP = self.dataSectList[i].startP + j - 1
                            break

                    # Start and end line for each hkl block.
                    self.dataSectList[i].hklSP = []
                    self.dataSectList[i].hklEP = []
                    for j in range(len(self.dataSectList[i].hklIsPos)):
                        if self._want_abort:
                            wx.PostEvent(self._notify_window, ResultEvent(None))
                            return
                        if (j == (len(self.dataSectList[i].hklIsPos) - 1)):
                            for k in range(self.dataSectList[i].endP -
                                           self.dataSectList[i].hklIsPos[j] + 1):
                                if self._want_abort:
                                    wx.PostEvent(self._notify_window, ResultEvent(None))
                                    return
                                if "load hkl_m_d_th2 I" in self.content[
                                        self.dataSectList[i].hklIsPos[j] + k]:
                                    tempIndex = self.dataSectList[i].hklIsPos[j] + k + 2
                                    self.dataSectList[i].hklSP.append(tempIndex)
                                    for l in range(self.dataSectList[i].endP - tempIndex + 1):
                                        if "}" in self.content[tempIndex + l]:
                                            self.dataSectList[i].hklEP.append(tempIndex + l - 1)
                                            break
                        else:
                            for k in range(self.dataSectList[i].hklIsPos[j + 1] -
                                           self.dataSectList[i].hklIsPos[j] + 1):
                                if self._want_abort:
                                    wx.PostEvent(self._notify_window, ResultEvent(None))
                                    return
                                if "load hkl_m_d_th2 I" in self.content[
                                        self.dataSectList[i].hklIsPos[j] + k]:
                                    tempIndex = self.dataSectList[i].hklIsPos[j] + k + 2
                                    self.dataSectList[i].hklSP.append(tempIndex)
                                    for l in range(self.dataSectList[i].hklIsPos[j + 1] -
                                                   tempIndex + 1):
                                        if "}" in self.content[tempIndex + l]:
                                            self.dataSectList[i].hklEP.append(tempIndex + l - 1)
                                            break

                # Backup the original self.content list.
                self.contentBAK = []
                for item in self.content:
                    if self._want_abort:
                        wx.PostEvent(self._notify_window, ResultEvent(None))
                        return
                    self.contentBAK.append(item)

                # Prepare for initial run.
                self.contentTemp = []
                for item in self.content:
                    if self._want_abort:
                        wx.PostEvent(self._notify_window, ResultEvent(None))
                        return
                    self.contentTemp.append(item)
                insertLines = 0
                for i in range(len(self.dataSectList)):
                    if self._want_abort:
                        wx.PostEvent(self._notify_window, ResultEvent(None))
                        return
                    if gridFC==0:
                        self.contentTemp.insert(self.dataSectList[i].startP + 1 +
                                                insertLines, "\tOut_X_Ycalc(\"x_ycheck" + "_" +
                                                str(i + 1) + ".dat\")\n")
                    else:
                        self.contentTemp.insert(self.dataSectList[i].startP + 1 +
                                                insertLines, "\tOut_X_Ycalc_Fine(\"x_ycheck" + "_" +
                                                str(i + 1) + ".dat\")\n")
                    insertLines += 1
                    if gridFC==0:
                        self.contentTemp.insert(self.dataSectList[i].startP + 2 +
                                                insertLines, "\tOut_X_Yobs(\"" + self.stemName +
                                                ".bragg" + str(i + 1) + "\")\n")
                    else:
                        self.contentTemp.insert(self.dataSectList[i].startP + 2 +
                                                insertLines, "\tOut_X_Yobs_Fine(\"" + self.stemName +
                                                ".bragg" + str(i + 1) + "\")\n")
                    insertLines += 1

                inpFileTemp = open(os.path.join(self.topasInpDir, "init_check.inp"), "w")
                for item in self.contentTemp:
                    if self._want_abort:
                        wx.PostEvent(self._notify_window, ResultEvent(None))
                        return
                    inpFileTemp.write(item)
                inpFileTemp.close()

                print("======== Information successfully extracted " +
                      "from the Topas input file ===========\n")
                print("# of data sections ->", len(self.dataSectList), "\n")
                for i in range(len(self.dataSectList)):
                    if self._want_abort:
                        wx.PostEvent(self._notify_window, ResultEvent(None))
                        return
                    if i > 0:
                        print("")
                    print("Data section", str(i + 1) + ":")
                    print("\t# of Pawley/Rietveld sections ->", len(self.dataSectList[i].hklIsPos))
                    for j in range(len(self.dataSectList[i].hklIsPos)):
                        if self._want_abort:
                            wx.PostEvent(self._notify_window, ResultEvent(None))
                            return
                        numhkls = self.dataSectList[i].hklEP[j] - self.dataSectList[i].hklSP[j] + 1
                        print("\t# of hkls for Pawley/Rietveld section", str(j + 1) + " -> " + str(numhkls))
                print("\n======== Information successfully extracted " +
                      "from the Topas input file ===========\n")

                print("===================== Initial Topas running =======================")
                print("=================== Topas subprocess started ======================\n")
                sp.call([self.topasExe, os.path.join(self.topasInpDir, "init_check.inp")])#,
                        #stdout=sp.DEVNULL, stderr=sp.STDOUT)
                print("\n==================== Topas subprocess ended ======================")
                print("=============== Initial Topas running " +
                      "successfully executed ===============\n")

                # Extract the cell volume for output purpose later.
                volReadFile = open(os.path.join(self.topasInpDir, "init_check.out"),"r")
                cellVol = []
                line = volReadFile.readline()
                while line:
                    if self._want_abort:
                        wx.PostEvent(self._notify_window, ResultEvent(None))
                        return
                    line = volReadFile.readline()
                    if line and ("MVW" in line):
                        cellVol.append(float(line.split(',')[1].split(',')[0].split('`')[0]))
                volReadFile.close()

                # Set all hkls to 0 for extracting the background.
                # Here we also check the minimum d-spacing is set properly.
                notOK = False
                for i in range(len(self.dataSectList)):
                    for j in range(len(self.dataSectList[i].hklIsPos)):
                        for k in range(self.dataSectList[i].hklEP[j] -
                                       self.dataSectList[i].hklSP[j] + 1):
                            if self._want_abort:
                                wx.PostEvent(self._notify_window, ResultEvent(None))
                                return
                            atPos = self.content[self.dataSectList[i].hklSP[j] + k].find("@")
                            self.content[self.dataSectList[i].hklSP[j] + k] = \
                                self.content[self.dataSectList[i].hklSP[j] + k][:atPos] + " 0\n"

                # Previously, the 'notOK' flag was set to gurantee the consistence 
                # between the input dmin and that in topas refinement. However, it
                # turns out that such a check is not necessary. We just go with 
                # whichever is larger.
                if not notOK:
                    # Prepare for extracting the background.
                    self.contentTemp = []
                    for item in self.content:
                        if self._want_abort:
                            wx.PostEvent(self._notify_window, ResultEvent(None))
                            return
                        self.contentTemp.append(item)
                    insertLines = 0
                    for i in range(len(self.dataSectList)):
                        if self._want_abort:
                            wx.PostEvent(self._notify_window, ResultEvent(None))
                            return
                        if gridFC==0:
                            self.contentTemp.insert(self.dataSectList[i].startP + 1 +
                                                    insertLines, "\tOut_X_Ycalc(\"x_ybkg" +
                                                    "_" + str(i + 1) + ".dat\")\n")
                        else:
                            self.contentTemp.insert(self.dataSectList[i].startP + 1 +
                                                    insertLines, "\tOut_X_Ycalc_Fine(\"x_ybkg" +
                                                    "_" + str(i + 1) + ".dat\")\n")
                        insertLines += 1

                    inpFileTemp = open(os.path.join(self.topasInpDir, "bkg_extract.inp"), "w")
                    for item in self.contentTemp:
                        if self._want_abort:
                            wx.PostEvent(self._notify_window, ResultEvent(None))
                            return
                        inpFileTemp.write(item)
                    inpFileTemp.close()

                    # Extracting the background.
                    print("====================== Extract background =======================")
                    print("==================== Topas subprocess started =====================\n")
                    sp.call([self.topasExe, os.path.join(self.topasInpDir, "bkg_extract.inp")])#,
                            #stdout=sp.DEVNULL, stderr=sp.STDOUT)
                    print("\n==================== Topas subprocess ended ======================")
                    print("================= Background successfully executed ===================\n")

                    # Grab the background data.
                    bkgData = []
                    for i in range(len(self.dataSectList)):
                        if self._want_abort:
                            wx.PostEvent(self._notify_window, ResultEvent(None))
                            return
                        bkgData.append([])
                        bkgFile = open(os.path.join(self.topasInpDir, "x_ybkg" +
                                                    "_" + str(i + 1) + ".dat"), "r")
                        line = bkgFile.readline()
                        bkgData[i].append(line.split())
                        while line:
                            if self._want_abort:
                                wx.PostEvent(self._notify_window, ResultEvent(None))
                                return
                            line = bkgFile.readline()
                            if line:
                                bkgData[i].append(line.split())
                        bkgFile.close()
                        os.remove(os.path.join(self.topasInpDir, "x_ybkg" + "_" + str(i + 1) + ".dat"))
                    self.bkgDataF = [[[float(z) for z in y] for y in x] for x in bkgData]

                    print("============ Now proceed to prepare for " +
                          "writing out profile of hkl ============\n")

                    # This is for writing out a .hkl file which will be needed
                    # by RMCProfile while fitting the Bragg data.
                    # The hkl limit is set to 30 by default. Change this if needed.
                    hmax = 30
                    kmax = 30
                    lmax = 30
                    hstep = 1.0
                    kstep = 1.0
                    lstep = 1.0
                    hklFile = open(os.path.join(self.topasInpDir, self.stemName+".hkl"),"w")
                    hklFile.write("{0:4.2F}\n".format(dmin[0]))
                    hklFile.write("{0:5d}{1:5d}{2:7.2F}\n".format(-hmax,hmax,hstep))
                    hklFile.write("{0:5d}{1:5d}{2:7.2F}\n".format(-hmax,hmax,hstep))
                    hklFile.write("{0:5d}{1:5d}{2:7.2F}\n".format(-hmax,hmax,hstep))
                    hklFile.close()

                    numDataSec = len(self.dataSectList)
                    prcocessed = 0

                    scale = []
                    for i in range(numDataSec):
                        if self._want_abort:
                            wx.PostEvent(self._notify_window, ResultEvent(None))
                            return
                        print("\n  Processing data block request " + str(i + 1) + " ...")
                        dataSecI = i
                        scale.append([])

                        # Write out the background of each data section to separate files.
                        bkgFileOut = open(os.path.join(self.topasInpDir,
                                                       self.stemName + ".back" + str(i + 1)), "w")
                        for item in self.bkgDataF[dataSecI]:
                            if self._want_abort:
                                wx.PostEvent(self._notify_window, ResultEvent(None))
                                return
                            bkgFileOut.write("{0:15.6F}{1:15.6F}\n".format(item[0], item[1]))
                        bkgFileOut.close()
                        hklFileOut = open(os.path.join(self.topasInpDir,
                                                       self.stemName + "_check_hkl_temp" + str(i + 1)), "w")
                        hklFileOut.write("Dmin = " + str(dmin[i]) + "\n")

                        numPawleySec = len(self.dataSectList[dataSecI].hklIsPos)

                        for j in range(numPawleySec):
                            if self._want_abort:
                                wx.PostEvent(self._notify_window, ResultEvent(None))
                                return
                            prcocessed += 1
                            print("\n    Processing Pawley/Rietveld section request " + str(j + 1) + " ...")
                            hklFileOut.write("Phase-" + str(j + 1) + "\n")
                            hklFileOut.write("Cell Vol = " + str(cellVol[prcocessed - 1]) + "\n")
                            PawleySecI = j

                            # Grabbing scale information. But this is only for potential use
                            # in the future. The Pawley scale will not be read in by RMCProfile. We
                            # do need the scale factor from Rietveld refinement.
                            inpFileOut = []
                            for item in self.content:
                                if self._want_abort:
                                    wx.PostEvent(self._notify_window, ResultEvent(None))
                                    return
                                inpFileOut.append(item)
                            scaleFound = False
                            if PawleySecI == len(self.dataSectList[dataSecI].hklIsPos) - 1:
                                for k in range(self.dataSectList[dataSecI].endP -
                                               self.dataSectList[dataSecI].hklIsPos[PawleySecI] + 1):
                                    if self._want_abort:
                                        wx.PostEvent(self._notify_window, ResultEvent(None))
                                        return
                                    strTemp = inpFileOut[self.dataSectList[
                                        dataSecI].hklSP[PawleySecI] + k]
                                    if ("scale" in strTemp) and (strTemp.lstrip()[0] != "'"):
                                        if "@" in strTemp:
                                            scale[i].append(float(strTemp.split()[2].split('`')[0].split('_')[0]))
                                            scaleFound = True
                                            break
                                        else:
                                            if (strTemp.split()[1].split('`')[0].split('_')[0].replace('.','',1).isdigit()):
                                                scale[i].append(float(strTemp.split()[1].split('`')[0].split('_')[0]))
                                                scaleFound = True
                                                break
                                            else:
                                                scale[i].append(float(strTemp.split()[2].split('`')[0].split('_')[0]))
                                                scaleFound = True
                                                break
                            else:
                                for k in range(self.dataSectList[dataSecI].hklIsPos[PawleySecI + 1] -
                                               self.dataSectList[dataSecI].hklIsPos[PawleySecI]):
                                    if self._want_abort:
                                        wx.PostEvent(self._notify_window, ResultEvent(None))
                                        return
                                    strTemp = inpFileOut[self.dataSectList[
                                        dataSecI].hklSP[PawleySecI] + k]
                                    if ("scale" in strTemp) and (strTemp.lstrip()[0] != "'"):
                                        if "@" in strTemp:
                                            scale[i].append(float(strTemp.split()[2].split('`')[0]))
                                            scaleFound = True
                                            break
                                        else:
                                            if (strTemp.split()[1].replace('.','',1).isdigit()):
                                                scale[i].append(float(strTemp.split()[1].split('`')[0]))
                                                scaleFound = True
                                                break
                                            else:
                                                scale[i].append(float(strTemp.split()[2].split('`')[0]))
                                                scaleFound = True
                                                break
                            if not scaleFound:
                                scale[i].append(1.0)

                            hklFileOut.write("Scale = " + str(scale[i][j]) + "\n")
                            hklFileOut.write("# of hkl = " + str(
                                self.dataSectList[dataSecI].hklEP[PawleySecI] -
                                self.dataSectList[dataSecI].hklSP[PawleySecI] + 1) + "\n")
                            hklFileOut.write(
                                "h\tk\tl\tMultiplicity\td-spacing\t" +
                                "Start_Point\tEnd_Point\thkl_Profile->\n")

                            for k in range(self.dataSectList[dataSecI].hklEP[PawleySecI] -
                                           self.dataSectList[dataSecI].hklSP[PawleySecI] + 1):
                                if self._want_abort:
                                    wx.PostEvent(self._notify_window, ResultEvent(None))
                                    return
                                # Previously when we did the background extraction, we set all
                                # intensity to zero. Now we want to change the intensity to 1 for each
                                # of the hkls one by one for extracting the profile corresponding to
                                # each hkl peak.
                                zeroPos = len(
                                    inpFileOut[self.dataSectList[dataSecI].hklSP[PawleySecI] + k]) - 2
                                inpFileOut[self.dataSectList[dataSecI].hklSP[PawleySecI] + k] = \
                                    inpFileOut[self.dataSectList[dataSecI].hklSP[PawleySecI] +
                                               k][:zeroPos] + " 1\n"

                                if gridFC==0:
                                    inpFileOut.insert(self.dataSectList[dataSecI].startP + 1,
                                                      "\tOut_X_Ycalc(\"x_ycalc.dat\")\n")
                                else:
                                    inpFileOut.insert(self.dataSectList[dataSecI].startP + 1,
                                                      "\tOut_X_Ycalc_Fine(\"x_ycalc.dat\")\n")

                                inpFileOutW = open(os.path.join(self.topasInpDir, "hkls_temp.inp"), "w")
                                for item in inpFileOut:
                                    if self._want_abort:
                                        wx.PostEvent(self._notify_window, ResultEvent(None))
                                        return
                                    inpFileOutW.write(item)
                                inpFileOutW.close()
                                sp.call([self.topasExe, os.path.join(self.topasInpDir,
                                                                     "hkls_temp.inp")])#,
                                        #stdout=sp.DEVNULL, stderr=sp.STDOUT)

                                inpFileOut = []
                                for item in self.content:
                                    if self._want_abort:
                                        wx.PostEvent(self._notify_window, ResultEvent(None))
                                        return
                                    inpFileOut.append(item)

                                hTemp = int(
                                    inpFileOut[self.dataSectList[dataSecI].hklSP[PawleySecI] +
                                               k].split()[0])
                                kTemp = int(
                                    inpFileOut[self.dataSectList[dataSecI].hklSP[PawleySecI] +
                                               k].split()[1])
                                lTemp = int(
                                    inpFileOut[self.dataSectList[dataSecI].hklSP[PawleySecI] +
                                               k].split()[2])
                                multiTemp = int(
                                    inpFileOut[self.dataSectList[dataSecI].hklSP[PawleySecI] +
                                               k].split()[3])
                                dSpTemp = float(
                                    inpFileOut[self.dataSectList[dataSecI].hklSP[PawleySecI] +
                                               k].split()[4])

                                hklProfTemp = []
                                calcTempFile = open(os.path.join(self.topasInpDir, "x_ycalc.dat"), "r")
                                line = calcTempFile.readline()
                                hklProfTemp.append(line.split())
                                while line:
                                    if self._want_abort:
                                        wx.PostEvent(self._notify_window, ResultEvent(None))
                                        return
                                    line = calcTempFile.readline()
                                    if line:
                                        hklProfTemp.append(line.split())
                                calcTempFile.close()
                                hklProfTempF = [[float(y) for y in x] for x in hklProfTemp]
                                # We devide the peak intensity by the Pawley scale.
                                for index in range(len(hklProfTempF)):
                                    if self._want_abort:
                                        wx.PostEvent(self._notify_window, ResultEvent(None))
                                        return
                                    hklProfTempF[index][1] -= self.bkgDataF[dataSecI][index][1]
                                    hklProfTempF[index][1] /= scale[i][j]
                                    if hklProfTempF[index][1] < 2E-6:
                                        hklProfTempF[index][1] = 0

                                # Get rid of all zeros to reduce the output file size.
                                hklProfSP = 0
                                hklProfEP = 0
                                for ii in range(len(hklProfTempF)):
                                    if self._want_abort:
                                        wx.PostEvent(self._notify_window, ResultEvent(None))
                                        return
                                    if hklProfTempF[ii][1] != 0:
                                        hklProfSP = ii + 1
                                        break
                                for ii in range(len(hklProfTempF)):
                                    if self._want_abort:
                                        wx.PostEvent(self._notify_window, ResultEvent(None))
                                        return
                                    if hklProfTempF[-(ii+1)][1] != 0:
                                        hklProfEP = len(hklProfTempF) - ii
                                        break

                                hklFileOut.write("{0:5d}{1:5d}{2:5d}{3:5d}{4:16.7F}{5:10d}{6:10d}".
                                                 format(hTemp, kTemp, lTemp, multiTemp,
                                                        dSpTemp, hklProfSP, hklProfEP))

                                for item in hklProfTempF[hklProfSP-1:hklProfEP]:
                                    if self._want_abort:
                                        wx.PostEvent(self._notify_window, ResultEvent(None))
                                        return
                                    hklFileOut.write("{0:17.8F}".format(item[1]))
                                allZero = True
                                for item in hklProfTempF:
                                    if self._want_abort:
                                        wx.PostEvent(self._notify_window, ResultEvent(None))
                                        return
                                    if not item[1] == 0:
                                        allZero = False
                                if allZero:
                                    hklFileOut.write("{0:15.6F}\n".format(0))
                                else:
                                    hklFileOut.write("\n")

                        hklFileOut.close()

                        hklUniqOut = []
                        lenUniqQ = []
                        hklFileOutRead = open(os.path.join(self.topasInpDir,
                                           self.stemName + "_check_hkl_temp" + str(i + 1)), "r")
                        dminLine = hklFileOutRead.readline()
                        for lbTemp in range(numPawleySec):
                            uniqQ = []
                            for iTemp in range(5):
                                if self._want_abort:
                                    wx.PostEvent(self._notify_window, ResultEvent(None))
                                    return
                                line = hklFileOutRead.readline()
                                hklUniqOut.append(line)
                                if iTemp==3:
                                    hklNum = int(line.split("=")[1])
                            for iTemp in range(hklNum):
                                line = hklFileOutRead.readline()
                                alreadyExist = False
                                # for itemitem in uniqQ:
                                #     if self._want_abort:
                                #         wx.PostEvent(self._notify_window, ResultEvent(None))
                                #         return
                                #     if abs(float(line.split()[4])-float(itemitem))<1E-4:
                                #         alreadyExist = True
                                #         break
                                if (not alreadyExist) and (float(line.split()[4]) >= dmin[i]):
                                    uniqQ.append(line.split()[4])
                                    hklUniqOut.append(line)
                            lenUniqQ.append(len(uniqQ))
                        hklFileUniqOut = open(os.path.join(self.topasInpDir,
                                           self.stemName + ".hkl" + str(i + 1)), "w")
                        hklFileUniqOut.write(dminLine)
                        lbTemp = 0
                        for itemTemp in hklUniqOut:
                            if self._want_abort:
                                wx.PostEvent(self._notify_window, ResultEvent(None))
                                return
                            if "# of hkl = " in itemTemp:
                                hklFileUniqOut.write("# of hkl = " + str(lenUniqQ[lbTemp]) + "\n")
                                lbTemp += 1
                            else:
                                hklFileUniqOut.write(itemTemp)
                        hklFileUniqOut.close()

                        if self._want_abort:
                            wx.PostEvent(self._notify_window, ResultEvent(None))
                            return

                    print("\n================= Profile of hkls successfully " +
                          "written out =================\n")

                    now = datetime.datetime.now()
                    if not os.path.isfile(os.path.join(self.topasInpDir, "profile_extract.hist")):
                        log_file = open(os.path.join(self.topasInpDir, "profile_extract.hist"), "w")
                        log_file.write("=====================================================\n")
                        log_file.write("History of profile extraction.\n")
                        log_file.write("=====================================================\n")
                        log_file.write("\n")
                        log_file.write("=====================================================\n")
                        log_file.write("Time stamp: " + str(now)[:19] + "\n")
                        log_file.write("=====================================================\n")
                        log_file.write("Topas executable: " + self.topasExe + "\n")
                        log_file.write("Topas working directory: " + self.topasInpDir + "\n")
                        log_file.write("Topas input file: " + self.stemName + ".inp" + "\n")
                        log_file.write("Input box: " + self.dmInput.GetValue() + "\n")
                        log_file.write("=====================================================")
                    else:
                        log_file = open(os.path.join(self.topasInpDir, "profile_extract.hist"), "a+")
                        log_file.write("\n\n=====================================================\n")
                        log_file.write("Time stamp: " + str(now)[:19] + "\n")
                        log_file.write("=====================================================\n")
                        log_file.write("Topas executable: " + self.topasExe + "\n")
                        log_file.write("Topas working directory: " + self.topasInpDir + "\n")
                        log_file.write("Topas input file: " + self.stemName + ".inp" + "\n")
                        log_file.write("Input box: " + self.dmInput.GetValue() + "\n")
                        log_file.write("=====================================================")
                    
                    log_file.close()
            else:
                wx.LogError('Specify topas executable location, input file and refine type and dmin value first!!!')

            wx.PostEvent(self._notify_window, ResultEvent(numDataSec*numPawleySec))
        except OSError:
            wx.LogError('Fails to extract profiles! Check the test examples if that helps!')
            raise

    def abort(self):
        """abort worker thread."""
        # Method for use by main thread to signal an abort
        self._want_abort = 1

class tof_rm_thread(Thread):

    """Worker Thread Class."""
    def __init__(self, notify_window, i1, i11, i2, topasDirSpec, topasInpSpec,
        topasInp, content, dataSectList, topasInpDir, topasExe, stemName, resMatTOFDone):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self._notify_window = notify_window
        self._want_abort = 0
        
        self.i1 = i1
        self.i11 = i11
        self.i2 = i2
        self.topasDirSpec = topasDirSpec
        self.topasInpSpec = topasInpSpec
        self.topasInp = topasInp
        self.content = content
        self.dataSectList = dataSectList
        self.topasInpDir = topasInpDir
        self.topasExe = topasExe
        self.stemName = stemName
        self.resMatTOFDone = resMatTOFDone

        # This starts the thread running on creation, but you could
        # also make the GUI thread responsible for calling this
        self.start()

    def run(self):
        """Run Worker Thread."""
        # This is the code executing in the new thread. Simulation of
        # a long process (well, 10s here) as a simple loop - you will
        # need to structure your processing so that you periodically
        # peek at the abort variable
        i1ValTemp = self.i1.GetValue()
        i11ValTemp = self.i11.GetValue()
        i2ValTemp = self.i2.GetValue()
        if self.topasDirSpec and self.topasInpSpec and (len(i1ValTemp)>0) and (len(i2ValTemp)>0) \
          and len(i11ValTemp)>0:
            i1Val = float(i1ValTemp.split(",")[0])
            i2Val = float(i1ValTemp.split(",")[1])
            i3Val = float(i1ValTemp.split(",")[2])
            i2FVal = float(i1ValTemp.split(",")[3])
            # shiftCent = int(i1ValTemp.split(",")[4])
            # flip_peak = int(i1ValTemp.split(",")[5])
            shiftCent = 0
            flip_peak = 0
            C_I = float(i2ValTemp.split(",")[0])
            A_I = float(i2ValTemp.split(",")[1])
            Z_I = float(i2ValTemp.split(",")[2])
            C_O = float(i2ValTemp.split(",")[3])
            if len(i11ValTemp.split(";")) == 1:
                si_sq = True
            else:
                si_sq = False
            dataList = []
            for item in i11ValTemp.split(";"):
                dataList.append(item.split(","))

            inpFileIn = open(self.topasInp, 'r')
            self.content = []

            # Read the whole input file to a list.
            line = inpFileIn.readline()
            self.content.append(line)
            while line:
                line = inpFileIn.readline()
                if line:
                    self.content.append(line)
            inpFileIn.close()

            # Worry about 'iters' line. We want to force Topas to run 0 times.
            for i in range(len(self.content)):
                if "iters" in self.content[i]:
                    self.content[i] = "iters 0\n"
                    itersLineExist = True
                    break
                else:
                    itersLineExist = False

            if not itersLineExist:
                self.content.insert(2, "iters 0\n")

            # Delete not defined block if "#ifdef" exists.
            defineLabels = []
            for i in range(len(self.content)):
                if "#define" in self.content[i] and "'" not in self.content[i]:
                    defineLabels.append(self.content[i].split()[1].strip())
            notdefinedB = []
            for i in range(len(self.content)):
                if "#ifdef" in self.content[i]:
                    labelT = self.content[i].split()[1].strip()
                    if labelT not in defineLabels:
                        notdefinedB.append(i)
            for i in range(len(notdefinedB)):
                line2Delete = notdefinedB[i]
                while True:
                    if "#endif" not in self.content[line2Delete]:
                        self.content[line2Delete] = "\n"
                    else:
                        self.content[line2Delete] = "\n"
                        break
                    line2Delete += 1

            spg_pos = []
            for i in range(len(self.content)):
                if "space_group" in self.content[i]:
                    spg_pos.append(i)
            insertedNum = 0
            for i in range(len(spg_pos)):
                self.content.insert(4*insertedNum+spg_pos[i]+1,"load hkl_m_d_th2 I\n")
                self.content.insert(4*insertedNum+spg_pos[i]+2,"{\n")
                self.content.insert(4*insertedNum+spg_pos[i]+3, \
                  "1   1   0   4    2.744190      32.55226     @  1000\n")
                self.content.insert(4*insertedNum+spg_pos[i]+4,"}\n")
                insertedNum += 1

            if self._want_abort:
                wx.PostEvent(self._notify_window, ResultEvent(None))
                return

            for i in range(len(self.content)):
                if "Cubic(" in self.content[i]:
                    self.content[i] = " \n"
            for i in range(len(self.content)):
                if "scale" in self.content[i]:
                    if self.content[i].split()[0]=="scale":
                        self.content[i] = " \n"

            for i in range(len(self.content)):
                if self.content[i].strip()=="str":
                    self.content[i] = "hkl_Is\n"
                if "site" in self.content[i] and "x" in self.content[i] and \
                  "y" in self.content[i] and "z" in self.content[i]:
                    self.content[i] = "\n"

            if (not si_sq):
                tofParas = []
                for item in self.content:
                    if "TOF_x_axis_calibration" in item and "macro" not in item:
                        if "'" in item:
                            if item.lstrip().index("'") != 0:
                                tofParas.append([float(item.split(",")[1].split("_")[0].split("`")[0]),
                                    float(item.split(",")[3].split("_")[0].split("`")[0]),
                                    float(item.split(",")[5].split("_")[0].split("`")[0].split(")")[0])])
                        else:
                            tofParas.append([float(item.split(",")[1].split("_")[0].split("`")[0]),
                                float(item.split(",")[3].split("_")[0].split("`")[0]),
                                float(item.split(",")[5].split("_")[0].split("`")[0].split(")")[0])])

            finishXT = []
            startXT = []
            for item in self.content:
                if "finish_X" in item:
                    finishXT.append(float(item.split()[1]))
                if "start_X" in item:
                    startXT.append(float(item.split()[1]))

            # Delete space group line if they exist.
            self.content = [x for x in self.content if "space_group" not in x]

            # Grab all data sections.
            self.dataSectList = []
            for i in range(len(self.content)):
                if "xdd" in self.content[i]:
                    self.dataSectList.append(data_sect(i))

            # Start and end line for each data section.
            for i in range(len(self.dataSectList)):
                if (i == (len(self.dataSectList) - 1)):
                    self.dataSectList[i].endP = len(self.content) - 1
                else:
                    self.dataSectList[i].endP = self.dataSectList[i + 1].startP - 1

                # Grab the number of the 'hkl_Is' line.
                self.dataSectList[i].hklIsPos = []
                for j in range(self.dataSectList[i].endP - self.dataSectList[i].startP + 1):
                    if self._want_abort:
                        wx.PostEvent(self._notify_window, ResultEvent(None))
                        return
                    if "hkl_Is" in self.content[self.dataSectList[i].startP + j]:
                        self.dataSectList[i].hklIsPos.append(self.dataSectList[i].startP + j)
                    if "#endif" in self.content[self.dataSectList[i].startP + j]:
                        self.dataSectList[i].endP = self.dataSectList[i].startP + j - 1
                        break
                    elif "C_matrix_normalized" in self.content[self.dataSectList[i].startP + j]:
                        self.dataSectList[i].endP = self.dataSectList[i].startP + j - 1
                        break

                # Start and end line for each hkl block.
                self.dataSectList[i].hklSP = []
                self.dataSectList[i].hklEP = []
                for j in range(len(self.dataSectList[i].hklIsPos)):
                    if (j == (len(self.dataSectList[i].hklIsPos) - 1)):
                        for k in range(self.dataSectList[i].endP -
                                       self.dataSectList[i].hklIsPos[j] + 1):
                            if "load hkl_m_d_th2 I" in self.content[
                                    self.dataSectList[i].hklIsPos[j] + k]:
                                tempIndex = self.dataSectList[i].hklIsPos[j] + k + 2
                                self.dataSectList[i].hklSP.append(tempIndex)
                                for l in range(self.dataSectList[i].endP - tempIndex + 1):
                                    if self._want_abort:
                                        wx.PostEvent(self._notify_window, ResultEvent(None))
                                        return
                                    if "}" in self.content[tempIndex + l]:
                                        self.dataSectList[i].hklEP.append(tempIndex + l - 1)
                                        break
                    else:
                        for k in range(self.dataSectList[i].hklIsPos[j + 1] -
                                       self.dataSectList[i].hklIsPos[j] + 1):
                            if "load hkl_m_d_th2 I" in self.content[
                                    self.dataSectList[i].hklIsPos[j] + k]:
                                tempIndex = self.dataSectList[i].hklIsPos[j] + k + 2
                                self.dataSectList[i].hklSP.append(tempIndex)
                                for l in range(self.dataSectList[i].hklIsPos[j + 1] -
                                               tempIndex + 1):
                                    if self._want_abort:
                                        wx.PostEvent(self._notify_window, ResultEvent(None))
                                        return
                                    if "}" in self.content[tempIndex + l]:
                                        self.dataSectList[i].hklEP.append(tempIndex + l - 1)
                                        break

            # Grab the maximum d-spacing for each data section. For TOF neutron data,
            # usually one should have a d-dependent scale factor (d^4). However, such
            # a scaling diverges as d becomes quite large, corresponding to small q.
            # For generating the resolution matrix, one, however, has to go to small
            # q. In this case, we need to cope with the divergence problem. Currently,
            # the method is to force the scaling to be the same with that for largest
            # possible d-spacing for those dummy d-spacings larger than the maximum
            # d-spacing of the structure.
            if (not si_sq):
                dsMax = []
                for i in range(len(self.dataSectList)):
                    dsValTemp = (-tofParas[i][1] + np.sqrt(tofParas[i][1]**2 -
                      4 * tofParas[i][2] * (tofParas[i][0] - finishXT[i])))/(2*tofParas[i][2])
                    dsMax.append(dsValTemp)

            qMin = []
            if (not si_sq):
                for i in range(len(dsMax)):
                    qMin.append(2*np.pi/dsMax[i])
            else:
                qMin.append(startXT[0])

            if (not si_sq):
                # Read in diffc, diffa and zero, again, for q-TOF transformation.
                aczData = []
                for i in range(len(self.content)):
                    if self._want_abort:
                        wx.PostEvent(self._notify_window, ResultEvent(None))
                        return
                    item = self.content[i].lstrip()
                    if ("TOF_x_axis_calibration" in item) and ("macro" not in item):
                        if ("'" in item):
                            if (not item.index("'")==0):
                                lineTemp = item.split("(")[1].split(")")[0]
                                zTemp = float(lineTemp.split(",")[1].split("_")[0].split("`")[0])
                                cTemp = float(lineTemp.split(",")[3].split("_")[0].split("`")[0])
                                aTemp = float(lineTemp.split(",")[5].split("_")[0].split("`")[0])
                                aczData.append([aTemp,cTemp,zTemp])
                        else:
                            lineTemp = item.split("(")[1].split(")")[0]
                            zTemp = float(lineTemp.split(",")[1].split("_")[0].split("`")[0])
                            cTemp = float(lineTemp.split(",")[3].split("_")[0].split("`")[0])
                            aTemp = float(lineTemp.split(",")[5].split("_")[0].split("`")[0])
                            aczData.append([aTemp,cTemp,zTemp])

            # Check whether the given Qmin value is OK, based on the TOF calibration
            # parameters of all datasets. Basically, the criterion here is the monotonicity
            # of the q-TOF curve. Without checking the Qmin value, sometimes we will get
            # negative TOF for very small q values.
            if (not si_sq):
                qNotOK = False
                qMinMin = 0
                for i in range(len(self.dataSectList)):
                    if -4*np.pi*aczData[i][0]/aczData[i][1] > qMinMin:
                        qMinMin = -4*np.pi*aczData[i][0]/aczData[i][1]
                if i1Val < qMinMin:
                    qNotOK = True
            else:
                qNotOK = False

            # Proceed only when Qmin is OK.
            if qNotOK:
                wx.MessageBox('Qmin too small (<' + str(round(qMinMin,5)) + \
                  ')!!! Please increase Qmin and try again!!!', \
                  'Warning', wx.OK | wx.ICON_WARNING)
            else:
                for i in range(len(self.dataSectList)):
                    self.content.insert(self.dataSectList[i].hklIsPos[0] + 1 + 3 * i, "space_group \"Fm-3m\"\n")
                    self.content.insert(self.dataSectList[i].hklIsPos[0] + 2 + 3 * i, "Cubic(5.0)\n")
                    self.content.insert(self.dataSectList[i].hklIsPos[0] + 3 + 3 * i, "scale 1.0\n")

                preTempFile = open(os.path.join(self.topasInpDir, "temptemp.inp"),"w")
                for item in self.content:
                    preTempFile.write(item)
                preTempFile.close()

                sp.call([self.topasExe, os.path.join(self.topasInpDir,
                  "temptemp.inp")])#, stdout=sp.DEVNULL, stderr=sp.STDOUT)

                inpFileIn = open(os.path.join(self.topasInpDir, "temptemp.out"), 'r')

                self.content = []
                # Read the whole input file to a list.
                line = inpFileIn.readline()
                self.content.append(line)
                while line:
                    line = inpFileIn.readline()
                    if line:
                        self.content.append(line)
                inpFileIn.close()

                # Delete the report lines if they exist.
                self.content = [x for x in self.content if ("Out_X_Yobs" not in x) \
                  and ("Out_X_Ycalc" not in x)]

                # Delete MVW line if they exist. This is not necessary for
                # the resolution matrix generation. But just to keep it for
                # potential future use.
                self.content = [x for x in self.content if "MVW" not in x]

                # Insert 'MVW' line for all hkl_Is sections.
                hklIs_line = []
                hklIs_line_num = 0
                for i in range(len(self.content)):
                    if "hkl_Is" in self.content[i]:
                        hklIs_line_num += 1
                        hklIs_line.append(i + hklIs_line_num)

                for item in hklIs_line:
                    self.content.insert(item, "\t\tMVW(0,0,0)\n")

                if self._want_abort:
                    wx.PostEvent(self._notify_window, ResultEvent(None))
                    return

                if (not si_sq):
                    # Insert 'Out_Q_Ycalc' line for all hkl_Is sections.
                    out_line = []
                    out_line_num = 0
                    for i in range(len(self.content)):
                        if "xdd" in self.content[i]:
                            out_line_num += 1
                            out_line.append(i + out_line_num)

                    for i in range(len(out_line)):
                        self.content.insert(out_line[i], "\t" + \
                          "Out_Q_Ycalc(\"q_ycalc_resmat_tof" + str(i+1) + ".dat\"," + \
                          str(aczData[i][0]) + "," + str(aczData[i][1]) + "," + str(aczData[i][2]) + ")\n")

                    self.content.append("\nmacro Out_Q_Ycalc(file,a,c,z)\n")
                    self.content.append("{\n")
                    self.content.append("xdd_out file load out_record out_fmt out_eqn\n")
                    self.content.append("{\n")
                    self.content.append("\"%11.6f \" = 4 Pi (a) / (Sqrt((c)^2 - 4 (a) ((z) - X)) - (c));\n")
                    self.content.append("\"%11.6f\\n\" = Ycalc;\n")
                    self.content.append("}\n")
                    self.content.append("}")
                else:
                    out_line = []
                    out_line_num = 0
                    for i in range(len(self.content)):
                        if "xdd" in self.content[i]:
                            out_line_num += 1
                            out_line.append(i + out_line_num)

                    for i in range(len(out_line)):
                        self.content.insert(out_line[i], "\t" + \
                          "Out_X_Ycalc(\"q_ycalc_resmat_tof" + str(i+1) + ".dat\"" + ")\n")

                # Configure the input file again after we change and run the initial
                # topas input file.
                self.dataSectList = []
                # Grab all data sections.
                for i in range(len(self.content)):
                    if ("xdd" in self.content[i]) and ("xdd_out" not in self.content[i]):
                        self.dataSectList.append(data_sect(i))

                # Start and end line for each data section.
                for i in range(len(self.dataSectList)):
                    if (i == (len(self.dataSectList) - 1)):
                        self.dataSectList[i].endP = len(self.content) - 1
                    else:
                        self.dataSectList[i].endP = self.dataSectList[i + 1].startP - 1

                    # Grab the number of the 'hkl_Is' line.
                    self.dataSectList[i].hklIsPos = []
                    for j in range(self.dataSectList[i].endP - self.dataSectList[i].startP + 1):
                        if self._want_abort:
                            wx.PostEvent(self._notify_window, ResultEvent(None))
                            return
                        if "hkl_Is" in self.content[self.dataSectList[i].startP + j]:
                            self.dataSectList[i].hklIsPos.append(self.dataSectList[i].startP + j)
                        if "#endif" in self.content[self.dataSectList[i].startP + j]:
                            self.dataSectList[i].endP = self.dataSectList[i].startP + j - 1
                            break
                        elif "C_matrix_normalized" in self.content[self.dataSectList[i].startP + j]:
                            self.dataSectList[i].endP = self.dataSectList[i].startP + j - 1
                            break

                    # Start and end line for each hkl block.
                    self.dataSectList[i].hklSP = []
                    self.dataSectList[i].hklEP = []
                    for j in range(len(self.dataSectList[i].hklIsPos)):
                        if (j == (len(self.dataSectList[i].hklIsPos) - 1)):
                            for k in range(self.dataSectList[i].endP -
                                        self.dataSectList[i].hklIsPos[j] + 1):
                                if "load hkl_m_d_th2 I" in self.content[
                                        self.dataSectList[i].hklIsPos[j] + k]:
                                    tempIndex = self.dataSectList[i].hklIsPos[j] + k + 2
                                    self.dataSectList[i].hklSP.append(tempIndex)
                                    for l in range(self.dataSectList[i].endP - tempIndex + 1):
                                        if self._want_abort:
                                            wx.PostEvent(self._notify_window, ResultEvent(None))
                                            return
                                        if "}" in self.content[tempIndex + l]:
                                            self.dataSectList[i].hklEP.append(tempIndex + l - 1)
                                            break
                        else:
                            for k in range(self.dataSectList[i].hklIsPos[j + 1] -
                                        self.dataSectList[i].hklIsPos[j] + 1):
                                if "load hkl_m_d_th2 I" in self.content[
                                        self.dataSectList[i].hklIsPos[j] + k]:
                                    tempIndex = self.dataSectList[i].hklIsPos[j] + k + 2
                                    self.dataSectList[i].hklSP.append(tempIndex)
                                    for l in range(self.dataSectList[i].hklIsPos[j + 1] -
                                                tempIndex + 1):
                                        if self._want_abort:
                                            wx.PostEvent(self._notify_window, ResultEvent(None))
                                            return
                                        if "}" in self.content[tempIndex + l]:
                                            self.dataSectList[i].hklEP.append(tempIndex + l - 1)
                                            break

                # Set all hkl intensity to zero for extracting the background.
                if (not si_sq):
                    lattPos = []
                    for i in range(len(self.dataSectList)):
                        for j in range(self.dataSectList[i].startP, self.dataSectList[i].endP + 1):
                            if self._want_abort:
                                wx.PostEvent(self._notify_window, ResultEvent(None))
                                return
                            if "finish_X" in self.content[j]:
                                tofMax = aczData[i][0]*(2*np.pi/i1Val)**2+aczData[i][1]*(2*np.pi/i1Val)+aczData[i][2]
                                atPos = self.content[j].find("finish_X")
                                self.content[j] = self.content[j][:atPos] + "finish_X " + str(int(tofMax*2)) + "\n"
                            if "start_X" in self.content[j]:
                                atPos = self.content[j].find("start_X")
                                self.content[j] = self.content[j][:atPos] + "start_X 0\n"
                        for j in range(len(self.dataSectList[i].hklIsPos)):
                            if j == 0:
                                for k in range(self.dataSectList[i].hklIsPos[j], self.dataSectList[i].endP + 1):
                                    if self._want_abort:
                                        wx.PostEvent(self._notify_window, ResultEvent(None))
                                        return
                                    if "Cubic(" in self.content[k]:
                                        lattPos.append(k)
                            for k in range(self.dataSectList[i].hklEP[j] - self.dataSectList[i].hklSP[j] + 1):
                                if self._want_abort:
                                    wx.PostEvent(self._notify_window, ResultEvent(None))
                                    return
                                atPos = self.content[self.dataSectList[i].hklSP[j] + k].find("@")
                                self.content[self.dataSectList[i].hklSP[j] + k] = \
                                    self.content[self.dataSectList[i].hklSP[j] + k][:atPos] + " 0\n"
                else:
                    lattPos = []
                    for i in range(len(self.dataSectList)):
                        for j in range(self.dataSectList[i].startP, self.dataSectList[i].endP + 1):
                            if self._want_abort:
                                wx.PostEvent(self._notify_window, ResultEvent(None))
                                return
                            if "finish_X" in self.content[j]:
                                atPos = self.content[j].find("finish_X")
                                self.content[j] = self.content[j][:atPos] + "finish_X " + str(int(50)) + "\n"
                            if "start_X" in self.content[j]:
                                atPos = self.content[j].find("start_X")
                                self.content[j] = self.content[j][:atPos] + "start_X 0\n"
                        for j in range(len(self.dataSectList[i].hklIsPos)):
                            if j == 0:
                                for k in range(self.dataSectList[i].hklIsPos[j], self.dataSectList[i].endP + 1):
                                    if self._want_abort:
                                        wx.PostEvent(self._notify_window, ResultEvent(None))
                                        return
                                    if "Cubic(" in self.content[k]:
                                        lattPos.append(k)
                            for k in range(self.dataSectList[i].hklEP[j] - self.dataSectList[i].hklSP[j] + 1):
                                atPos = self.content[self.dataSectList[i].hklSP[j] + k].find("@")
                                self.content[self.dataSectList[i].hklSP[j] + k] = \
                                    self.content[self.dataSectList[i].hklSP[j] + k][:atPos] + " 0\n"

                if abs(i2FVal - 0) > 1E-6:
                    # Generate dummy xye data.
                    if (not si_sq):
                        qarray = np.arange(i1Val,2.2*i3Val,i2FVal)
                        for i in range(len(self.dataSectList)):
                            dataTempFile = open(os.path.join(self.topasInpDir, \
                            "dataTemp" + str(i) + ".xye"), "w")
                            for item in reversed(qarray):
                                if self._want_abort:
                                    wx.PostEvent(self._notify_window, ResultEvent(None))
                                    return
                                tofTemp = aczData[i][0] * (2*np.pi/item)**2 + aczData[i][1] * (2*np.pi/item) + aczData[i][2]
                                dataTempFile.write("{0:15.7F}{1:11.3F}{2:11.3F}\n".format(tofTemp, 500, 15))
                            dataTempFile.close()
                    else:
                        qarray = np.arange(i2FVal,2.2*i3Val,i2FVal)
                        for i in range(len(self.dataSectList)):
                            dataTempFile = open(os.path.join(self.topasInpDir, \
                            "dataTemp" + str(i) + ".xye"), "w")
                            for item in qarray:
                                if self._want_abort:
                                    wx.PostEvent(self._notify_window, ResultEvent(None))
                                    return
                                dataTempFile.write("{0:15.7F}{1:11.3F}{2:11.3F}\n".format(item, 500, 15))
                            dataTempFile.close()

                    line_num = 0
                    for i in range(len(self.content)):
                        if "xdd" in self.content[i] and "_out" not in self.content[i]:
                            self.content[i] = "xdd \".\\dataTemp" + str(line_num) + ".xye\"\n"
                            line_num += 1
                else:
                    line_num = 0
                    for i in range(len(self.content)):
                        if "xdd" in self.content[i] and "_out" not in self.content[i]:
                            if "\"" in self.content[i]:
                                file_temp = self.content[i].split()[1].split("\"")[1]
                            else:
                                file_temp = self.content[i].split()[1]
                            file_temp_read = open(os.path.join(self.topasInpDir, file_temp), "r")
                            q_temp = []
                            while True:
                                if self._want_abort:
                                    wx.PostEvent(self._notify_window, ResultEvent(None))
                                    return
                                line = file_temp_read.readline()
                                if line:
                                    try:
                                        q_temp.append(float(line.split()[0]))
                                    except:
                                        continue
                                else:
                                    break

                            if (not si_sq):
                                for j in range(len(q_temp)):
                                    if self._want_abort:
                                        wx.PostEvent(self._notify_window, ResultEvent(None))
                                        return
                                    q_temp[j] = 4 * np.pi * aczData[line_num][0] / (np.sqrt(aczData[line_num][1]**2 - \
                                        4 * aczData[line_num][0] * (aczData[line_num][2] - q_temp[j])) - aczData[line_num][1])
                                qarray = []
                                for item in reversed(q_temp):
                                    qarray.append(item)
                            else:
                                qarray = []
                                for item in q_temp:
                                    qarray.append(item)
                            
                            if (not si_sq):
                                if qarray[0] > i1Val:
                                    q_temp = np.arange(i1Val, qarray[0], qarray[1] - qarray[0])
                                    q_temp = q_temp.tolist()
                                    q_temp.extend(qarray)
                                    qarray = q_temp
                                elif qarray[0] < i1Val:
                                    if (not si_sq):
                                        q_temp = []
                                        for j in range(len(qarray)):
                                            if qarray[j] > i1Val:
                                                q_temp.append(qarray[j])
                                        q_temp.insert(0, i1Val)
                                        qarray = q_temp
                                    else:
                                        q_temp = []
                                        for j in range(len(qarray)):
                                            if qarray[j] >= i1Val:
                                                q_temp.append(qarray[j])

                            interval = qarray[-1] - qarray[-2]
                            while qarray[-1] < 2.2*i3Val:
                                qarray.append(qarray[-1] + interval)

                            dataTempFile = open(os.path.join(self.topasInpDir, \
                              "dataTemp" + str(line_num) + ".xye"), "w")

                            if (not si_sq):
                                for item in reversed(qarray):
                                    tofTemp = aczData[line_num][0] * (2*np.pi/item)**2 + \
                                      aczData[line_num][1] * (2*np.pi/item) + aczData[line_num][2]
                                    dataTempFile.write("{0:15.7F}{1:11.3F}{2:11.3F}\n".format(tofTemp, 500, 15))
                                dataTempFile.close()
                            else:
                                for item in qarray:
                                    dataTempFile.write("{0:15.7F}{1:11.3F}{2:11.3F}\n".format(item, 500, 15))
                                dataTempFile.close()

                            self.content[i] = "xdd \".\\dataTemp" + str(line_num) + ".xye\"\n"

                            line_num += 1

                bkgTempFile = open(os.path.join(self.topasInpDir, "bkg_extract_temp.inp"), "w")
                for item in self.content:
                    bkgTempFile.write(item)
                bkgTempFile.close()
                sp.call([self.topasExe, os.path.join(self.topasInpDir, \
                "bkg_extract_temp.inp")])#, stdout=sp.DEVNULL, stderr=sp.STDOUT)
                bkgTempData = []
                for i in range(len(self.dataSectList)):
                    if self._want_abort:
                        wx.PostEvent(self._notify_window, ResultEvent(None))
                        return
                    bkgTempData.append([])
                    bkgDataFile = open(os.path.join(self.topasInpDir, \
                    "q_ycalc_resmat_tof" + str(i+1) + ".dat"))
                    line = bkgDataFile.readline()
                    bkgValTemp = float(line.split()[1])
                    bkgTempData[i].append(bkgValTemp)
                    while line:
                        line = bkgDataFile.readline()
                        if line:
                            bkgValTemp = float(line.split()[1])
                            bkgTempData[i].append(bkgValTemp)
                    bkgDataFile.close()

                # For the TOF data, we need to reverse the Q points since by default
                # it will be given in a descending order.
                if (not si_sq):
                    bkgTempTemp = []
                    for i in range(len(self.dataSectList)):
                        bkgTempTemp.append([x for x in reversed(bkgTempData[i])])
                    bkgTempData = bkgTempTemp

                hkl2Config = []
                for i in range(len(self.dataSectList)):
                    for j in range(len(self.dataSectList[i].hklIsPos)):
                        for k in range(self.dataSectList[i].hklEP[j] - self.dataSectList[i].hklSP[j] + 1):
                            if self._want_abort:
                                wx.PostEvent(self._notify_window, ResultEvent(None))
                                return
                            if (j == 0 and k == 0):
                                multi = float(self.content[self.dataSectList[i].hklSP[j] + k].split()[3])
                                atPos = len(self.content[self.dataSectList[i].hklSP[j] + k]) - 2
                                self.content[self.dataSectList[i].hklSP[j] + k] = \
                                    self.content[self.dataSectList[i].hklSP[j] + k][:atPos] \
                                    + str(100000/multi) + "\n"
                                hTemp = float(self.content[self.dataSectList[i].hklSP[j] + k].split()[0])
                                kTemp = float(self.content[self.dataSectList[i].hklSP[j] + k].split()[1])
                                lTemp = float(self.content[self.dataSectList[i].hklSP[j] + k].split()[2])
                                hkl2Config.append([hTemp,kTemp,lTemp])
                            elif (j == 0):
                                self.content[self.dataSectList[i].hklSP[j] + k] = \
                                "'" + self.content[self.dataSectList[i].hklSP[j] + k]

                if self._want_abort:
                    wx.PostEvent(self._notify_window, ResultEvent(None))
                    return

                print("============== Proceed to generate resolution matrix ===================")
                print("================= Usually this will take tens of minutes =================")

                total = len(self.dataSectList) * int((i3Val+i2Val-i1Val)/i2Val)
                processed = 0
                # plt.ion()
                # fig = []
                # ax = []
                for i in range(len(self.dataSectList)):
                    if self._want_abort:
                        wx.PostEvent(self._notify_window, ResultEvent(None))
                        return
                    print("\n=================== Processing data section " + str(i+1) + " ====================")
                    if abs(i2FVal - 0.0) > 1E-5:
                        qarrayDExp = np.arange(i1Val,2.2*i3Val,i2FVal)
                    else:
                        dataTempFile = open(os.path.join(self.topasInpDir, \
                          "q_ycalc_resmat_tof" + str(i+1) + ".dat"), "r")
                        qarrayDExpT = []
                        while True:
                            line = dataTempFile.readline()
                            if line:
                                qarrayDExpT.append(float(line.split()[0]))
                            else:
                                break
                        dataTempFile.close()
                        if (not si_sq):
                            qarrayDExp = []
                            for item in reversed(qarrayDExpT):
                                qarrayDExp.append(item)
                            qarrayDExp = np.asarray(qarrayDExp)
                        else:
                            qarrayDExp = []
                            for item in qarrayDExpT:
                                qarrayDExp.append(item)
                            qarrayDExp = np.asarray(qarrayDExp)

                    qarrayTT = np.arange(i1Val,2.2*i3Val,i2Val)
                    qarrayT = np.arange(i1Val,i3Val+i2Val,i2Val)
                    qarray = np.zeros(len(qarrayT))
                    tarray = np.zeros(len(qarrayT))
                    q_to_t(qarrayT,A_I,C_I,Z_I,tarray)
                    t_to_q(tarray,A_I,C_O,Z_I,qarray)
                    resMatData = np.zeros((len(qarray),len(qarray)))
                    # fig.append(plt.figure())
                    # fig[i].canvas.set_window_title("Data section-" + str(i + 1))
                    # ax.append(fig[i].add_subplot(111))
                    sumTemp = []
                    for j in range(len(qarray)):
                        if self._want_abort:
                            wx.PostEvent(self._notify_window, ResultEvent(None))
                            return
                        aTemp = (np.sqrt(hkl2Config[i][0]**2 + hkl2Config[i][1]**2 +
                          hkl2Config[i][2]**2)) * 2 * np.pi / qarray[j]
                        atPos = self.content[lattPos[i]].find("(")
                        self.content[lattPos[i]] = self.content[lattPos[i]][:atPos] + \
                        "(" + str(aTemp) + ")\n"
                        resFile = open(os.path.join(self.topasInpDir, "res_mat_prep_temp.inp"),"w")
                        for item in self.content:
                            resFile.write(item)
                        resFile.close()
                        sp.call([self.topasExe, os.path.join(self.topasInpDir, \
                          "res_mat_prep_temp.inp")])#, stdout=sp.DEVNULL, stderr=sp.STDOUT)
                        yCalcTemp = []
                        qYFileTemp = open(os.path.join(self.topasInpDir, \
                          "q_ycalc_resmat_tof" + str(i+1) + ".dat"), "r")
                        line = qYFileTemp.readline()
                        yCalcTemp.append(float(line.split()[1]))
                        while line:
                            line = qYFileTemp.readline()
                            if line:
                                yCalcTemp.append(float(line.split()[1]))
                        qYFileTemp.close()
                        if (not si_sq):
                            yCalcTempTemp = [x for x in reversed(yCalcTemp)]
                            yCalcTemp = yCalcTempTemp
                        for k in range(len(yCalcTemp)):
                            yCalcTemp[k] -= bkgTempData[i][k]
                        for k in range(len(qarrayDExp)):
                            # Here is the actual place where we worry about the
                            # divergence problem when q becomes too small.
                            if qarrayDExp[k] < qMin[i]:
                                yCalcTemp[k] *= (qarrayDExp[k]/qMin[i])**4
                        if (abs(C_I-C_O)<1E-5):
                            if (shiftCent==1):
                                maxPos = yCalcTemp.index(max(yCalcTemp))
                                jPos = np.where(qarrayDExp==min(qarrayDExp, key=lambda x:abs(x-qarray[j])))[0][0]
                                if (maxPos != jPos):
                                    if (maxPos > jPos):
                                        yCalcTempRot = shiftLbyn(yCalcTemp,abs(maxPos-jPos))
                                        yCalcTemp = yCalcTempRot
                                        for k in range(abs(maxPos-jPos)):
                                            yCalcTemp[-(k+1)] = yCalcTemp[-(abs(maxPos-jPos)+1)]
                                    else:
                                        yCalcTempRot = shiftRbyn(yCalcTemp,abs(maxPos-jPos))
                                        yCalcTemp = yCalcTempRot
                                        for k in range(abs(maxPos-jPos)):
                                            yCalcTemp[k] = yCalcTemp[abs(maxPos-jPos)]

                        leftTemp = []
                        rightTemp = []
                        leftNum = 0

                        if self._want_abort:
                            wx.PostEvent(self._notify_window, ResultEvent(None))
                            return

                        if yCalcTemp[0] == 0 and flip_peak == 1:
                            if (abs(i2Val-i2FVal)>1E-5) and (abs(i2FVal-0.0) > 1E-5):
                                for k in range(len(qarrayDExp)):
                                    if self._want_abort:
                                        wx.PostEvent(self._notify_window, ResultEvent(None))
                                        return
                                    if (qarrayDExp[k]<qarray[j]):
                                        leftTemp.append(yCalcTemp[k])
                                        yCalcTemp[k] = 0
                                        leftNum += 1
                                    else:
                                        break
                                for k in range(len(yCalcTemp)):
                                    if self._want_abort:
                                        wx.PostEvent(self._notify_window, ResultEvent(None))
                                        return
                                    if (qarrayDExp[k]>qarray[j]):
                                        rightTemp.append(yCalcTemp[k])
                                        yCalcTemp[k] = 0
                                for k in range(leftNum):
                                    yCalcTemp[leftNum-k-1] = rightTemp[k]
                                    yCalcTemp[leftNum+k] = leftTemp[-(k+1)]
                            elif abs(i2FVal-0.0) > 1E-5:
                                for k in range(len(qarrayDExp)):
                                    if self._want_abort:
                                        wx.PostEvent(self._notify_window, ResultEvent(None))
                                        return
                                    if (k<j):
                                        leftTemp.append(yCalcTemp[k])
                                        yCalcTemp[k] = 0
                                        leftNum += 1
                                    else:
                                        break
                                for k in range(len(yCalcTemp)):
                                    if self._want_abort:
                                        wx.PostEvent(self._notify_window, ResultEvent(None))
                                        return
                                    if (k>j):
                                        rightTemp.append(yCalcTemp[k])
                                        yCalcTemp[k] = 0
                                for k in range(leftNum):
                                    if self._want_abort:
                                        wx.PostEvent(self._notify_window, ResultEvent(None))
                                        return
                                    yCalcTemp[leftNum-k-1] = rightTemp[k]
                                    yCalcTemp[leftNum+k+1] = leftTemp[-(k+1)]

                        finterp = interp1d(qarrayDExp, yCalcTemp, kind='nearest')
                        if abs(i2FVal-0.0) < 1E-5 and flip_peak == 1:
                            yCalcTempInterpT = finterp(qarrayTT)
                            leftTemp = []
                            rightTemp = []
                            leftNum = 0
                            if yCalcTempInterpT[0] == 0:
                                for k in range(len(qarrayTT)):
                                    if self._want_abort:
                                        wx.PostEvent(self._notify_window, ResultEvent(None))
                                        return
                                    if (k<j):
                                        leftTemp.append(yCalcTempInterpT[k])
                                        yCalcTempInterpT[k] = 0
                                        leftNum += 1
                                    else:
                                        break
                                for k in range(len(yCalcTempInterpT)):
                                    if self._want_abort:
                                        wx.PostEvent(self._notify_window, ResultEvent(None))
                                        return
                                    if (k>j):
                                        rightTemp.append(yCalcTempInterpT[k])
                                        yCalcTempInterpT[k] = 0
                                for k in range(leftNum):
                                    if self._want_abort:
                                        wx.PostEvent(self._notify_window, ResultEvent(None))
                                        return
                                    yCalcTempInterpT[leftNum-k-1] = rightTemp[k]
                                    yCalcTempInterpT[leftNum+k+1] = leftTemp[-(k+1)]
                            yCalcTempInterp = []
                            for k in range(len(qarrayT)):
                                yCalcTempInterp.append(yCalcTempInterpT[k])
                        else:
                            yCalcTempInterp = finterp(qarrayT)
                        sumTempTemp = 0
                        for k in range(len(qarrayT)):
                            if self._want_abort:
                                wx.PostEvent(self._notify_window, ResultEvent(None))
                                return
                            resMatData[j][k] = yCalcTempInterp[k]
                            sumTempTemp += resMatData[j][k]
                        sumTemp.append(sumTempTemp)
                        processed += 1
                        perct = float(processed) / float(total) * 100
                        if processed%(int(0.01*total)) == 0 or (processed==total):
                            print("================== Progress: {0:3.0F} % ==================".format(perct))
                        # ax[i].cla()
                        # ax[i].imshow(resMatData,cmap='BuGn')
                        # ax[i].set_title("Resolution matrix generation")
                        # ax[i].title.set_fontsize(15)
                        # ax[i].title.set_fontweight('bold')
                        # ax[i].xaxis.label.set_fontsize(17)
                        # ax[i].yaxis.label.set_fontweight('bold')
                        # ax[i].yaxis.label.set_fontsize(17)
                        # ax[i].xaxis.label.set_fontweight('bold')
                        # for itemitem in ax[i].get_xticklabels():
                        #     itemitem.set_fontsize(13)
                        # for itemitem in ax[i].get_yticklabels():
                        #     itemitem.set_fontsize(13)
                        # fig[i].canvas.flush_events()
                        # fig[i].canvas.draw()
                        if self._want_abort:
                            wx.PostEvent(self._notify_window, ResultEvent(None))
                            return

                    for tempi in range(len(resMatData)):
                        toSubtract = 0
                        for tempj in range(len(resMatData[tempi])):
                            if self._want_abort:
                                wx.PostEvent(self._notify_window, ResultEvent(None))
                                return
                            if (resMatData[tempi][tempj]/sumTemp[tempi] < 1E-4):
                                toSubtract += resMatData[tempi][tempj]
                                resMatData[tempi][tempj] = 0
                        sumTemp[tempi] -= toSubtract

                    resMatRed = []
                    index = 0
                    for item in resMatData:
                        for k in range(len(item)):
                            if self._want_abort:
                                wx.PostEvent(self._notify_window, ResultEvent(None))
                                return
                            if item[k] != 0:
                                spTemp = k + 1
                                startPFound = True
                                break
                        for k in range(len(item)):
                            if self._want_abort:
                                wx.PostEvent(self._notify_window, ResultEvent(None))
                                return
                            if item[-(k+1)] != 0:
                                epTemp = len(item) - k
                                endPFound = True
                                break
                        if not startPFound and not endPFound:
                            spTemp = 0
                            epTemp = 0

                        # The sumTemp array here is for normalizing the resolution matrix.
                        resMatRed.append([x/sumTemp[index] for x in item[spTemp-1:epTemp]])
                        resMatRed[index].insert(0,spTemp)
                        resMatRed[index].insert(1,epTemp)

                        index += 1

                    resMatFile = open(os.path.join(self.topasInpDir, "res_matrix" + str(i+1) + ".dat"), "w")
                    for j in range(len(resMatRed)):
                        resMatFile.write("{0:11d}{1:11d}".format(resMatRed[j][0], resMatRed[j][1]))
                        for k in range(2, len(resMatRed[j])):
                            if self._want_abort:
                                wx.PostEvent(self._notify_window, ResultEvent(None))
                                return
                            resMatFile.write("{0:11.8F}".format(resMatRed[j][k]))
                        resMatFile.write("\n")
                    resMatFile.close()

                # Combine the resolution matrices for all banks to a single file.
                resMatFileFinal = open(os.path.join(self.topasInpDir, "res_matrix.dat"), "w")
                resMatFileFinal.write("{0:11d}{1:11d}\n".format(len(dataList), len(resMatRed)))
                for item in dataList:
                    if len(item)==1:
                        resMatFileTemp = open(os.path.join(self.topasInpDir, "res_matrix" + str(int(item[0]))+ ".dat"), "r")
                        for j in range(len(resMatRed)):
                            if self._want_abort:
                                wx.PostEvent(self._notify_window, ResultEvent(None))
                                return
                            resMatFileFinal.write(resMatFileTemp.readline())
                        resMatFileTemp.close()
                    else:
                        numOfDataSec = int(item[0])
                        sectTemp = item[1:numOfDataSec+1]
                        sect = [int(x) for x in sectTemp]
                        sectSepTemp = item[(numOfDataSec+1):(2*numOfDataSec)]
                        sectSep = [float(x) for x in sectSepTemp]
                        sectSepPnt = [int((x-i1Val)/i2Val) for x in sectSep]
                        OutTemp = []
                        for j in range(len(sect)):
                            resMatFileTemp = open(os.path.join(self.topasInpDir, "res_matrix" + str(sect[j]) + ".dat"), "r")
                            resMatLines = resMatFileTemp.readlines()
                            resMatFileTemp.close()
                            if j==0:
                                for k in range(len(resMatLines)):
                                    if self._want_abort:
                                        wx.PostEvent(self._notify_window, ResultEvent(None))
                                        return
                                    if (k < sectSepPnt[0]):
                                        OutTemp.append(resMatLines[k])
                            elif (j==len(sect)-1):
                                for k in range(len(resMatLines)):
                                    if self._want_abort:
                                        wx.PostEvent(self._notify_window, ResultEvent(None))
                                        return
                                    if (k>=sectSepPnt[j-1]):
                                        OutTemp.append(resMatLines[k])
                            else:
                                for k in range(len(resMatLines)):
                                    if self._want_abort:
                                        wx.PostEvent(self._notify_window, ResultEvent(None))
                                        return
                                    if (k>=sectSepPnt[j-1]) and (k<sectSepPnt[j]):
                                        OutTemp.append(resMatLines[k])
                        for itemTemp in OutTemp:
                            resMatFileFinal.write(itemTemp)
                resMatFileFinal.close()

                now = datetime.datetime.now()
                if not os.path.isfile(os.path.join(self.topasInpDir, "res_matrix.hist")):
                    log_file = open(os.path.join(self.topasInpDir, "res_matrix.hist"), "w")
                    log_file.write("=====================================================\n")
                    log_file.write("History of resolution matrix generation.\n")
                    log_file.write("=====================================================\n")
                    log_file.write("\n")
                    log_file.write("=====================================================\n")
                    log_file.write("Time stamp: " + str(now)[:19] + "\n")
                    log_file.write("=====================================================\n")
                    log_file.write("Topas executable: " + self.topasExe + "\n")
                    log_file.write("Topas working directory: " + self.topasInpDir + "\n")
                    log_file.write("Topas input file: " + self.stemName + ".inp" + "\n")
                    log_file.write("Input box-1: " + i1ValTemp + "\n")
                    log_file.write("Input box-2: " + i11ValTemp + "\n")
                    log_file.write("Input box-3: " + i2ValTemp + "\n")
                    log_file.write("=====================================================")
                else:
                    log_file = open(os.path.join(self.topasInpDir, "res_matrix.hist"), "w+")
                    log_file.write("\n\n")
                    log_file.write("=====================================================\n")
                    log_file.write("Time stamp: " + str(now)[:19] + "\n")
                    log_file.write("=====================================================\n")
                    log_file.write("Topas executable: " + self.topasExe + "\n")
                    log_file.write("Topas working directory: " + self.topasInpDir + "\n")
                    log_file.write("Topas input file: " + self.stemName + ".inp" + "\n")
                    log_file.write("Input box-1: " + i1ValTemp + "\n")
                    log_file.write("Input box-2: " + i11ValTemp + "\n")
                    log_file.write("Input box-3: " + i2ValTemp + "\n")
                    log_file.write("=====================================================")
                
                log_file.close()

                # Cleaning up the resolution matrices files for each individual file.
                for i in range(len(self.dataSectList)):
                    os.remove(os.path.join(self.topasInpDir, "res_matrix" + str(i+1) + ".dat"))

                self.resMatTOFDone = True
                print("============= Resolution matrix successfully generated ==================\n")
                # plt.ioff()
                # plt.show()
        else:
            wx.LogError('Specify the topas install dir, topas input file and q grid values first!!!')

        # Here's where the result would be returned (this is an
        # example fixed result of the number 10, but it could be
        # any Python object)
        wx.PostEvent(self._notify_window, ResultEvent(total))

    def abort(self):
        """abort worker thread."""
        # Method for use by main thread to signal an abort
        self._want_abort = 1


# Class containing the line indeces for each data section.
class data_sect(object):
    def __init__(self, startP=None, endP=None, hklIsPos=None, hklSP=None, hklEP=None):
        self.startP = startP
        self.endP = endP
        self.hklIsPos = hklIsPos
        self.hklSP = hklSP
        self.hklEP = hklEP

# The first tab for extracting profiles.
class ProfileExtract(wx.Panel):
    def __init__(self, parent):
        self.topasDir = ''
        self.stemName = ''
        self.topasExe = ''
        self.topasInp = ''
        self.topasInpDir = ''
        self.topasDirSpec = False
        self.topasInpSpec = False
        self.profileOut = False
        self.dataSectList = []
        self.content = []
        self.contentBAK = []
        self.contentTemp = []
        self.bkgDataF = []
        self.refType = 1

        self.histDir = ''
        self.histFile = ''
        self.histFileLoaded = False

        wx.Panel.__init__(self, parent)
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        fgSizerMain = wx.FlexGridSizer(3, 1, 0, 0)
        fgSizerMain.SetFlexibleDirection(wx.BOTH)
        fgSizerMain.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        fgSizerSub1 = wx.FlexGridSizer(3, 3, 0, 0)
        fgSizerSub1.SetFlexibleDirection(wx.BOTH)
        fgSizerSub1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.dmText = wx.StaticText(
            self, wx.ID_ANY, u"Ref Type;Min d;Precision", wx.DefaultPosition, wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.dmInput = wx.TextCtrl(
            self, wx.ID_ANY, u"1;0.7;0", wx.DefaultPosition, wx.DefaultSize)
        self.topasInsDirButton = wx.Button(
            self, wx.ID_ANY, u"Topas Installation Directory", wx.DefaultPosition, wx.DefaultSize, 0)
        self.topasInsDirButton.Bind(wx.EVT_BUTTON, self.locateTopas)

        self.topasInpButton = wx.Button(
            self, wx.ID_ANY, u"Topas Input File", wx.DefaultPosition, wx.DefaultSize, 0)
        self.topasInpButton.Bind(wx.EVT_BUTTON, self.locateInp)

        self.extractButton = wx.Button(self, wx.ID_ANY, u"Extract Profile",
                                       wx.DefaultPosition, wx.DefaultSize, 0)
        self.extractButton.Bind(wx.EVT_BUTTON, self.extractProfile)

        self.checkSetupButton = wx.Button(
            self, wx.ID_ANY, u"Check Set-up", wx.DefaultPosition, wx.DefaultSize, 0)
        self.checkSetupButton.Bind(wx.EVT_BUTTON, self.checkSetup)

        self.exitButton = wx.Button(self, wx.ID_ANY, u"Clean up",
                                    wx.DefaultPosition, wx.DefaultSize, 0)
        self.exitButton.Bind(wx.EVT_BUTTON, self.cleanExit)

        self.loadHistButton = wx.Button(self, wx.ID_ANY, u"Load history",
                                    wx.DefaultPosition, wx.DefaultSize, 0)
        self.loadHistButton.Bind(wx.EVT_BUTTON, self.read_hist)

        self.abortButton = wx.Button(self, wx.ID_ANY, u"Abort",
                                    wx.DefaultPosition, wx.DefaultSize, 0)
        self.abortButton.Bind(wx.EVT_BUTTON, self.OnStop)

        fgSizerSub1.AddMany([(self.dmText, 1, wx.EXPAND | wx.TOP, 4),
                             (self.topasInsDirButton, 1, wx.EXPAND),
                             (self.topasInpButton, 1, wx.EXPAND),
                             (self.dmInput, 1, wx.EXPAND),
                             (self.extractButton, 1, wx.EXPAND),
                             (self.checkSetupButton, 1, wx.EXPAND),
                             (self.loadHistButton, 1, wx.EXPAND),
                             (self.abortButton, 1, wx.EXPAND),
                             (self.exitButton, 1, wx.EXPAND)])

        # Make rows and columns growable.
        fgSizerSub1.AddGrowableRow(0, 1)
        fgSizerSub1.AddGrowableRow(1, 1)
        fgSizerSub1.AddGrowableRow(2, 1)
        fgSizerSub1.AddGrowableCol(0, 1)
        fgSizerSub1.AddGrowableCol(1, 1)
        fgSizerSub1.AddGrowableCol(2, 1)

        fgSizerSub2 = wx.FlexGridSizer(2, 2, 0, 0)
        fgSizerSub2.SetFlexibleDirection(wx.BOTH)
        fgSizerSub2.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.sysOutText = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                      wx.DefaultSize, wx.TE_MULTILINE |
                                      wx.TE_READONLY | wx.TE_WORDWRAP)
        self.sysOutText.Bind(wx.EVT_CHAR, self.OnSelectAll)
        fgSizerSub2.AddMany([(self.sysOutText, 1, wx.EXPAND)])
        fgSizerSub2.AddGrowableRow(0, 1)
        fgSizerSub2.AddGrowableCol(0, 1)

        fgSizerMain.AddMany([(fgSizerSub1, 1, wx.EXPAND, 5),
                             (fgSizerSub2, 1, wx.EXPAND, 5)])

        fgSizerMain.AddGrowableRow(1, 1)
        fgSizerMain.AddGrowableCol(0, 1)

        self.SetSizer(fgSizerMain)
        self.Layout()

        self.Centre(wx.BOTH)

        EVT_RESULT(self,self.OnResult)

        self.profile_worker = None

    def OnStop(self, event):
        if self.profile_worker:
            self.profile_worker.abort()
            print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!!!!!!!Profile execution aborted!!!!!!!")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
            self.profileOut = False
            self.profile_worker = None

    def OnResult(self, event):
        if event.data is None:
            self.profileOut = False
            self.profile_worker = None
        else:
            self.profileOut = True

    # Locate the topas executable.
    def locateTopas(self, event):
        dialog = wx.DirDialog(self, 'Locate Topas executable', '',
                              style=wx.DD_DEFAULT_STYLE)
        try:
            if dialog.ShowModal() == wx.ID_CANCEL:
                return
            sys.stdout = self.sysOutText
            self.topasDir = dialog.GetPath()
            if self.topasDir.isspace() or not self.topasDir:
                self.topasDir = os.path.join("c:\\Topas\\")
            self.topasExe = os.path.join(self.topasDir, "tc.exe")
            if os.path.isfile(self.topasExe):
                self.topasDirSpec = True
                print("\n================= Topas installation " +
                      "directory specified ================\n")
                print(self.topasDir, "\n")
                print("================= Topas installation directory specified ================\n")
            else:
                print("\n=============== Topas not found in the " +
                      "directory specified ==============\n")
                print(self.topasDir, "\n")
                print("=============== Topas not found in the directory specified ==============\n")
                return
        except Exception:
            wx.LogError('Failed to open directory!')
            raise
        finally:
            dialog.Destroy()

    # Locate the topas input file.
    def locateInp(self, event):
        filedialog = wx.FileDialog(self, "Open Topas Input File",
                                   wildcard="inp files (*.inp)|*.inp",
                                   style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        try:
            if filedialog.ShowModal() == wx.ID_CANCEL:
                return
            sys.stdout = self.sysOutText
            self.stemName = filedialog.GetFilename().split('.')[0]
            self.topasInpDir = filedialog.GetDirectory()
            self.topasInp = os.path.join(filedialog.GetDirectory(),
                                         filedialog.GetFilename())
            self.topasInpSpec = True
            print("\n===================== Topas input file specified ====================\n")
            print(os.path.join(filedialog.GetDirectory(),
                               filedialog.GetFilename()), "\n")
            print("===================== Topas input file specified ====================\n")
        except Exception:
            wx.LogError('Failed to open topas input file!')
            raise
        finally:
            filedialog.Destroy()

    def read_hist(self, event):
        filedialog = wx.FileDialog(self, "Open history File",
                                   wildcard="hist files (*.hist)|*.hist",
                                   style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        try:
            if filedialog.ShowModal() == wx.ID_CANCEL:
                return
            sys.stdout = self.sysOutText
            self.histDir = filedialog.GetDirectory()
            self.histFile = os.path.join(filedialog.GetDirectory(),
                                         filedialog.GetFilename())
            self.histFileLoaded = True
            print("\n===================== History file specified ====================\n")
            print(os.path.join(filedialog.GetDirectory(),
                               filedialog.GetFilename()), "\n")
            print("===================== History file specified ====================\n")

            hist_file_open = open(self.histFile, "r")
            hist_file_lines = hist_file_open.readlines()
            hist_file_open.close()
            last_pos = 1
            while True:
                if "Time stamp:" in hist_file_lines[-last_pos]:
                    break
                else:
                    last_pos += 1
            last_pos = len(hist_file_lines) - last_pos

            self.topasExe = hist_file_lines[last_pos + 2].split("executable:")[1].strip()

            self.topasDirSpec = True
            print("\n================= Topas executable specified ================\n")
            print(self.topasExe, "\n")
            print("================= Topas executable specified ================\n")

            self.topasInpDir = hist_file_lines[last_pos + 3].split("directory:")[1].strip()
            self.topasInp = os.path.join(self.topasInpDir, 
                hist_file_lines[last_pos + 4].split("file:")[1].strip())
            self.stemName = hist_file_lines[last_pos + 4].split("file:")[1].strip().split(".")[0]

            self.topasInpSpec = True
            print("\n===================== Topas input file specified ====================\n")
            print(self.topasInp, "\n")
            print("===================== Topas input file specified ====================\n")

            self.dmInput.SetValue(hist_file_lines[last_pos + 5].split("box:")[1].strip())
        except Exception:
            wx.LogError('Failed to open history file!')
            raise
        finally:
            filedialog.Destroy()
        
    # Extract profiles.
    def extractProfile(self, event):
        sys.stdout = self.sysOutText
        try:
            if not self.profile_worker and self.topasDirSpec and self.topasInpSpec:
                self.profile_worker = profile_thread(self, self.dmInput, self.profileOut, 
                    self.dataSectList, self.content, self.contentBAK, self.contentTemp, 
                    self.bkgDataF, self.topasDirSpec, self.topasInpSpec,
                    self.refType, self.topasInpDir, self.stemName, self.topasExe)
                self.profileOut = self.profile_worker.profileOut
            else:
                if not self.topasDirSpec or not self.topasInpSpec:
                    wx.LogError('Specify the Topas executable and input file first!')
                    return
        except Exception:
            wx.LogError('Exception caught! Refer to the terminal for information!')
            self.profile_worker = None

    # Use the original Pawley intensities and the output profiles data to test
    # whether the setup is OK. If everything runs smoothly, we should get exactly
    # the same result as what we could get within Topas.
    def checkSetup(self, event):
        if self.profile_worker and self.profileOut:
            print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Proceeding to " +
                  "test the setup !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
            print("The first data section will be taken as the test example.\n")
            print("The Pawley intensity will be initialized to 1 in Topas.\n")
            print("If the setup is OK, the GREEN DIFFERENCE CURVE SHOWN IN THE \n")
            print("BOTTOM PANEL SHOULD BE CLOSE TO FLAT, ALLOWING ROUND UP ERRORS.\n")
            print("PLEASE CHECK IT!\n")

            # Take the first data section as the test case.
            expFileName = self.profile_worker.content[self.profile_worker.dataSectList[0].startP]
            if "\"" in expFileName:
                expFileName = expFileName.split("\"")[1]
            elif "'" in expFileName:
                expFileName = expFileName.split("'")[1]
            else:
                expFileName = expFileName.split()[1]

            # Read in the experiment data file.
            expFile = open(os.path.join(self.profile_worker.topasInpDir, expFileName), "r")
            expData = []
            line = expFile.readline()
            if "'" not in line:
                expData.append(line.split()[:2])
            while line:
                line = expFile.readline()
                if line and "'" not in line:
                    expData.append(line.split()[:2])
            expDataF = [[float(y) for y in x] for x in expData]
            sDataP = self.profile_worker.bkgDataF[0][0][0]
            eDataP = self.profile_worker.bkgDataF[0][-1][0]
            expDataFX = [x[0] for x in expDataF]
            expDataSPTemp = min(expDataFX, key=lambda x:abs(x-sDataP))
            expDataEPTemp = min(expDataFX, key=lambda x:abs(x-eDataP))
            expDataSP = expDataFX.index(expDataSPTemp)
            expDataEP = expDataFX.index(expDataEPTemp)
            expDataUse = expDataF[expDataSP:expDataEP + 1]

            # Read in the Pawley intensities and the corresponding multiplicity for testing.
            PawleyInt = []
            for i in range(len(self.profile_worker.dataSectList[0].hklIsPos)):
                PawleyInt.append([])
                for j in range(self.profile_worker.dataSectList[0].hklEP[i] -
                               self.profile_worker.dataSectList[0].hklSP[i] + 1):
                    multiTemp = float(self.profile_worker.contentBAK[self.profile_worker.dataSectList[0].hklSP[i] + j].split()[3])
                    PawleyInt[i].append(float(self.profile_worker.contentBAK[self.profile_worker.dataSectList[0].hklSP[i] +
                      j].split("@")[1].split("`")[0]))

            # Read in the tabulated profiles data.
            hklFileTest = open(os.path.join(self.profile_worker.topasInpDir, self.profile_worker.stemName + "_check_hkl_temp1"), "r")
            line = hklFileTest.readline()
            line = hklFileTest.readline()
            scale = []
            hklProfData = []
            hklProfSec = 0
            while line:
                if "Phase-" in line:
                    hklProfSec += 1
                    hklProfData.append([])
                    line = hklFileTest.readline()
                    line = hklFileTest.readline()
                    scale.append(float(line.split("=")[1]))
                    line = hklFileTest.readline()
                    hklNum = int(line.split("=")[1])
                line = hklFileTest.readline()
                for i in range(hklNum):
                    line = hklFileTest.readline()
                    hklProfData[hklProfSec - 1].append(line.split()[5:])
                hklNum = 0
                line = hklFileTest.readline()
            hklFileTest.close()

            hklProfDataF = [[[float(z) for z in y] for y in x] for x in hklProfData]
            for i in range(len(hklProfDataF)):
                for j in range(len(hklProfDataF[i])):
                    for k in range(len(hklProfDataF[i][j]) - 2):
                        hklProfDataF[i][j][k + 2] *= PawleyInt[i][j]
                        hklProfDataF[i][j][k + 2] *= scale[i]

            calc = []
            for i in range(len(expDataUse)):
                calc.append(copy.copy(expDataUse[i]))
            for i in range(len(calc)):
                calc[i][1] = 0
            for i in range(len(expDataUse)):
                for j in range(len(scale)):
                    for item in hklProfDataF[j]:
                        if (i + 1) >= item[0] and (i + 1) <= item[1]:
                            calc[i][1] += item[i - int(item[0]) + 3]

            calcX = []
            calcY = []
            for item in calc:
                calcX.append(item[0])
                calcY.append(item[1])
            checkX = []
            checkY = []
            checkFile = open(os.path.join(self.profile_worker.topasInpDir, "x_ycheck_1.dat"), "r")
            line = checkFile.readline()
            checkData = []
            checkData.append(line.split())
            while line:
                line = checkFile.readline()
                if line:
                    checkData.append(line.split())
            checkFile.close()
            checkDataF = [[float(y) for y in x] for x in checkData]
            for item in checkDataF:
                checkX.append(item[0])
                checkY.append(item[1])
            expX = []
            expY = []
            for item in expDataUse:
                expX.append(item[0])
                expY.append(item[1])

            for i in range(len(checkY)):
                checkY[i] -= self.profile_worker.bkgDataF[0][i][1]

            # Write the checking result.
            testFile = open(os.path.join(self.profile_worker.topasInpDir, "calc_check.dat"), "w")
            testFile.write("X\tY_Calc\tY_Init\tDiff_Y_Calc_Init\n")
            for i in range(len(calc)):
                testFile.write("{0:15.6F}{1:15.6F}{2:15.6F}{3:15.6F}\n"
                               .format(calc[i][0], calc[i][1], checkY[i],
                                       calc[i][1] - checkY[i]))
            testFile.close()

            diff2 = []
            for i in range(len(expDataUse)):
                diff2.append(calcY[i] - checkY[i] + min(checkY) -
                             (max(checkY) - min(checkY)) * 0.05)

            fig, axs = plt.subplots(1, 1)
            axs.plot(checkX, checkY, 'r', label='Initial Topas Pawley/Reitveld Run')
            axs.plot(calcX, calcY, 'b', label='External Check Run')
            axs.plot(calcX, diff2, 'g', label='Difference')
            axs.legend(loc='upper right', shadow=True, fontsize='x-large')
            axs.set_xlabel(r'X (TOF or Q or $2\theta$)')
            axs.set_ylabel('Int. (a. u.)')
            axs.set_title('External Check Run & Initial Topas Pawley/Rietveld Run')
            fig.tight_layout()
            axs.title.set_fontsize(15)
            axs.title.set_fontweight('bold')
            axs.xaxis.label.set_fontsize(17)
            axs.yaxis.label.set_fontweight('bold')
            axs.yaxis.label.set_fontsize(17)
            axs.xaxis.label.set_fontweight('bold')
            for itemitem in axs.get_xticklabels():
                itemitem.set_fontsize(13)
            for itemitem in axs.get_yticklabels():
                itemitem.set_fontsize(13)

            plt.show()

            print("The setup-checking data is also output to 'calc_check.dat' file.\n")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! " +
                  "Setup-checking done " +
                  "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
        else:
            wx.LogError('Extract the profile first!!!')
            return

    # Enable Ctrl+A to select all text in the output text box.
    def OnSelectAll(self, event):
        keyInput = event.GetKeyCode()
        if keyInput == 1:  # 1 stands for 'ctrl+a'
            self.sysOutText.SelectAll()
            pass
        event.Skip()

    # For cleaning up.
    def cleanExit(self, event):
        if self.profile_worker and self.profileOut:
            if self.profile_worker.topasDirSpec and self.profile_worker.topasInpSpec and \
                self.profile_worker.profileOut:
                dlg = wx.MessageDialog(None, "Do you want to clean up unnecessary files??",
                                       'Confirmation', wx.YES_NO | wx.ICON_QUESTION)
                result = dlg.ShowModal()
                if result == wx.ID_YES:
                    print("======================== Cleaning up ===========================\n")
                    if os.path.exists(os.path.join(self.topasInpDir, "bkg_extract.inp")):
                        os.remove(os.path.join(self.topasInpDir, "bkg_extract.inp"))
                    if os.path.exists(os.path.join(self.topasInpDir, "bkg_extract.out")):
                        os.remove(os.path.join(self.topasInpDir, "bkg_extract.out"))
                    if os.path.exists(os.path.join(self.topasInpDir, "hkls_temp.inp")):
                        os.remove(os.path.join(self.topasInpDir, "hkls_temp.inp"))
                    if os.path.exists(os.path.join(self.topasInpDir, "hkls_temp.out")):
                        os.remove(os.path.join(self.topasInpDir, "hkls_temp.out"))
                    if os.path.exists(os.path.join(self.topasInpDir, "init_check.inp")):
                        os.remove(os.path.join(self.topasInpDir, "init_check.inp"))
                    if os.path.exists(os.path.join(self.topasInpDir, "init_check.out")):
                        os.remove(os.path.join(self.topasInpDir, "init_check.out"))
                    if os.path.exists(os.path.join(self.topasInpDir, "x_ycalc.dat")):
                        os.remove(os.path.join(self.topasInpDir, "x_ycalc.dat"))
                    for fl in glob.glob(os.path.join(self.topasInpDir,"x_ycheck_*.dat")):
                        os.remove(fl)
                    for fl in glob.glob(os.path.join(self.topasInpDir,"*_check_hkl_temp*")):
                        os.remove(fl)
                    if (self.refType==1):
                        if os.path.exists(os.path.join(self.topasInpDir, "temptemptemp.inp")):
                            os.remove(os.path.join(self.topasInpDir, "temptemptemp.inp"))
                        if os.path.exists(os.path.join(self.topasInpDir, "temptemptemp.out")):
                            os.remove(os.path.join(self.topasInpDir, "temptemptemp.out"))
                    print("====================== Cleaning up done =========================\n")
                    self.profile_worker.profileOut = False
                    self.profileOut = False
                    self.profile_worker = None
            else:
                wx.LogError('Nothing to clean yet!!!')
        else:
            wx.LogError('Nothing to clean yet!!!')

# Second tab for generating resolution matrix for constant
# wavelength data (X-ray or neutron).
class PageRMCW(wx.Panel):
    def __init__(self, parent):
        # Initializing variables.
        self.topasDir = ''
        self.stemName = ''
        self.topasExe = ''
        self.topasInp = ''
        self.topasInpDir = ''
        self.topasDirSpec = False
        self.topasInpSpec = False
        self.resMatDone = False
        self.dataSectList = []
        self.content = []

        wx.Panel.__init__(self, parent)
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        fgSizerMain = wx.FlexGridSizer(2, 1, 0, 0)
        fgSizerMain.SetFlexibleDirection(wx.BOTH)
        fgSizerMain.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        fgSizerSub1 = wx.FlexGridSizer(3, 3, 0, 0)
        fgSizerSub1.SetFlexibleDirection(wx.BOTH)
        fgSizerSub1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        fgSizerSub11 = wx.FlexGridSizer(1, 2, 0, 0)
        fgSizerSub11.SetFlexibleDirection(wx.BOTH)
        fgSizerSub11.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        fgSizerSub12 = wx.FlexGridSizer(1, 2, 0, 0)
        fgSizerSub12.SetFlexibleDirection(wx.BOTH)
        fgSizerSub12.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        fgSizerSub13 = wx.FlexGridSizer(1, 2, 0, 0)
        fgSizerSub13.SetFlexibleDirection(wx.BOTH)
        fgSizerSub13.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.l1 = wx.StaticText(
            self, wx.ID_ANY, u"Q_Start", wx.DefaultPosition, wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.i1 = wx.TextCtrl(
            self, wx.ID_ANY, u"0.01", wx.DefaultPosition, wx.DefaultSize)

        self.l2 = wx.StaticText(
            self, wx.ID_ANY, u"Q_Step", wx.DefaultPosition, wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.i2 = wx.TextCtrl(
            self, wx.ID_ANY, u"0.01", wx.DefaultPosition, wx.DefaultSize)

        self.l3 = wx.StaticText(
            self, wx.ID_ANY, u"Q_End", wx.DefaultPosition, wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.i3 = wx.TextCtrl(
            self, wx.ID_ANY, u"30.0", wx.DefaultPosition, wx.DefaultSize)

        fgSizerSub11.AddMany([(self.l1, 1, wx.EXPAND | wx.TOP, 4),
                              (self.i1, 1, wx.EXPAND)])

        fgSizerSub11.AddGrowableRow(0, 1)
        fgSizerSub11.AddGrowableCol(0, 1)
        fgSizerSub11.AddGrowableCol(1, 1)

        fgSizerSub12.AddMany([(self.l2, 1, wx.EXPAND | wx.TOP, 4),
                              (self.i2, 1, wx.EXPAND)])

        fgSizerSub12.AddGrowableRow(0, 1)
        fgSizerSub12.AddGrowableCol(0, 1)
        fgSizerSub12.AddGrowableCol(1, 1)

        fgSizerSub13.AddMany([(self.l3, 1, wx.EXPAND | wx.TOP, 4),
                              (self.i3, 1, wx.EXPAND)])

        fgSizerSub13.AddGrowableRow(0, 1)
        fgSizerSub13.AddGrowableCol(0, 1)
        fgSizerSub13.AddGrowableCol(1, 1)

        self.topasInst = wx.Button(self, wx.ID_ANY, u"Topas Installation Directory",
                                    wx.DefaultPosition, wx.DefaultSize, 0)
        self.topasInst.Bind(wx.EVT_BUTTON, self.locateTopas)
        self.topasInp = wx.Button(self, wx.ID_ANY, u"Topas Input File",
                                    wx.DefaultPosition, wx.DefaultSize, 0)
        self.topasInp.Bind(wx.EVT_BUTTON, self.locateInp)
        self.matrixButton = wx.Button(self, wx.ID_ANY, u"Matrix Prep",
                                    wx.DefaultPosition, wx.DefaultSize, 0)
        self.matrixButton.Bind(wx.EVT_BUTTON, self.resMatrixPrep)

        self.exitButton = wx.Button(self, wx.ID_ANY, u"Clean up",
                                    wx.DefaultPosition, wx.DefaultSize, 0)
        self.exitButton.Bind(wx.EVT_BUTTON, self.cleanExit)

        self.abortButton = wx.Button(self, wx.ID_ANY, u"Abort",
                                    wx.DefaultPosition, wx.DefaultSize, 0)
        self.abortButton.Bind(wx.EVT_BUTTON, self.OnStop)

        self.loadHistButton = wx.Button(self, wx.ID_ANY, u"Load history",
                                    wx.DefaultPosition, wx.DefaultSize, 0)
        self.loadHistButton.Bind(wx.EVT_BUTTON, self.read_hist)

        fgSizerSub1.AddMany([(fgSizerSub11, 1, wx.EXPAND),
                             (fgSizerSub12, 1, wx.EXPAND),
                             (fgSizerSub13, 1, wx.EXPAND),
                             (self.topasInst, 1, wx.EXPAND),
                             (self.topasInp, 1, wx.EXPAND),
                             (self.matrixButton, 1, wx.EXPAND),
                             (self.loadHistButton, 1, wx.EXPAND),
                             (self.abortButton, 1, wx.EXPAND),
                             (self.exitButton, 1, wx.EXPAND)])
        fgSizerSub1.AddGrowableRow(0, 1)
        fgSizerSub1.AddGrowableRow(1, 1)
        fgSizerSub1.AddGrowableRow(2, 1)
        fgSizerSub1.AddGrowableCol(0, 1)
        fgSizerSub1.AddGrowableCol(1, 1)
        fgSizerSub1.AddGrowableCol(2, 1)

        fgSizerSub2 = wx.FlexGridSizer(2, 2, 0, 0)
        fgSizerSub2.SetFlexibleDirection(wx.BOTH)
        fgSizerSub2.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.sysOutText = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                      wx.DefaultSize, wx.TE_MULTILINE |
                                      wx.TE_READONLY | wx.TE_WORDWRAP)
        self.sysOutText.Bind(wx.EVT_CHAR, self.OnSelectAll)
        fgSizerSub2.AddMany([(self.sysOutText, 1, wx.EXPAND)])
        fgSizerSub2.AddGrowableRow(0, 1)
        fgSizerSub2.AddGrowableCol(0, 1)

        fgSizerMain.AddMany([(fgSizerSub1, 1, wx.EXPAND, 5),
                             (fgSizerSub2, 1, wx.EXPAND, 5)])

        fgSizerMain.AddGrowableRow(1, 1)
        fgSizerMain.AddGrowableCol(0, 1)

        self.SetSizer(fgSizerMain)
        self.Layout()

        self.Centre(wx.BOTH)

        # Set up event handler for any worker thread results
        EVT_RESULT(self, self.OnResult)

        # And indicate we don't have a worker thread yet
        self.cw_rm_worker = None

    def OnStop(self, event):
        if self.cw_rm_worker:
            self.cw_rm_worker.abort()
            print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!!!!!!!Resolution matrix generation aborted!!!!!!!")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
            self.resMatDone = False
            self.cw_rm_worker = None

    def OnResult(self, event):
        if event.data is None:
            self.resMatDone = False
            self.cw_rm_worker = None
        else:
            self.resMatDone = True

    def locateTopas(self, event):
        dialog = wx.DirDialog(self, 'Locate Topas executable', '',
                              style=wx.DD_DEFAULT_STYLE)
        try:
            if dialog.ShowModal() == wx.ID_CANCEL:
                return
            sys.stdout = self.sysOutText
            self.topasDir = dialog.GetPath()
            if self.topasDir.isspace() or not self.topasDir:
                self.topasDir = os.path.join("c:\\Topas\\")
            self.topasExe = os.path.join(self.topasDir, "tc.exe")
            if os.path.isfile(self.topasExe):
                self.topasDirSpec = True
                print("\n================= Topas installation " +
                      "directory specified ================\n")
                print(self.topasDir, "\n")
                print("================= Topas installation directory specified ================\n")
            else:
                print("\n=============== Topas not found in the " +
                      "directory specified ==============\n")
                print(self.topasDir, "\n")
                print("=============== Topas not found in the directory specified ==============\n")
                return
        except Exception:
            wx.LogError('Failed to open directory!')
            raise
        finally:
            dialog.Destroy()

    def locateInp(self, event):
        filedialog = wx.FileDialog(self, "Open Topas Input File",
                                   wildcard="inp files (*.inp)|*.inp",
                                   style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        try:
            if filedialog.ShowModal() == wx.ID_CANCEL:
                return
            sys.stdout = self.sysOutText
            self.stemName = filedialog.GetFilename().split('.')[0]
            self.topasInpDir = os.path.join(filedialog.GetDirectory())
            self.topasInp = os.path.join(filedialog.GetDirectory(),
                                         filedialog.GetFilename())
            self.topasInpSpec = True
            print("\n===================== Topas input file specified ====================\n")
            print(os.path.join(filedialog.GetDirectory(),
                               filedialog.GetFilename()), "\n")
            print("===================== Topas input file specified ====================\n\n")
        except Exception:
            wx.LogError('Failed to open topas input file!')
            raise
        finally:
            filedialog.Destroy()

    def read_hist(self, event):
        filedialog = wx.FileDialog(self, "Open history File",
                                   wildcard="hist files (*.hist)|*.hist",
                                   style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        try:
            if filedialog.ShowModal() == wx.ID_CANCEL:
                return
            sys.stdout = self.sysOutText
            self.histDir = filedialog.GetDirectory()
            self.histFile = os.path.join(filedialog.GetDirectory(),
                                         filedialog.GetFilename())
            self.histFileLoaded = True
            print("\n===================== History file specified ====================\n")
            print(os.path.join(filedialog.GetDirectory(),
                               filedialog.GetFilename()), "\n")
            print("===================== History file specified ====================\n")

            hist_file_open = open(self.histFile, "r")
            hist_file_lines = hist_file_open.readlines()
            hist_file_open.close()
            last_pos = 1
            while True:
                if "Time stamp:" in hist_file_lines[-last_pos]:
                    break
                else:
                    last_pos += 1
            last_pos = len(hist_file_lines) - last_pos

            self.topasExe = hist_file_lines[last_pos + 2].split("executable:")[1].strip()

            self.topasDirSpec = True
            print("\n================= Topas executable specified ================\n")
            print(self.topasExe, "\n")
            print("================= Topas executable specified ================\n")

            self.topasInpDir = hist_file_lines[last_pos + 3].split("directory:")[1].strip()
            self.topasInp = os.path.join(self.topasInpDir, 
                hist_file_lines[last_pos + 4].split("file:")[1].strip())
            self.stemName = hist_file_lines[last_pos + 4].split("file:")[1].strip().split(".")[0]

            self.topasInpSpec = True
            print("\n===================== Topas input file specified ====================\n")
            print(self.topasInp, "\n")
            print("===================== Topas input file specified ====================\n")

            self.i1.SetValue(hist_file_lines[last_pos + 5].split("box-1:")[1].strip())
            self.i2.SetValue(hist_file_lines[last_pos + 6].split("box-2:")[1].strip())
            self.i3.SetValue(hist_file_lines[last_pos + 7].split("box-3:")[1].strip())
        except Exception:
            wx.LogError('Failed to open history file!')
            raise
        finally:
            filedialog.Destroy()

    # Generate the resolution matrix.
    def resMatrixPrep(self, event):
        sys.stdout = self.sysOutText
        try:
            if not self.cw_rm_worker and self.topasDirSpec and self.topasInpSpec:
                self.cw_rm_worker = cw_rm_thread(self, self.i1, self.i2, self.i3,
                    self.resMatDone, self.dataSectList, self.content,
                    self.topasDirSpec, self.topasInpSpec, self.topasExe, 
                    self.topasInp, self.topasInpDir)
                self.resMatDone = self.cw_rm_worker.resMatDone
            else:
                if not self.topasDirSpec or not self.topasInpSpec:
                    wx.LogError('Please specify Topas executable and input file first!')
                    return
        except Exception:
            wx.LogError('Exception caught! Refer to the terminal for information!')
            self.cw_rm_worker = None

    def OnSelectAll(self, event):
        keyInput = event.GetKeyCode()
        if keyInput == 1:  # 1 stands for 'ctrl+a'
            self.doc_text.SelectAll()
            pass
        event.Skip()

    def cleanExit(self, event):
        if self.cw_rm_worker and self.resMatDone:
            if self.topasDirSpec and self.topasInpSpec:
                dlg = wx.MessageDialog(None, "Do you want to clean up unnecessary files??",
                                       'Confirmation', wx.YES_NO | wx.ICON_QUESTION)
                result = dlg.ShowModal()
                if result == wx.ID_YES:
                    print("======================== Cleaning up ==========================\n")
                    if os.path.exists(os.path.join(self.topasInpDir, "bkg_extract_temp.inp")):
                        os.remove(os.path.join(self.topasInpDir, "bkg_extract_temp.inp"))
                    if os.path.exists(os.path.join(self.topasInpDir, "bkg_extract_temp.out")):
                        os.remove(os.path.join(self.topasInpDir, "bkg_extract_temp.out"))
                    if os.path.exists(os.path.join(self.topasInpDir, "res_mat_prep_temp.inp")):
                        os.remove(os.path.join(self.topasInpDir, "res_mat_prep_temp.inp"))
                    if os.path.exists(os.path.join(self.topasInpDir, "res_mat_prep_temp.out")):
                        os.remove(os.path.join(self.topasInpDir, "res_mat_prep_temp.out"))
                    if os.path.exists(os.path.join(self.topasInpDir, "temptemp.inp")):
                        os.remove(os.path.join(self.topasInpDir, "temptemp.inp"))
                    if os.path.exists(os.path.join(self.topasInpDir, "temptemp.out")):
                        os.remove(os.path.join(self.topasInpDir, "temptemp.out"))
                    for fl in glob.glob(os.path.join(self.topasInpDir,"q_ycalc_resmat_cw*.dat")):
                        os.remove(fl)
                    for fl in glob.glob(os.path.join(self.topasInpDir,"dataTemp*.xye")):
                        os.remove(fl)
                    self.resMatDone = False
                    self.cw_rm_worker = None
                    print("===================== Cleaning up done =========================\n")
            else:
                wx.LogError('Nothing to clean yet!!!')
                return
        else:
            wx.LogError('Nothing to clean yet!!!')
            return

# Third tab for generating the resolution matrix for time-of-flight neutron data.
class PageRMTOF(wx.Panel):
    def __init__(self, parent):
        # Initializing variables.
        self.topasDir = ''
        self.stemName = ''
        self.topasExe = ''
        self.topasInp = ''
        self.topasInpDir = ''
        self.topasDirSpec = False
        self.topasInpSpec = False
        self.resMatTOFDone = False
        self.dataSectList = []
        self.content = []

        wx.Panel.__init__(self, parent)
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        fgSizerMain = wx.FlexGridSizer(2, 1, 0, 0)
        fgSizerMain.SetFlexibleDirection(wx.BOTH)
        fgSizerMain.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        fgSizerSub1 = wx.FlexGridSizer(3, 3, 0, 0)
        fgSizerSub1.SetFlexibleDirection(wx.BOTH)
        fgSizerSub1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        fgSizerSub11 = wx.FlexGridSizer(1, 2, 0, 0)
        fgSizerSub11.SetFlexibleDirection(wx.BOTH)
        fgSizerSub11.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        fgSizerSub12 = wx.FlexGridSizer(1, 2, 0, 0)
        fgSizerSub12.SetFlexibleDirection(wx.BOTH)
        fgSizerSub12.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        fgSizerSub13 = wx.FlexGridSizer(1, 2, 0, 0)
        fgSizerSub13.SetFlexibleDirection(wx.BOTH)
        fgSizerSub13.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.l1 = wx.StaticText(
            self, wx.ID_ANY, u"Q_Grid", wx.DefaultPosition, wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.i1 = wx.TextCtrl(self, wx.ID_ANY, u"0.01,0.01,30.0,0",
                              wx.DefaultPosition, wx.DefaultSize)

        self.l11 = wx.StaticText(self, wx.ID_ANY, u"Data_Sections",
                                 wx.DefaultPosition, wx.DefaultSize,
                                 wx.ALIGN_CENTRE_HORIZONTAL)
        self.i11 = wx.TextCtrl(
            self, wx.ID_ANY, u"1;2;3;4;5", wx.DefaultPosition, wx.DefaultSize)

        self.l2 = wx.StaticText(
            self, wx.ID_ANY, u"TOF_Paras", wx.DefaultPosition, wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.i2 = wx.TextCtrl(self, wx.ID_ANY, u"7391.35,-2.16,1.88,7391.35",
                              wx.DefaultPosition, wx.DefaultSize)

        fgSizerSub11.AddMany([(self.l1, 1, wx.EXPAND | wx.TOP, 4),
                              (self.i1, 1, wx.EXPAND)])
        fgSizerSub11.AddGrowableRow(0, 1)
        fgSizerSub11.AddGrowableCol(0, 1)
        fgSizerSub11.AddGrowableCol(1, 1)

        fgSizerSub12.AddMany([(self.l11, 1, wx.EXPAND | wx.TOP, 4),
                              (self.i11, 1, wx.EXPAND)])
        fgSizerSub12.AddGrowableRow(0, 1)
        fgSizerSub12.AddGrowableCol(0, 1)
        fgSizerSub12.AddGrowableCol(1, 1)

        fgSizerSub13.AddMany([(self.l2, 1, wx.EXPAND | wx.TOP, 4),
                              (self.i2, 1, wx.EXPAND)])
        fgSizerSub13.AddGrowableRow(0, 1)
        fgSizerSub13.AddGrowableCol(0, 1)
        fgSizerSub13.AddGrowableCol(1, 1)

        self.topasInst = wx.Button(self, wx.ID_ANY,
                                   u"Topas Installation Directory",
                                   wx.DefaultPosition, wx.DefaultSize, 0)
        self.topasInst.Bind(wx.EVT_BUTTON, self.locateTopas)
        self.topasInp = wx.Button(self, wx.ID_ANY, u"Topas Input File",
                                  wx.DefaultPosition, wx.DefaultSize, 0)
        self.topasInp.Bind(wx.EVT_BUTTON, self.locateInp)
        self.matrixButton = wx.Button(self, wx.ID_ANY, u"Matrix Prep",
                                      wx.DefaultPosition, wx.DefaultSize,
                                      0)
        self.matrixButton.Bind(wx.EVT_BUTTON, self.resMatrixPrep)

        self.exitButton = wx.Button(self, wx.ID_ANY, u"Clean up",
                                    wx.DefaultPosition, wx.DefaultSize, 0)
        self.exitButton.Bind(wx.EVT_BUTTON, self.cleanExit)

        self.loadHistButton = wx.Button(self, wx.ID_ANY,
                                        u"Load history",
                                        wx.DefaultPosition,
                                        wx.DefaultSize, 0)
        self.loadHistButton.Bind(wx.EVT_BUTTON, self.read_hist)

        self.abortButton = wx.Button(self, wx.ID_ANY,
                                     u"Abort",
                                     wx.DefaultPosition,
                                     wx.DefaultSize, 0)
        self.abortButton.Bind(wx.EVT_BUTTON, self.OnStop)

        fgSizerSub1.AddMany([(fgSizerSub11, 1, wx.EXPAND),
                             (fgSizerSub12, 1, wx.EXPAND),
                             (fgSizerSub13, 1, wx.EXPAND),
                             (self.topasInst, 1, wx.EXPAND),
                             (self.topasInp, 1, wx.EXPAND),
                             (self.matrixButton, 1, wx.EXPAND),
                             (self.loadHistButton, 1, wx.EXPAND),
                             (self.abortButton, 1, wx.EXPAND),
                             (self.exitButton, 1, wx.EXPAND)])
        fgSizerSub1.AddGrowableRow(0, 1)
        fgSizerSub1.AddGrowableRow(1, 1)
        fgSizerSub1.AddGrowableRow(2, 1)
        fgSizerSub1.AddGrowableCol(0, 1)
        fgSizerSub1.AddGrowableCol(1, 1)
        fgSizerSub1.AddGrowableCol(2, 1)

        fgSizerSub2 = wx.FlexGridSizer(1, 1, 0, 0)
        fgSizerSub2.SetFlexibleDirection(wx.BOTH)
        fgSizerSub2.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        temp_var = wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP
        self.sysOutText = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString,
                                      wx.DefaultPosition,
                                      wx.DefaultSize, temp_var)
        self.sysOutText.Bind(wx.EVT_CHAR, self.OnSelectAll)
        fgSizerSub2.AddMany([(self.sysOutText, 1, wx.EXPAND)])
        fgSizerSub2.AddGrowableRow(0, 1)
        fgSizerSub2.AddGrowableCol(0, 1)

        fgSizerMain.AddMany([(fgSizerSub1, 1, wx.EXPAND, 5),
                             (fgSizerSub2, 1, wx.EXPAND, 5)])

        fgSizerMain.AddGrowableRow(1, 1)
        fgSizerMain.AddGrowableCol(0, 1)

        self.SetSizer(fgSizerMain)
        self.Layout()

        self.Centre(wx.BOTH)

        # Set up event handler for any worker thread results
        EVT_RESULT(self, self.OnResult)

        # And indicate we don't have a worker thread yet
        self.tof_rm_worker = None

    def OnStop(self, event):
        if self.tof_rm_worker:
            self.tof_rm_worker.abort()
            print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!!!!!!!Resolution matrix generation aborted!!!!!!!")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
            self.resMatTOFDone = False
            self.tof_rm_worker = None

    def OnResult(self, event):
        if event.data is None:
            self.resMatTOFDone = False
            self.tof_rm_worker = None
        else:
            self.resMatTOFDone = True

    def locateTopas(self, event):
        dialog = wx.DirDialog(self, 'Locate Topas executable', '',
                              style=wx.DD_DEFAULT_STYLE)
        try:
            if dialog.ShowModal() == wx.ID_CANCEL:
                return
            sys.stdout = self.sysOutText
            self.topasDir = dialog.GetPath()
            if self.topasDir.isspace() or not self.topasDir:
                self.topasDir = os.path.join("c:\\Topas\\")
            self.topasExe = os.path.join(self.topasDir, "tc.exe")
            if os.path.isfile(self.topasExe):
                self.topasDirSpec = True
                print("\n================= Topas installation " +
                      "directory specified ================\n")
                print(self.topasDir, "\n")
                print("================= Topas installation directory specified ================\n")
            else:
                print("\n=============== Topas not found in the " +
                      "directory specified ==============\n")
                print(self.topasDir, "\n")
                print("=============== Topas not found in the directory specified ==============\n")
                return
        except Exception:
            wx.LogError('Failed to open directory!')
            raise
        finally:
            dialog.Destroy()

    def locateInp(self, event):
        filedialog = wx.FileDialog(self, "Open Topas Input File",
                                   wildcard="inp files (*.inp)|*.inp",
                                   style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        try:
            if filedialog.ShowModal() == wx.ID_CANCEL:
                return
            sys.stdout = self.sysOutText
            self.stemName = filedialog.GetFilename().split('.')[0]
            self.topasInpDir = os.path.join(filedialog.GetDirectory())
            self.topasInp = os.path.join(filedialog.GetDirectory(),
                                         filedialog.GetFilename())
            self.topasInpSpec = True
            print("\n===================== Topas input file specified ====================\n")
            print(os.path.join(filedialog.GetDirectory(),
                               filedialog.GetFilename()), "\n")
            print("===================== Topas input file specified ====================\n\n")
        except Exception:
            wx.LogError('Failed to open topas input file!')
            raise
        finally:
            filedialog.Destroy()

    def read_hist(self, event):
        filedialog = wx.FileDialog(self, "Open history File",
                                   wildcard="hist files (*.hist)|*.hist",
                                   style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        try:
            if filedialog.ShowModal() == wx.ID_CANCEL:
                return
            sys.stdout = self.sysOutText
            self.histDir = filedialog.GetDirectory()
            self.histFile = os.path.join(filedialog.GetDirectory(),
                                         filedialog.GetFilename())
            self.histFileLoaded = True
            print("\n===================== History file specified ====================\n")
            print(os.path.join(filedialog.GetDirectory(),
                               filedialog.GetFilename()), "\n")
            print("===================== History file specified ====================\n")

            hist_file_open = open(self.histFile, "r")
            hist_file_lines = hist_file_open.readlines()
            hist_file_open.close()
            last_pos = 1
            while True:
                if "Time stamp:" in hist_file_lines[-last_pos]:
                    break
                else:
                    last_pos += 1
            last_pos = len(hist_file_lines) - last_pos

            self.topasExe = hist_file_lines[last_pos + 2].split("executable:")[1].strip()

            self.topasDirSpec = True
            print("\n================= Topas executable specified ================\n")
            print(self.topasExe, "\n")
            print("================= Topas executable specified ================\n")

            self.topasInpDir = hist_file_lines[last_pos + 3].split("directory:")[1].strip()
            self.topasInp = os.path.join(self.topasInpDir, 
                hist_file_lines[last_pos + 4].split("file:")[1].strip())
            self.stemName = hist_file_lines[last_pos + 4].split("file:")[1].strip().split(".")[0]

            self.topasInpSpec = True
            print("\n===================== Topas input file specified ====================\n")
            print(self.topasInp, "\n")
            print("===================== Topas input file specified ====================\n")

            self.i1.SetValue(hist_file_lines[last_pos + 5].split("box-1:")[1].strip())
            self.i11.SetValue(hist_file_lines[last_pos + 6].split("box-2:")[1].strip())
            self.i2.SetValue(hist_file_lines[last_pos + 7].split("box-3:")[1].strip())
        except Exception:
            wx.LogError('Failed to open history file!')
            raise
        finally:
            filedialog.Destroy()

    def resMatrixPrep(self, event):
        sys.stdout = self.sysOutText
        try:
            if not self.tof_rm_worker and self.topasDirSpec and self.topasInpSpec:
                self.tof_rm_worker = tof_rm_thread(self, self.i1, self.i11, self.i2,
                    self.topasDirSpec, self.topasInpSpec, self.topasInp, 
                    self.content, self.dataSectList, self.topasInpDir,
                    self.topasExe, self.stemName, self.resMatTOFDone)
                self.resMatTOFDone = self.tof_rm_worker.resMatTOFDone
            else:
                if not self.topasDirSpec or not self.topasInpSpec:
                    wx.LogError('Please specify Topas executable and input file first!')
                    return
        except Exception:
            wx.LogError('Exception caught! Refer to the terminal for information!')
            self.tof_rm_worker = None

    def OnSelectAll(self, event):
        keyInput = event.GetKeyCode()
        if keyInput == 1:  # 1 stands for 'ctrl+a'
            self.doc_text.SelectAll()
            pass
        event.Skip()

    def cleanExit(self, event):
        if self.tof_rm_worker and self.resMatTOFDone:
            if self.topasDirSpec and self.topasInpSpec:
                dlg = wx.MessageDialog(None, "Do you want to clean up unnecessary files??",
                                       'Confirmation', wx.YES_NO | wx.ICON_QUESTION)
                result = dlg.ShowModal()
                if result == wx.ID_YES:
                    print("======================= Cleaning up ==========================\n")
                    if os.path.exists(os.path.join(self.topasInpDir, "bkg_extract_temp.inp")):
                        os.remove(os.path.join(self.topasInpDir, "bkg_extract_temp.inp"))
                    if os.path.exists(os.path.join(self.topasInpDir, "bkg_extract_temp.out")):
                        os.remove(os.path.join(self.topasInpDir, "bkg_extract_temp.out"))
                    if os.path.exists(os.path.join(self.topasInpDir, "res_mat_prep_temp.inp")):
                        os.remove(os.path.join(self.topasInpDir, "res_mat_prep_temp.inp"))
                    if os.path.exists(os.path.join(self.topasInpDir, "res_mat_prep_temp.out")):
                        os.remove(os.path.join(self.topasInpDir, "res_mat_prep_temp.out"))
                    if os.path.exists(os.path.join(self.topasInpDir, "temptemp.inp")):
                        os.remove(os.path.join(self.topasInpDir, "temptemp.inp"))
                    if os.path.exists(os.path.join(self.topasInpDir, "temptemp.out")):
                        os.remove(os.path.join(self.topasInpDir, "temptemp.out"))
                    for fl in glob.glob(os.path.join(self.topasInpDir,"dataTemp*.xye")):
                        os.remove(fl)
                    for fl in glob.glob(os.path.join(self.topasInpDir,"q_ycalc_resmat_tof*.dat")):
                        os.remove(fl)
                    self.resMatTOFDone = False
                    self.tof_rm_worker = None
                    print("===================== Cleaning up done =========================\n")
            else:
                wx.LogError('Nothing to clean yet!!!')
                return
        else:
            wx.LogError('Nothing to clean yet!!!')
            return

# Tab for displaying help docs.
class PageHelp(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        docDisp = wx.FlexGridSizer(1, 1, 0, 0)
        docDisp.SetFlexibleDirection(wx.BOTH)
        docDisp.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.doc_text = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                      wx.DefaultSize, wx.TE_MULTILINE |
                                      wx.TE_READONLY | wx.TE_WORDWRAP)
        self.doc_text.Bind(wx.EVT_CHAR, self.OnSelectAll)
        docDisp.AddMany([(self.doc_text, 1, wx.EXPAND)])
        docDisp.AddGrowableRow(0, 1)
        docDisp.AddGrowableCol(0, 1)

        docFile = open(os.path.join(package_directory, "stuff", "help.txt"),"r")
        for line in docFile:
            self.doc_text.WriteText(line)

        self.SetSizer(docDisp)
        self.Layout()

    def OnSelectAll(self, event):
        keyInput = event.GetKeyCode()
        if keyInput == 1:  # 1 stands for 'ctrl+a'
            self.doc_text.SelectAll()
            pass
        event.Skip()

class MainFrame(wx.Frame):
    def __init__(self,parent):
        wx.Frame.__init__(self, None, title=wx.EmptyString, pos=wx.DefaultPosition, size=wx.Size(
                              1000, 650), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        # Here we create a panel and a notebook on the panel
        p = wx.Panel(self)
        self.nb = wx.Notebook(p)

        # create the page windows as children of the notebook
        page1 = ProfileExtract(self.nb)
        page2 = PageRMCW(self.nb)
        page2a = PageRMTOF(self.nb)
        page3 = PageHelp(self.nb)

        # add the pages to the notebook with the label to show on the tab
        self.nb.AddPage(page1, "Profile Preparation")
        self.nb.AddPage(page2, "Resolution Matrix - CW")
        self.nb.AddPage(page2a, "Resolution Matrix - TOF")
        self.nb.AddPage(page3, "Help")

        # finally, put the notebook in a sizer for the panel to manage
        # the layout
        sizer = wx.BoxSizer()
        sizer.Add(self.nb, 1, wx.EXPAND)
        p.SetSizer(sizer)

        page3.Bind(wx.EVT_LEFT_DCLICK, self.dynamic_tab)

        ico = wx.Icon(os.path.join(package_directory, "stuff", "icon.ico"), wx.BITMAP_TYPE_ICO)
        self.SetIcon(ico)

    def dynamic_tab(self, event):
        print('dynamic_tab()')
        dynamic_page = PageDynamic(self.nb)
        self.nb.AddPage(dynamic_page, "Page Dynamic")

    def __del__(self):
        pass
