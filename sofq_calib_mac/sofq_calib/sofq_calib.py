from datetime import datetime
import platform
import os
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np

import wx
import matplotlib
# matplotlib.use('WXAgg')
import matplotlib.pyplot as plt
from datetime import datetime
import sys


if platform.system() == "Windows":
    import ctypes
    myappid = 'ornl.sofq_calib.1.0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


class plotBFrame(wx.Frame):
    def __init__(self, parent, numBnks, sofq_banks_data, bank_keys,
                 check_boxes):
        wx.Frame.__init__(self, None, title='Plot banks',
                          size=wx.Size(1200, 750),
                          style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        self.numBnks = numBnks
        self.sofq_banks_data = sofq_banks_data
        self.bank_keys = bank_keys
        self.check_boxes = check_boxes

        if getattr(sys, 'frozen', False):
            # frozen
            package_directory = os.path.dirname(sys.executable)
        else:
            # unfrozen
            package_directory = os.path.dirname(os.path.abspath(__file__))

        # package_directory = os.path.dirname(os.path.abspath(__file__))
        # package_directory = os.path.dirname(os.path.abspath('.'))
        ico = wx.Icon(os.path.join(package_directory, "stuff",
                                   "icon.ico"), wx.BITMAP_TYPE_ICO)
        self.SetIcon(ico)

        self.panel = plotBPanel(self, self.numBnks, self.sofq_banks_data,
                                self.bank_keys, self.check_boxes)

        self.Show()

    def OnCloseWindow(self, event):
        self.Destroy()

    def Destroy(self):
        return wx.Frame.Destroy(self)


class plotBPanel(wx.Panel):
    def __init__(self, parent, numBnks, sofq_banks_data,
                 bank_keys, check_boxes):
        wx.Panel.__init__(self, parent)
        
        self.numBnks = numBnks
        self.sofq_banks_data = sofq_banks_data
        self.bank_keys = bank_keys
        self.check_boxes = check_boxes
        
        self.figure = Figure()
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.Realize()
        
        self.holder = wx.StaticText(
            self, wx.ID_ANY, u"", wx.DefaultPosition,
            wx.DefaultSize, wx.ALIGN_CENTRE_HORIZONTAL)

        self.canvas.mpl_connect('motion_notify_event',
                                self.onMotion)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.EXPAND)
        sizer.Add(self.holder, 0, wx.LEFT | wx.EXPAND)
        sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
        self.SetSizer(sizer)
        
        self.axes = self.figure.add_subplot(111)
        self.figure.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.1)
        
        if self.numBnks > 0 and not any(self.check_boxes):
            self.axes.clear()
            for i in range(self.numBnks):
                q_temp = []
                y_temp = []
                for item in self.sofq_banks_data[self.bank_keys[i]]:
                    q_temp.append(item[0])
                    y_temp.append(item[1])
                q_temp_a = np.asarray(q_temp)
                y_temp_a = np.asarray(y_temp)
                
                self.axes.plot(q_temp_a, y_temp_a, label="Bank-" + self.bank_keys[i])

            self.axes.xaxis.set_ticks_position('bottom')
            self.axes.yaxis.set_ticks_position('left')
            self.axes.legend()
            self.axes.set_xlabel("Q ($\AA^{-1}$)", fontsize=15)
            self.axes.set_ylabel("S(Q)", fontsize=15)
            self.axes.xaxis.set_tick_params(labelsize=13)
            self.axes.yaxis.set_tick_params(labelsize=13)
        elif self.numBnks == 0:
            wx.MessageBox('No banks calibrated yet!',
                          'Error', wx.OK | wx.ICON_ERROR)
            return
        else:
            self.axes.clear()
            for i in range(self.numBnks):
                if self.check_boxes[i]:
                    q_temp = []
                    y_temp = []
                    for item in self.sofq_banks_data[self.bank_keys[i]]:
                        q_temp.append(item[0])
                        y_temp.append(item[1])
                    q_temp_a = np.asarray(q_temp)
                    y_temp_a = np.asarray(y_temp)
                    
                    self.axes.plot(q_temp_a, y_temp_a,
                                   label="Bank-" + self.bank_keys[i])
            
            self.axes.xaxis.set_ticks_position('bottom')
            self.axes.yaxis.set_ticks_position('left')
            self.axes.legend()
            self.axes.set_xlabel("Q ($\AA^{-1}$)", fontsize=15)
            self.axes.set_ylabel("S(Q)", fontsize=15)
            self.axes.xaxis.set_tick_params(labelsize=13)
            self.axes.yaxis.set_tick_params(labelsize=13)

    def onMotion(self, event):
        xdata = event.xdata
        ydata = event.ydata
        try:
            x = xdata
            y = ydata
        except:
            x = 0
            y = 0
        if x and y:
            self.holder.SetLabelText("x={0:5.3f}, y={1:5.3f}".format(x, y))
        else:
            self.holder.SetLabelText("")


class mergeFrame(wx.Frame):

    def __init__(self, numBnks, sofq_banks_data,
                 difcIn_banks_data, difcInput_banks_data,
                 difaInput_banks_data, dzeroInput_banks_data,
                 path_hist_sofq, outText):
        wx.Frame.__init__(self, None, title="Merge banks",
                          pos=wx.DefaultPosition,
                          size=wx.Size(500, 300),
                          style=wx.MINIMIZE_BOX |
                          wx.SYSTEM_MENU |
                          wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        if getattr(sys, 'frozen', False):
            # frozen
            package_directory = os.path.dirname(sys.executable)
        else:
            # unfrozen
            package_directory = os.path.dirname(os.path.abspath(__file__))
        
        # package_directory = os.path.dirname(os.path.abspath(__file__))
        # package_directory = os.path.dirname(os.path.abspath('.'))
        ico = wx.Icon(os.path.join(package_directory, "stuff",
                                   "icon.ico"), wx.BITMAP_TYPE_ICO)
        self.SetIcon(ico)

        self.numBnks = numBnks
        self.sofq_banks_data = sofq_banks_data
        self.difcIn_banks_data = difcIn_banks_data
        self.difcInput_banks_data = difcInput_banks_data
        self.difaInput_banks_data = difaInput_banks_data
        self.dzeroInput_banks_data = dzeroInput_banks_data
        self.path_hist_sofq = path_hist_sofq
        self.outText = outText

        self.panel = mergePanel(self, self.numBnks, self.sofq_banks_data,
                                self.difcIn_banks_data, self.difcInput_banks_data,
                                self.difaInput_banks_data, self.dzeroInput_banks_data,
                                self.path_hist_sofq, self.outText)

        self.Show()

    def Destroy(self):
        try:
            for item in self.panel.frame:
                try:
                    item.Destroy()
                except RuntimeError:
                    pass
                except AttributeError:
                    pass
        except RuntimeError:
            pass
        except AttributeError:
            pass
        
        return wx.Frame.Destroy(self)


class mergePanel(wx.Panel):
    def __init__(self, parent, numBnks, sofq_banks_data,
                 difcIn_banks_data, difcInput_banks_data,
                 difaInput_banks_data, dzeroInput_banks_data,
                 path_hist_sofq, outText):

        wx.Panel.__init__(self, parent)

        self.frame = []

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        self.numBnks = numBnks
        self.sofq_banks_data = sofq_banks_data
        self.difcIn_banks_data = difcIn_banks_data
        self.difcInput_banks_data = difcInput_banks_data
        self.difaInput_banks_data = difaInput_banks_data
        self.dzeroInput_banks_data = dzeroInput_banks_data
        self.path_hist_sofq = path_hist_sofq
        self.outText = outText

        self.default_dir = ""

        mainMainS = wx.FlexGridSizer(3, 1, 0, 0)
        mainMainS.SetFlexibleDirection(wx.BOTH)
        mainMainS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        holder = wx.StaticText(
            self, wx.ID_ANY, u"", wx.DefaultPosition,
            wx.DefaultSize, wx.ALIGN_CENTRE_HORIZONTAL)
        qStartH = wx.StaticText(
            self, wx.ID_ANY, u"\nQ_Start", wx.DefaultPosition,
            wx.DefaultSize, wx.ALIGN_CENTRE_HORIZONTAL)
        qEndH = wx.StaticText(
            self, wx.ID_ANY, u"\nQ_End", wx.DefaultPosition,
            wx.DefaultSize, wx.ALIGN_CENTRE_HORIZONTAL)

        mainS = wx.FlexGridSizer(self.numBnks + 1, 3, 0, 0)
        mainS.SetFlexibleDirection(wx.BOTH)
        mainS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.input_matrix = []
        self.checkBoxes = []
        self.inputBoxes = []

        self.input_matrix.append((holder, 1, wx.ALIGN_CENTER_HORIZONTAL, 0))
        self.input_matrix.append((qStartH, 1, wx.ALIGN_CENTER_HORIZONTAL, 5))
        self.input_matrix.append((qEndH, 1, wx.ALIGN_CENTER_HORIZONTAL, 5))

        self.bank_keys = [key for key in self.sofq_banks_data.keys()]

        for i in range(self.numBnks):
            self.checkBoxes.append(wx.CheckBox(self,
                                               label='Bank-' + self.bank_keys[i]))
            self.input_matrix.append((self.checkBoxes[i], 1, wx.EXPAND, 5))
            self.inputBoxes.append([])
            for j in range(2):
                self.inputBoxes[i].append(wx.TextCtrl(
                    self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize))
                self.input_matrix.append((self.inputBoxes[i][j], 1,
                                          wx.EXPAND, 5))

        mainS.AddMany(self.input_matrix)

        for i in range(3):
            mainS.AddGrowableCol(i, 1)

        buttonS = wx.FlexGridSizer(2, 1, 0, 0)
        buttonS.SetFlexibleDirection(wx.BOTH)
        buttonS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        holder_text = wx.StaticText(
            self, wx.ID_ANY, u"", wx.DefaultPosition,
            wx.DefaultSize, wx.ALIGN_CENTRE_HORIZONTAL)

        buttonGroup0 = wx.FlexGridSizer(1, 2, 0, 0)
        buttonGroup0.SetFlexibleDirection(wx.BOTH)
        buttonGroup0.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        plotBButton = wx.Button(
            self, wx.ID_ANY, u"Plot banks", wx.DefaultPosition,
            wx.DefaultSize, 0)
        DCSButton = wx.Button(
            self, wx.ID_ANY, u"Generate DCS", wx.DefaultPosition,
            wx.DefaultSize, 0)

        plotBButton.Bind(wx.EVT_BUTTON, self.plot_banks)
        DCSButton.Bind(wx.EVT_BUTTON, self.prep_dcs)

        buttonGroup0.AddMany([(plotBButton, 1, wx.EXPAND, 5),
                              (DCSButton, 1, wx.EXPAND, 5)])

        buttonGroup0.AddGrowableCol(0, 1)
        buttonGroup0.AddGrowableCol(1, 1)

        buttonGroup = wx.FlexGridSizer(1, 3, 0, 0)
        buttonGroup.SetFlexibleDirection(wx.BOTH)
        buttonGroup.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        saveMButton = wx.Button(
            self, wx.ID_ANY, u"Save matrix", wx.DefaultPosition,
            wx.DefaultSize, 0)
        loadMButton = wx.Button(
            self, wx.ID_ANY, u"Load matrix", wx.DefaultPosition,
            wx.DefaultSize, 0)
        mergeButton = wx.Button(
            self, wx.ID_ANY, u"Merge banks", wx.DefaultPosition,
            wx.DefaultSize, 0)

        saveMButton.Bind(wx.EVT_BUTTON, self.save_matrix)
        loadMButton.Bind(wx.EVT_BUTTON, self.load_matrix)

        mergeButton.Bind(wx.EVT_BUTTON, self.merge_banks)

        buttonGroup.AddMany([(saveMButton, 1, wx.EXPAND, 5),
                             (loadMButton, 1, wx.EXPAND, 5),
                             (mergeButton, 1, wx.EXPAND, 5)])

        # buttonGroup.AddGrowableRow(0, 1)
        buttonGroup.AddGrowableCol(0, 1)
        buttonGroup.AddGrowableCol(1, 1)
        buttonGroup.AddGrowableCol(2, 1)

        buttonS.AddMany([(buttonGroup0, 1, wx.EXPAND, 5),
                         (buttonGroup, 1, wx.EXPAND, 5)])

        buttonS.AddGrowableCol(0, 1)

        mainMainS.AddMany([(mainS, 1, wx.EXPAND, 5),
                           (holder_text, 1, wx.EXPAND, 5),
                           (buttonS, 1, wx.EXPAND, 5)])

        mainMainS.AddGrowableRow(0, 1)
        mainMainS.AddGrowableRow(1, 1)
        mainMainS.AddGrowableCol(0, 1)

        self.SetSizer(mainMainS)
        self.Layout()

    def plot_banks(self, event):
        check_boxes = [self.checkBoxes[i].IsChecked() for i in range(self.numBnks)]

        if self.numBnks == 0:
            wx.MessageBox('No banks calibrated yet!',
                          'Error', wx.OK | wx.ICON_ERROR)
            return

        self.frame.append(plotBFrame(wx.Frame, self.numBnks, self.sofq_banks_data,
                          self.bank_keys, check_boxes))

    def prep_dcs(self, event):
        if self.numBnks == 0:
            wx.MessageBox('No banks calibrated yet!',
                          'Error', wx.OK | wx.ICON_ERROR)
            return
        
        for i in range(self.numBnks):
            if not (self.inputBoxes[i][0].GetValue() and
                    self.inputBoxes[i][1].GetValue()):
                wx.MessageBox('Values missing for bank-' +
                              self.bank_keys[i] + "!",
                              'Error', wx.OK | wx.ICON_ERROR)
                return
        
        q_val_temp = []
        int_val_temp = []
        for i in range(6):
            if str(i + 1) in self.bank_keys:
                pos = self.bank_keys.index(str(i + 1))
                lower_lim = float(self.inputBoxes[pos][0].GetValue())
                upper_lim = float(self.inputBoxes[pos][1].GetValue())
                for item in self.sofq_banks_data[str(i + 1)]:
                    if lower_lim < item[0] <= upper_lim:
                        q_val_temp.append(item[0])
                        int_val_temp.append([0 for j in range(12)])
                        int_val_temp[-1][2 * i] = item[1]

        if not platform.system() == "Windows":
            if os.path.exists(self.path_hist_sofq):
                hist_file = open(self.path_hist_sofq, "r")
                line = hist_file.readline()
                if line:
                    self.default_dir = line.strip()
                hist_file.close()
        else:
            pass

        if not self.default_dir:
            export_file = wx.FileDialog(self, 'Save DCS file',
                                        wildcard='DCS (*.dcs)|*.dcs|All Files|*',
                                        style=wx.FD_SAVE |
                                        wx.FD_OVERWRITE_PROMPT)
        else:
            export_file = wx.FileDialog(self, 'Save DCS file',
                                        defaultDir=self.default_dir,
                                        wildcard='DCS (*.dcs)|*.dcs|All Files|*',
                                        style=wx.FD_SAVE |
                                        wx.FD_OVERWRITE_PROMPT)

        try:
            if export_file.ShowModal() == wx.ID_CANCEL:
                return
            self.dcs_out = os.path.join(export_file.GetDirectory(),
                                        export_file.GetFilename())
            dcs_file = open(self.dcs_out, "w")
            for i in range(len(q_val_temp)):
                dcs_file.write("{0:15.7E}".format(q_val_temp[i]))
                for j in range(6):
                    dcs_file.write("{0:15.7E}{1:15.7E}".format(
                        int_val_temp[i][2 * j], int_val_temp[i][2 * j + 1]))
                dcs_file.write("\n")
            dcs_file.close()
            self.outText.SetValue(self.outText.GetValue() + "\n" +
                                  "DCS file output to: " + "\n" +
                                  self.dcs_out + "\n")
            wx.MessageBox('Remember to manually add header' +
                          ' lines to the DCS file if needed!',
                          'Warning', wx.OK | wx.ICON_WARNING)
        except Exception:
            wx.LogError('Failed to create DCS file!')
            raise
        finally:
            export_file.Destroy()

    def merge_banks(self, event):
        check_boxes = [self.checkBoxes[i].IsChecked() for
                       i in range(self.numBnks)]

        if self.numBnks == 0:
            wx.MessageBox('No banks calibrated yet!',
                          'Error', wx.OK | wx.ICON_ERROR)
            return

        if self.numBnks > 0 and not any(check_boxes):
            wx.MessageBox('No boxes checked!',
                          'Error', wx.OK | wx.ICON_ERROR)
            return

        merged_data = []
        for i in range(self.numBnks):
            if check_boxes[i]:
                if not (self.inputBoxes[i][0].GetValue() and self.inputBoxes[i][1].GetValue()):
                    wx.MessageBox('Values missing for bank-' + self.bank_keys[i] + "!",
                                  'Error', wx.OK | wx.ICON_ERROR)
                    return

                upper_lim = float(self.inputBoxes[i][1].GetValue())
                lower_lim = float(self.inputBoxes[i][0].GetValue())

                for item in self.sofq_banks_data[self.bank_keys[i]]:
                    if lower_lim <= item[0] < upper_lim:
                        merged_data.append(item)
                        
        final_q_temp = []
        to_drop = []
        for key, item in enumerate(merged_data):
            if item[0] not in final_q_temp:
                final_q_temp.append(item[0])
            else:
                to_drop.append(key)
        
        for ele in sorted(to_drop, reverse = True):
            del merged_data[ele]

        merged_data_final = sorted(merged_data, key=lambda x: x[0])

        if not platform.system() == "Windows":
            if os.path.exists(self.path_hist_sofq):
                hist_file = open(self.path_hist_sofq, "r")
                line = hist_file.readline()
                if line:
                    self.default_dir = line.strip()
                hist_file.close()
        else:
            pass

        if not self.default_dir:
            export_file = wx.FileDialog(self, 'Save merged S(Q) data',
                                        wildcard='S(Q) (*.sq)|*.sq|All Files|*',
                                        style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        else:
            export_file = wx.FileDialog(self, 'Save merged S(Q) data',
                                        defaultDir=self.default_dir,
                                        wildcard='S(Q) (*.sq)|*.sq|All Files|*',
                                        style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

        try:
            if export_file.ShowModal() == wx.ID_CANCEL:
                return
            self.merge_out = os.path.join(export_file.GetDirectory(),
                                          export_file.GetFilename())
            merge_file = open(self.merge_out, "w")
            
            merge_file.write(str(len(merged_data_final)) + "\n")
            merge_file.write("# Merged S(Q)\n")
            for item in merged_data_final:
                merge_file.write("{0:12.5f}{1:15.7f}\n".format(item[0], item[1]))
            merge_file.close()
            
            time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            if self.outText.GetValue():
                self.outText.SetValue(self.outText.GetValue() + "\n" + time_str + "\n" +
                                      "Merged S(Q) data exported:" +
                                      "\n" + export_file.GetPath() + "\n")
            else:
                self.outText.SetValue(self.outText.GetValue() + time_str + "\n" +
                                      "Merged S(Q) data exported:" +
                                      "\n" + export_file.GetPath() + "\n")
            merged_banks_label = []
            for i in range(self.numBnks):
                if check_boxes[i]:
                    merged_banks_label.append(self.bank_keys[i])
            separator = ', '
            merge_out_log = separator.join(merged_banks_label)
            self.outText.SetValue(self.outText.GetValue() + "\n" +
                                  "Merged banks: " + merge_out_log + "\n")
        except Exception:
            wx.LogError('Failed to save merged S(Q) data file!')
            raise
        finally:
            export_file.Destroy()
            
    def save_matrix(self, event):
        check_boxes = [self.checkBoxes[i].IsChecked() for i in range(self.numBnks)]

        if self.numBnks == 0:
            wx.MessageBox('No banks calibrated yet!',
                          'Error', wx.OK | wx.ICON_ERROR)
            return

        if self.numBnks > 0 and not any(check_boxes):
            wx.MessageBox('No boxes checked!',
                          'Error', wx.OK | wx.ICON_ERROR)
            return

        matrix_data = []
        for i in range(self.numBnks):
            if check_boxes[i]:
                if not (self.inputBoxes[i][0].GetValue() and self.inputBoxes[i][1].GetValue()):
                    wx.MessageBox('Values missing for bank-' + self.bank_keys[i] + "!",
                                  'Error', wx.OK | wx.ICON_ERROR)
                    return

                upper_lim = self.inputBoxes[i][1].GetValue()
                lower_lim = self.inputBoxes[i][0].GetValue()
                
                matrix_data.append([lower_lim, upper_lim])
            else:
                matrix_data.append([])

        if not platform.system() == "Windows":
            if os.path.exists(self.path_hist_sofq):
                hist_file = open(self.path_hist_sofq, "r")
                line = hist_file.readline()
                if line:
                    self.default_dir = line.strip()
                hist_file.close()
        else:
            pass

        if not self.default_dir:
            export_file = wx.FileDialog(self, 'Save matrix',
                                        wildcard='matrix (*.mat)|*.mat|All Files|*',
                                        style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        else:
            export_file = wx.FileDialog(self, 'Save matrix',
                                        defaultDir=self.default_dir,
                                        wildcard='matrix (*.mat)|*.mat|All Files|*',
                                        style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        
        try:
            if export_file.ShowModal() == wx.ID_CANCEL:
                return
            matrix_out = os.path.join(export_file.GetDirectory(),
                                      export_file.GetFilename())
            matrix_file = open(matrix_out, "w")
            for i in range(self.numBnks):
                if check_boxes[i]:
                    matrix_file.write("{0:5s}{1:15s}{2:15s}\n".format(self.bank_keys[i],
                                                                    matrix_data[i][0],
                                                                    matrix_data[i][1]))
            matrix_file.close()
            
            time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            if self.outText.GetValue():
                self.outText.SetValue(self.outText.GetValue() + "\n" + time_str + "\n" +
                                      "Matrix data exported:" +
                                      "\n" + export_file.GetPath() + "\n")
            else:
                self.outText.SetValue(self.outText.GetValue() + time_str + "\n" +
                                      "Matrix data exported:" +
                                      "\n" + export_file.GetPath() + "\n")
            
        except Exception:
            wx.LogError('Failed to save the matrix!')
            raise
        finally:
            export_file.Destroy()

    def load_matrix(self, event):

        if self.numBnks == 0:
            wx.MessageBox('No banks calibrated yet!',
                          'Error', wx.OK | wx.ICON_ERROR)
            return

        if not platform.system() == "Windows":
            if os.path.exists(self.path_hist_sofq):
                hist_file = open(self.path_hist_sofq, "r")
                line = hist_file.readline()
                if line:
                    self.default_dir = line.strip()
                hist_file.close()
        else:
            pass

        if not self.default_dir:
            load_file = wx.FileDialog(self, 'Load matrix',
                                        wildcard='matrix (*.mat)|*.mat|All Files|*',
                                        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        else:
            load_file = wx.FileDialog(self, 'Load matrix',
                                        defaultDir=self.default_dir,
                                        wildcard='matrix (*.mat)|*.mat|All Files|*',
                                        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        
        try:
            if load_file.ShowModal() == wx.ID_CANCEL:
                return
            matrix_in = os.path.join(load_file.GetDirectory(),
                                      load_file.GetFilename())
            matrix_file = open(matrix_in, "r")
            
            matrix_data = {}
            line = matrix_file.readline()
            bank_id = line.split()[0].strip()
            matrix_data[bank_id] = [line.strip().split()[1], line.strip().split()[2]]
            while line:
                line = matrix_file.readline()
                if line:
                    bank_id = line.split()[0].strip()
                    matrix_data[bank_id] = [line.strip().split()[1], line.strip().split()[2]]

            matrix_file.close()

            for i in range(self.numBnks):
                if self.bank_keys[i] in matrix_data.keys():
                    self.inputBoxes[i][0].SetValue(matrix_data[self.bank_keys[i]][0])
                    self.inputBoxes[i][1].SetValue(matrix_data[self.bank_keys[i]][1])
            
            time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            if self.outText.GetValue():
                self.outText.SetValue(self.outText.GetValue() + "\n" + time_str + "\n" +
                                      "Matrix data loaded:" +
                                      "\n" + load_file.GetPath() + "\n")
            else:
                self.outText.SetValue(self.outText.GetValue() + time_str + "\n" +
                                      "Matrix data loaded:" +
                                      "\n" + load_file.GetPath() + "\n")
            
        except Exception:
            wx.LogError('Failed to load the matrix!')
            raise
        finally:
            load_file.Destroy()


class CanvasPanel(wx.Panel):
    def __init__(self, parent, path_hist_sofq, path_hist_bragg):

        self.sofqIn = ""
        self.sofqInSpec = False
        self.BraggIn = ""
        self.braggInSpec = False

        self.sofq_data = []
        self.sofq_bank_nums = 0
        self.bragg_data = []
        self.bragg_bank_nums = 0
        self.sofq_data_temp = []
        self.bragg_data_temp = []

        self.sofq_plot_initilized = []
        self.bragg_plot_initilized = []

        self.sld0_call_n = 0
        self.sld1_call_n = 0
        self.sld2_call_n = 0
        self.sld3_call_n = 0
        self.sld4_call_n = 0

        self.sofq_banks_data = {}
        self.difcIn_banks_data = {}
        self.difcInput_banks_data = {}
        self.difaInput_banks_data = {}
        self.dzeroInput_banks_data = {}

        self.path_hist_sofq = path_hist_sofq
        self.path_hist_bragg = path_hist_bragg
        
        self.frame = []
        
        self.default_dir = ""

        wx.Panel.__init__(self, parent)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        mainMainS = wx.FlexGridSizer(3, 1, 0, 0)
        mainMainS.SetFlexibleDirection(wx.BOTH)
        mainMainS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        lineM1 = wx.StaticLine(self, wx.ID_ANY, size=(-1, -1),
                               style=wx.LI_VERTICAL)
        lineM2 = wx.StaticLine(self, wx.ID_ANY, size=(-1, -1),
                               style=wx.LI_VERTICAL)

        # Main sizer.
        fgSizerMain = wx.FlexGridSizer(1, 6, 0, 0)
        fgSizerMain.SetFlexibleDirection(wx.BOTH)
        fgSizerMain.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        # Plot Window.
        # self.figure = Figure()
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.figure.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.1)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.plotWin = wx.BoxSizer(wx.VERTICAL)
        self.plotWin.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.toolbar = NavigationToolbar2Wx(self.canvas)
        self.canvas.mpl_connect('motion_notify_event',
                                self.onMotion)

        # Left column.
        leftCol = wx.FlexGridSizer(16, 1, 0, 0)
        leftCol.SetFlexibleDirection(wx.BOTH)
        leftCol.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        # Load data buttons.
        leftColS1 = wx.FlexGridSizer(1, 2, 0, 0)
        leftColS1.SetFlexibleDirection(wx.BOTH)
        leftColS1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        leftColS1.AddGrowableRow(0, 1)
        leftColS1.AddGrowableCol(0, 1)
        leftColS1.AddGrowableCol(1, 1)

        loadSofQButton = wx.Button(
            self, wx.ID_ANY, u"Load S(Q) data", wx.DefaultPosition,
            wx.DefaultSize, 0)
        loadBraggButton = wx.Button(
            self, wx.ID_ANY, u"Load Bragg data", wx.DefaultPosition,
            wx.DefaultSize, 0)

        loadSofQButton.Bind(wx.EVT_BUTTON, self.loadSofQ)
        loadBraggButton.Bind(wx.EVT_BUTTON, self.loadBragg)

        leftColS1.AddMany([(loadSofQButton, 1, wx.EXPAND, 5),
                           (loadBraggButton, 1, wx.EXPAND, 5)])

        # Input bank number and the corresponding difc value.
        leftColS2 = wx.FlexGridSizer(1, 2, 0, 0)
        leftColS2.SetFlexibleDirection(wx.BOTH)
        leftColS2.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        leftColS2.AddGrowableRow(0, 1)
        leftColS2.AddGrowableCol(0, 1)
        leftColS2.AddGrowableCol(1, 1)

        leftColS21 = wx.FlexGridSizer(2, 2, 0, 0)
        leftColS21.SetFlexibleDirection(wx.BOTH)
        leftColS21.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        leftColS21.AddGrowableRow(0, 1)
        leftColS21.AddGrowableRow(1, 1)
        leftColS21.AddGrowableCol(0, 1)
        leftColS21.AddGrowableCol(1, 1)

        self.bnkNText = wx.StaticText(
            self, wx.ID_ANY, u"Bank Number", wx.DefaultPosition,
            wx.DefaultSize, wx.ALIGN_CENTRE_HORIZONTAL)
        self.bnkNInput = wx.TextCtrl(
            self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize)
        self.inDifcText = wx.StaticText(
            self, wx.ID_ANY, u"Input DIFC", wx.DefaultPosition, wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.inDifcInput = wx.TextCtrl(
            self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize,
            wx.TE_PROCESS_ENTER)

        leftColS21.AddMany([(self.bnkNText, 1, wx.EXPAND, 5),
                            (self.bnkNInput, 1, wx.EXPAND, 5),
                            (self.inDifcText, 1, wx.EXPAND, 5),
                            (self.inDifcInput, 1, wx.EXPAND, 5)])

        plotButton = wx.Button(
            self, wx.ID_ANY, u"Plot", wx.DefaultPosition,
            wx.DefaultSize, 0)

        plotButton.Bind(wx.EVT_BUTTON, self.plot_sofq_bragg)
        
        self.inDifcInput.Bind(wx.EVT_TEXT_ENTER, self.plot_sofq_bragg)

        leftColS2.AddMany([(leftColS21, 1, wx.EXPAND, 5),
                           (plotButton, 1, wx.EXPAND, 5)])

        self.adjustText0 = wx.StaticText(
            self, wx.ID_ANY, u"Adjust Difc", wx.DefaultPosition,
            wx.DefaultSize, wx.ALIGN_CENTRE_HORIZONTAL)
        self.sld0 = wx.Slider(self, value=0, minValue=-100, maxValue=100,
                              style=wx.SL_HORIZONTAL)  # | wx.SL_LABELS)

        self.sld0.Bind(wx.EVT_SLIDER, self.adj_difc_update)

        self.leftColS3 = wx.FlexGridSizer(1, 3, 0, 0)
        self.leftColS3.SetFlexibleDirection(wx.BOTH)
        self.leftColS3.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.adjustText1 = wx.StaticText(
            self, wx.ID_ANY, u"Adjust Bragg Scale", wx.DefaultPosition,
            wx.DefaultSize, wx.ALIGN_CENTRE_HORIZONTAL)
        self.adjustVal1 = wx.TextCtrl(
            self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize,
            wx.TE_PROCESS_ENTER)
        updateButton1 = wx.Button(
            self, wx.ID_ANY, u"Update", wx.DefaultPosition,
            wx.DefaultSize, 0)

        updateButton1.Bind(wx.EVT_BUTTON, self.adj_bragg_scale)
        self.adjustVal1.Bind(wx.EVT_TEXT_ENTER, self.adj_bragg_scale)

        self.leftColS3.AddMany([(self.adjustText1, 1, wx.EXPAND, 5),
                                (self.adjustVal1, 1, wx.EXPAND, 5),
                                (updateButton1, 1, wx.EXPAND, 5)])
        self.leftColS3.AddGrowableCol(0, 1)
        self.leftColS3.AddGrowableCol(1, 1)
        self.leftColS3.AddGrowableCol(2, 1)

        self.sld1 = wx.Slider(self, value=0, minValue=-10, maxValue=10,
                              style=wx.SL_HORIZONTAL)  # | wx.SL_LABELS)

        self.sld1.Bind(wx.EVT_SLIDER, self.adj_bragg_scale_sld)

        self.leftColS4 = wx.FlexGridSizer(1, 3, 0, 0)
        self.leftColS4.SetFlexibleDirection(wx.BOTH)
        self.leftColS4.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.adjustText2 = wx.StaticText(
            self, wx.ID_ANY, u"Adjust Bragg Offset", wx.DefaultPosition,
            wx.DefaultSize, wx.ALIGN_CENTRE_HORIZONTAL)
        self.adjustVal2 = wx.TextCtrl(
            self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize,
            wx.TE_PROCESS_ENTER)
        updateButton2 = wx.Button(
            self, wx.ID_ANY, u"Update", wx.DefaultPosition,
            wx.DefaultSize, 0)

        updateButton2.Bind(wx.EVT_BUTTON, self.adj_bragg_offset)
        self.adjustVal2.Bind(wx.EVT_TEXT_ENTER, self.adj_bragg_offset)

        self.leftColS4.AddMany([(self.adjustText2, 1, wx.EXPAND, 5),
                                (self.adjustVal2, 1, wx.EXPAND, 5),
                                (updateButton2, 1, wx.EXPAND, 5)])
        self.leftColS4.AddGrowableCol(0, 1)
        self.leftColS4.AddGrowableCol(1, 1)
        self.leftColS4.AddGrowableCol(2, 1)

        self.sld2 = wx.Slider(self, value=0, minValue=-10, maxValue=10,
                              style=wx.SL_HORIZONTAL)  # | wx.SL_LABELS)

        self.sld2.Bind(wx.EVT_SLIDER, self.adj_bragg_offset_sld)

        self.leftColS5 = wx.FlexGridSizer(1, 3, 0, 0)
        self.leftColS5.SetFlexibleDirection(wx.BOTH)
        self.leftColS5.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.adjustText3 = wx.StaticText(
            self, wx.ID_ANY, u"Adjust S(TOF) Scale", wx.DefaultPosition,
            wx.DefaultSize, wx.ALIGN_CENTRE_HORIZONTAL)
        self.adjustVal3 = wx.TextCtrl(
            self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize,
            wx.TE_PROCESS_ENTER)
        updateButton3 = wx.Button(
            self, wx.ID_ANY, u"Update", wx.DefaultPosition,
            wx.DefaultSize, 0)

        updateButton3.Bind(wx.EVT_BUTTON, self.adj_sofq_scale)
        self.adjustVal3.Bind(wx.EVT_TEXT_ENTER, self.adj_sofq_scale)

        self.leftColS5.AddMany([(self.adjustText3, 1, wx.EXPAND, 5),
                                (self.adjustVal3, 1, wx.EXPAND, 5),
                                (updateButton3, 1, wx.EXPAND, 5)])
        self.leftColS5.AddGrowableCol(0, 1)
        self.leftColS5.AddGrowableCol(1, 1)
        self.leftColS5.AddGrowableCol(2, 1)

        self.sld3 = wx.Slider(self, value=0, minValue=-10, maxValue=10,
                              style=wx.SL_HORIZONTAL)  # | wx.SL_LABELS)

        self.sld3.Bind(wx.EVT_SLIDER, self.adj_sofq_scale_sld)

        self.leftColS6 = wx.FlexGridSizer(1, 3, 0, 0)
        self.leftColS6.SetFlexibleDirection(wx.BOTH)
        self.leftColS6.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.adjustText4 = wx.StaticText(
            self, wx.ID_ANY, u"Adjust S(TOF) Offset", wx.DefaultPosition,
            wx.DefaultSize, wx.ALIGN_CENTRE_HORIZONTAL)
        self.adjustVal4 = wx.TextCtrl(
            self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize,
            wx.TE_PROCESS_ENTER)
        updateButton4 = wx.Button(
            self, wx.ID_ANY, u"Update", wx.DefaultPosition,
            wx.DefaultSize, 0)

        updateButton4.Bind(wx.EVT_BUTTON, self.adj_sofq_offset)
        self.adjustVal4.Bind(wx.EVT_TEXT_ENTER, self.adj_sofq_offset)

        self.leftColS6.AddMany([(self.adjustText4, 1, wx.EXPAND, 5),
                                (self.adjustVal4, 1, wx.EXPAND, 5),
                                (updateButton4, 1, wx.EXPAND, 5)])
        self.leftColS6.AddGrowableCol(0, 1)
        self.leftColS6.AddGrowableCol(1, 1)
        self.leftColS6.AddGrowableCol(2, 1)

        self.sld4 = wx.Slider(self, value=0, minValue=-10, maxValue=10,
                              style=wx.SL_HORIZONTAL)  # | wx.SL_LABELS)

        self.sld4.Bind(wx.EVT_SLIDER, self.adj_sofq_offset_sld)

        self.holder_MT = wx.StaticText(
            self, wx.ID_ANY, u"",
            wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_LEFT)

        self.holder = wx.StaticText(
            self, wx.ID_ANY, u"",
            wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_LEFT)

        self.authorInfo = wx.StaticText(
            self, wx.ID_ANY,
            u"Yuanpeng Zhang @ NIST-ORNL\nzyroc1990@gmail.com",
            wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_LEFT)

        # Compose left column.
        leftCol.AddMany([(leftColS1, 1, wx.EXPAND | wx.TOP, 4),
                         (leftColS2, 1, wx.EXPAND | wx.TOP, 4),
                         (self.adjustText0, 1, wx.EXPAND | wx.TOP, 4),
                         (self.sld0, 1, wx.EXPAND | wx.TOP, 4),
                         (self.leftColS3, 1, wx.EXPAND | wx.TOP, 4),
                         (self.sld1, 1, wx.EXPAND | wx.TOP, 4),
                         (self.leftColS4, 1, wx.EXPAND | wx.TOP, 4),
                         (self.sld2, 1, wx.EXPAND | wx.TOP, 4),
                         (self.leftColS5, 1, wx.EXPAND | wx.TOP, 4),
                         (self.sld3, 1, wx.EXPAND | wx.TOP, 4),
                         (self.leftColS6, 1, wx.EXPAND | wx.TOP, 4),
                         (self.sld4, 1, wx.EXPAND | wx.TOP, 4),
                         (self.holder_MT, 1, wx.EXPAND, 5),
                         (self.holder, 1, wx.EXPAND, 5),
                         (self.toolbar, 1, wx.EXPAND, 5),
                         (self.authorInfo, 1, wx.EXPAND, 5)])

        leftCol.AddGrowableRow(12, 1)

        # Separator line.
        line1 = wx.StaticLine(self, wx.ID_ANY, size=(-1, -1),
                              style=wx.LI_VERTICAL)
        line2 = wx.StaticLine(self, wx.ID_ANY, size=(-1, -1),
                              style=wx.LI_VERTICAL)
        line3 = wx.StaticLine(self, wx.ID_ANY, size=(-1, -1),
                              style=wx.LI_VERTICAL)

        # Right column.
        rightCol = wx.FlexGridSizer(4, 1, 0, 0)
        rightCol.SetFlexibleDirection(wx.BOTH)
        rightCol.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        # Input boxes in the right column.
        rightColS1 = wx.FlexGridSizer(3, 2, 0, 0)
        rightColS1.SetFlexibleDirection(wx.BOTH)
        rightColS1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.difcText = wx.StaticText(
            self, wx.ID_ANY, u"Difc", wx.DefaultPosition, wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.difcInput = wx.TextCtrl(
            self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize)
        self.difaText = wx.StaticText(
            self, wx.ID_ANY, u"Difa", wx.DefaultPosition, wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.difaInput = wx.TextCtrl(
            self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize)
        self.dzText = wx.StaticText(
            self, wx.ID_ANY, u"Dzero", wx.DefaultPosition, wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.dzInput = wx.TextCtrl(
            self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize)

        rightColS1.AddMany([(self.difcText, 1, wx.EXPAND, 5),
                            (self.difcInput, 1, wx.EXPAND, 5),
                            (self.difaText, 1, wx.EXPAND, 5),
                            (self.difaInput, 1, wx.EXPAND, 5),
                            (self.dzText, 1, wx.EXPAND, 5),
                            (self.dzInput, 1, wx.EXPAND, 5)])
        rightColS1.AddGrowableRow(0, 1)
        rightColS1.AddGrowableRow(1, 1)
        rightColS1.AddGrowableRow(2, 1)
        rightColS1.AddGrowableCol(0, 1)
        rightColS1.AddGrowableCol(1, 1)

        self.outText = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString,
                                   wx.DefaultPosition,
                                   wx.DefaultSize, wx.TE_MULTILINE |
                                   wx.TE_READONLY | wx.TE_WORDWRAP)
        self.outText.Bind(wx.EVT_CHAR, self.OnSelectAll)
        self.outText.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)

        saveLogButton = wx.Button(
            self, wx.ID_ANY, u"Save log", wx.DefaultPosition,
            wx.DefaultSize, 0)

        saveLogButton.Bind(wx.EVT_BUTTON, self.save_log)

        rightColS2 = wx.FlexGridSizer(1, 2, 0, 0)
        rightColS2.SetFlexibleDirection(wx.BOTH)
        rightColS2.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        exportButton = wx.Button(
            self, wx.ID_ANY, u"Export", wx.DefaultPosition,
            wx.DefaultSize, 0)
        mergeButton = wx.Button(
            self, wx.ID_ANY, u"Merge", wx.DefaultPosition,
            wx.DefaultSize, 0)

        exportButton.Bind(wx.EVT_BUTTON, self.exportBank)

        mergeButton.Bind(wx.EVT_BUTTON, self.open_merge_frame)

        rightColS2.AddMany([(exportButton, 1, wx.EXPAND, 5),
                            (mergeButton, 1, wx.EXPAND, 5)])
        rightColS2.AddGrowableRow(0, 1)
        rightColS2.AddGrowableCol(0, 1)
        rightColS2.AddGrowableCol(1, 1)

        # Compose the right column.
        rightCol.AddMany([(rightColS1, 1, wx.EXPAND | wx.TOP, 4),
                          (self.outText, 1, wx.EXPAND | wx.TOP, 4),
                          (saveLogButton, 1, wx.EXPAND | wx.TOP, 4),
                          (rightColS2, 1, wx.EXPAND | wx.TOP, 4)])

        rightCol.AddGrowableRow(1, 1)
        rightCol.AddGrowableCol(0, 1)

        # Compose the main sizer.
        fgSizerMain.AddMany([(leftCol, 1, wx.EXPAND, 5),
                             (line1, 1, wx.EXPAND, 5),
                             (self.plotWin, 1, wx.EXPAND, 5),
                             (line2, 1, wx.EXPAND, 5),
                             (rightCol, 1, wx.EXPAND, 5),
                             (line3, 1, wx.EXPAND, 5)])

        fgSizerMain.AddGrowableRow(0, 1)
        fgSizerMain.AddGrowableCol(2, 1)

        mainMainS.AddMany([(lineM1, 1, wx.EXPAND, 5),
                           (fgSizerMain, 1, wx.EXPAND, 5),
                           (lineM2, 1, wx.EXPAND, 5)])

        mainMainS.AddGrowableRow(1, 1)
        mainMainS.AddGrowableCol(0, 1)

        self.SetSizer(mainMainS)
        self.Layout()

    def open_merge_frame(self, event):
        self.frame.append(mergeFrame(len(self.sofq_banks_data), self.sofq_banks_data,
                                     self.difcIn_banks_data,
                                     self.difcInput_banks_data, self.difaInput_banks_data,
                                     self.dzeroInput_banks_data, self.path_hist_sofq,
                                     self.outText))

    def draw(self):
        self.axes.set_ylim(-1,1)
        self.axes.set_xlim(-1, 1)
        self.axes.set_yticklabels([])
        self.axes.set_xticklabels([])
        self.axes.xaxis.set_ticks_position('none')
        self.axes.yaxis.set_ticks_position('none')
        self.axes.text(-0.67, 0, r'Calibrate $S(Q)$ against Bragg', fontsize=20)

    def loadSofQ(self, event):

        if not platform.system() == "Windows":
            if os.path.exists(self.path_hist_sofq):
                hist_file = open(self.path_hist_sofq, "r")
                line = hist_file.readline()
                if line:
                    self.default_dir = line.strip()
                hist_file.close()
            else:
                if os.path.exists(self.path_hist_bragg):
                    hist_file = open(self.path_hist_bragg, "r")
                    line = hist_file.readline()
                    if line:
                        self.default_dir = line.strip()
                    hist_file.close()
        else:
            pass
        
        if not self.default_dir:
            filedialog = wx.FileDialog(self, "Load S(Q) File",
                                       wildcard="S(Q) data file (*.sq;*.fq;*.dat)|*.sq;*.fq;*.dat|All files (*.*)|*.*",
                                       style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        else:
            filedialog = wx.FileDialog(self, "Load S(Q) File",
                                       defaultDir=self.default_dir,
                                       wildcard="S(Q) data file (*.sq;*.fq;*.dat)|*.sq;*.fq;*.dat|All files (*.*)|*.*",
                                       style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
            
        try:
            if filedialog.ShowModal() == wx.ID_CANCEL:
                return
            self.sofqIn = os.path.join(filedialog.GetDirectory(),
                                         filedialog.GetFilename())
            self.sofqInSpec = True
            sofq_file = open(self.sofqIn, "r")
            line = sofq_file.readline()
            sofq_pnts_num = int(line.split()[0])
            line = sofq_file.readline()

            self.sofq_data.append([])
            self.sofq_bank_nums += 1
            self.sofq_plot_initilized.append(False)

            for i in range(sofq_pnts_num):
                line = sofq_file.readline()
                if "nan" not in line:
                    self.sofq_data[self.sofq_bank_nums - 1].append(
                        [float(line.split()[0]), float(line.split()[1])])
            sofq_file.close()

            self.sofq_data_temp = []
            for item in self.sofq_data:
                self.sofq_data_temp.append(item)

            time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            if self.outText.GetValue():
                self.outText.SetValue(self.outText.GetValue() + "\n" + time_str + "\n" +
                                    "S(Q) data file loaded:" + "\n" + self.sofqIn + "\n")
            else:
                self.outText.SetValue(self.outText.GetValue() + time_str + "\n" +
                                      "S(Q) data file loaded:" + "\n" + self.sofqIn + "\n")
        except Exception:
            wx.LogError('Failed to open/process S(Q) data file!')
            raise
        finally:
            hist_file = open(self.path_hist_sofq, "w")
            hist_file.write(os.path.join(filedialog.GetDirectory()))
            hist_file.close()
            
            filedialog.Destroy()

    def loadBragg(self, event):

        if not platform.system() == "Windows":
            if os.path.exists(self.path_hist_bragg):
                hist_file = open(self.path_hist_bragg, "r")
                line = hist_file.readline()
                if line:
                    self.default_dir = line.strip()
                hist_file.close()
            else:
                if os.path.exists(self.path_hist_sofq):
                    hist_file = open(self.path_hist_sofq, "r")
                    line = hist_file.readline()
                    if line:
                        self.default_dir = line.strip()
                    hist_file.close()
        else:
            pass

        if not self.default_dir:
            filedialog = wx.FileDialog(self, "Load Bragg File",
                                       wildcard="Bragg data file (*.xye;*.xy)|*.xye;*.xy|All files (*.*)|*.*",
                                       style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        else:
            filedialog = wx.FileDialog(self, "Load Bragg File",
                                       defaultDir=self.default_dir,
                                       wildcard="Bragg data file (*.xye;*.xy)|*.xye;*.xy|All files (*.*)|*.*",
                                       style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        try:
            if filedialog.ShowModal() == wx.ID_CANCEL:
                return
            self.BraggIn = os.path.join(filedialog.GetDirectory(),
                                       filedialog.GetFilename())
            self.braggInSpec = True

            self.bragg_data.append([])
            self.bragg_bank_nums += 1
            self.bragg_plot_initilized.append(False)

            bragg_file = open(self.BraggIn, "r")
            line = bragg_file.readline()
            while "'" in line:
                line = bragg_file.readline()

            self.bragg_data[self.bragg_bank_nums - 1].append([float(line.split()[0]),
                                                              float(line.split()[1])])

            while line:
                line = bragg_file.readline()
                if line:
                    self.bragg_data[self.bragg_bank_nums - 1].append(
                        [float(line.split()[0]), float(line.split()[1])])
            bragg_file.close()
            self.bragg_data_temp = []
            for item in self.bragg_data:
                self.bragg_data_temp.append(item)

            time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            if self.outText.GetValue():
                self.outText.SetValue(self.outText.GetValue() + "\n" + time_str + "\n" +
                                    "Bragg data file loaded:" + "\n" + self.BraggIn + "\n")
            else:
                self.outText.SetValue(self.outText.GetValue() + time_str + "\n" +
                                      "Bragg data file loaded:" + "\n" + self.BraggIn + "\n")

        except Exception:
            wx.LogError('Failed to open/process Bragg data file!')
            raise
        finally:
            hist_file = open(self.path_hist_bragg, "w")
            hist_file.write(os.path.join(filedialog.GetDirectory()))
            hist_file.close()
            
            filedialog.Destroy()

    def plot_sofq_bragg(self, event):
        if not self.braggInSpec:
            wx.LogError("Please load Bragg data!")
            return
        if not self.sofqInSpec:
            wx.LogError("Please load S(Q) data!")
            return
        if self.inDifcInput.GetValue().strip() == "":
            wx.LogError("Please specify input difc value!")
            return

        self.difcIn = float(self.inDifcInput.GetValue())

        t_sofq = [float(item[0])
                  for item in self.sofq_data_temp[self.sofq_bank_nums - 1]]
        t_sofq_temp = [2 * np.pi * self.difcIn / item for item in t_sofq]
        t_sofq_array = np.asarray(t_sofq_temp)
        s_sofq = [float(item[1])
                  for item in self.sofq_data_temp[self.sofq_bank_nums - 1]]
        s_sofq_array = np.asarray(s_sofq)

        t_bragg = [float(item[0])
                   for item in self.bragg_data_temp[self.bragg_bank_nums - 1]]
        t_bragg_array = np.asarray(t_bragg)
        s_bragg = [float(item[1])
                   for item in self.bragg_data_temp[self.bragg_bank_nums - 1]]
        s_bragg_array = np.asarray(s_bragg)
        self.axes.clear()
        self.sofq_plot, = self.axes.plot(t_sofq_array, s_sofq_array, label="S(Q)")
        self.bragg_plot, = self.axes.plot(t_bragg_array, s_bragg_array, label="Bragg")
        self.axes.xaxis.set_ticks_position('bottom')
        self.axes.yaxis.set_ticks_position('left')
        self.axes.legend()
        self.axes.set_xlabel("TOF", fontsize=15)
        self.axes.set_ylabel("Intensity", fontsize=15)
        self.canvas.draw()

        self.sld0.SetValue(0)

        self.sofq_plot_initilized[self.sofq_bank_nums - 1] = True
        self.bragg_plot_initilized[self.bragg_bank_nums - 1] = True

    def adj_difc_update(self, event):
        if self.inDifcInput.GetValue():
            self.sld0_call_n += 1
            if self.sld0_call_n == 1:
                self.difcIn = float(self.inDifcInput.GetValue())
            self.inDifcInput.SetValue(str(self.difcIn +
                                      0.1 * float(self.sld0.GetValue())))

            t_sofq = [float(item[0])
                      for item in self.sofq_data_temp[self.sofq_bank_nums - 1]]
            t_sofq_temp = [2 * np.pi * (self.difcIn + 0.1 * float(self.sld0.GetValue()))
                           / item for item in t_sofq]
            t_sofq_array = np.asarray(t_sofq_temp)
            # s_sofq = [float(item[1])
            #         for item in self.sofq_data_temp[self.sofq_bank_nums - 1]]
            # s_sofq_array = np.asarray(s_sofq)

            self.sofq_plot.set_xdata(t_sofq_array)

            self.canvas.draw()

    def adj_sofq_offset(self, event):
        if not self.braggInSpec:
            wx.LogError("Please load Bragg data!")
            return
        if not self.sofqInSpec:
            wx.LogError("Please load S(Q) data!")
            return
        if self.adjustVal4.GetValue().strip() == "":
            wx.LogError("Please specify offset value for S(Q/TOF) data!")
            return
        if self.sofq_plot_initilized[self.sofq_bank_nums - 1]:
            self.sofq_offset = float(self.adjustVal4.GetValue())
            for i in range(len(self.sofq_data_temp[self.sofq_bank_nums - 1])):
                self.sofq_data_temp[self.sofq_bank_nums - 1][i][1] += self.sofq_offset

            s_sofq = [float(item[1])
                    for item in self.sofq_data_temp[self.sofq_bank_nums - 1]]
            s_sofq_array = np.asarray(s_sofq)

            self.sofq_plot.set_ydata(s_sofq_array)

            self.canvas.draw()

            self.sld4.SetValue(0)
            self.sld4_call_n = 0

        else:
            return

    def adj_sofq_offset_sld(self, event):
        if not self.braggInSpec:
            return
        if not self.sofqInSpec:
            return
        if self.sofq_plot_initilized[self.sofq_bank_nums - 1]:
            self.sofq_offset = float(self.sld4.GetValue() * 0.1)
            self.sld4_call_n += 1
            if self.sld4_call_n == 1:
                self.sofq_data_init = [
                    item[1] for item in self.sofq_data_temp[self.sofq_bank_nums - 1]]
            for i in range(len(self.sofq_data_init)):
                self.sofq_data_temp[self.sofq_bank_nums -
                                    1][i][1] = self.sofq_data_init[i] + self.sofq_offset

            s_sofq = [float(item[1])
                      for item in self.sofq_data_temp[self.sofq_bank_nums - 1]]
            s_sofq_array = np.asarray(s_sofq)

            self.sofq_plot.set_ydata(s_sofq_array)

            self.canvas.draw()

            self.sld3.SetValue(0)
            self.sld3_call_n = 0

        else:
            return

    def adj_sofq_scale(self, event):
        if not self.braggInSpec:
            wx.LogError("Please load Bragg data!")
            return
        if not self.sofqInSpec:
            wx.LogError("Please load S(Q) data!")
            return
        if self.adjustVal3.GetValue().strip() == "":
            wx.LogError("Please specify scale value for S(Q/TOF) data!")
            return
        if self.sofq_plot_initilized[self.sofq_bank_nums - 1]:
            self.sofq_scale = float(self.adjustVal3.GetValue())
            for i in range(len(self.sofq_data_temp[self.sofq_bank_nums - 1])):
                self.sofq_data_temp[self.sofq_bank_nums -
                                    1][i][1] *= self.sofq_scale

            s_sofq = [float(item[1])
                      for item in self.sofq_data_temp[self.sofq_bank_nums - 1]]
            s_sofq_array = np.asarray(s_sofq)

            self.sofq_plot.set_ydata(s_sofq_array)

            self.canvas.draw()

            self.sld3.SetValue(0)
            self.sld3_call_n = 0

        else:
            return

    def adj_sofq_scale_sld(self, event):
        if not self.braggInSpec:
            return
        if not self.sofqInSpec:
            return
        if self.sofq_plot_initilized[self.sofq_bank_nums - 1]:
            self.sofq_scale = float(self.sld3.GetValue()) * 0.1 + 1.0
            self.sld3_call_n += 1
            if self.sld3_call_n == 1:
                self.sofq_data_init = [
                    item[1] for item in self.sofq_data_temp[self.sofq_bank_nums - 1]]
            for i in range(len(self.sofq_data_init)):
                self.sofq_data_temp[self.sofq_bank_nums -
                                    1][i][1] = self.sofq_data_init[i] * self.sofq_scale

            s_sofq = [float(item[1])
                      for item in self.sofq_data_temp[self.sofq_bank_nums - 1]]
            s_sofq_array = np.asarray(s_sofq)

            self.sofq_plot.set_ydata(s_sofq_array)

            self.canvas.draw()

            self.sld4_call_n = 0
            self.sld4.SetValue(0)

        else:
            return

    def adj_bragg_offset(self, event):
        if not self.sofqInSpec:
            wx.LogError("Please load S(Q) data!")
            return
        if not self.braggInSpec:
            wx.LogError("Please load Bragg data!")
            return
        if self.adjustVal2.GetValue().strip() == "":
            wx.LogError("Please specify offset value for Bragg data!")
            return
        if self.bragg_plot_initilized[self.bragg_bank_nums - 1]:
            self.bragg_offset = float(self.adjustVal2.GetValue())
            for i in range(len(self.bragg_data_temp[self.bragg_bank_nums - 1])):
                self.bragg_data_temp[self.bragg_bank_nums -
                                    1][i][1] += self.bragg_offset

            s_bragg = [float(item[1])
                      for item in self.bragg_data_temp[self.bragg_bank_nums - 1]]
            s_bragg_array = np.asarray(s_bragg)

            self.bragg_plot.set_ydata(s_bragg_array)

            self.canvas.draw()

            self.sld2.SetValue(0)
            self.sld2_call_n = 0

        else:
            return

    def adj_bragg_offset_sld(self, event):
        if not self.braggInSpec:
            return
        if not self.sofqInSpec:
            return
        if self.bragg_plot_initilized[self.bragg_bank_nums - 1]:
            self.bragg_offset = float(self.sld2.GetValue() * 0.1)
            self.sld2_call_n += 1
            if self.sld2_call_n == 1:
                self.bragg_data_init = [
                    item[1] for item in self.bragg_data_temp[self.bragg_bank_nums - 1]]
            for i in range(len(self.bragg_data_init)):
                self.bragg_data_temp[self.bragg_bank_nums -
                                    1][i][1] = self.bragg_data_init[i] + self.bragg_offset

            s_bragg = [float(item[1])
                      for item in self.bragg_data_temp[self.bragg_bank_nums - 1]]
            s_bragg_array = np.asarray(s_bragg)

            self.bragg_plot.set_ydata(s_bragg_array)

            self.canvas.draw()

            self.sld1.SetValue(0)
            self.sld1_call_n = 0

        else:
            return

    def adj_bragg_scale(self, event):
        if not self.braggInSpec:
            wx.LogError("Please load Bragg data!")
            return
        if not self.sofqInSpec:
            wx.LogError("Please load S(Q) data!")
            return
        if self.adjustVal1.GetValue().strip() == "":
            wx.LogError("Please specify scale value for Bragg data!")
            return
        if self.bragg_plot_initilized[self.bragg_bank_nums - 1]:
            self.bragg_scale = float(self.adjustVal1.GetValue())
            for i in range(len(self.bragg_data_temp[self.bragg_bank_nums - 1])):
                self.bragg_data_temp[self.bragg_bank_nums -
                                     1][i][1] *= self.bragg_scale

            s_bragg = [float(item[1])
                      for item in self.bragg_data_temp[self.bragg_bank_nums - 1]]
            s_bragg_array = np.asarray(s_bragg)

            self.bragg_plot.set_ydata(s_bragg_array)

            self.canvas.draw()

            self.sld1.SetValue(0)
            self.sld1_call_n = 0

        else:
            return

    def adj_bragg_scale_sld(self, event):
        if not self.braggInSpec:
            return
        if not self.sofqInSpec:
            return
        if self.bragg_plot_initilized[self.bragg_bank_nums - 1]:
            self.bragg_scale = float(self.sld1.GetValue()) * 0.1 + 1.0
            self.sld1_call_n += 1
            if self.sld1_call_n == 1:
                self.bragg_data_init = [
                    item[1] for item in self.bragg_data_temp[self.bragg_bank_nums - 1]]
            for i in range(len(self.bragg_data_init)):
                self.bragg_data_temp[self.bragg_bank_nums -
                                     1][i][1] = self.bragg_data_init[i] * self.bragg_scale

            s_bragg = [float(item[1])
                       for item in self.bragg_data_temp[self.bragg_bank_nums - 1]]
            s_bragg_array = np.asarray(s_bragg)

            self.bragg_plot.set_ydata(s_bragg_array)

            self.canvas.draw()

            self.sld2.SetValue(0)
            self.sld2_call_n = 0

        else:
            return

    def onMotion(self, event):
        xdata = event.xdata
        ydata = event.ydata
        try:
            x = xdata
            y = ydata
        except:
            x = 0
            y = 0
        if x and y:
            self.holder.SetLabelText("x={0:5.3f}, y={1:5.3f}".format(x, y))
        else:
            self.holder.SetLabelText("")

    def OnSelectAll(self, event):
        keyInput = event.GetKeyCode()
        if keyInput == 1:  # 1 stands for 'ctrl+a'
            self.outText.SelectAll()
            pass
        event.Skip()

    def OnRightDown(self, event):
        select_temp = self.outText.GetSelection()
        menu = MyPopupMenu(self.outText.GetValue(),
                           self.outText.GetValue()[int(select_temp[0]):
                               int(select_temp[1])], self.outText)
        self.outText.PopupMenu(menu, event.GetPosition())
        menu.Destroy()

    def exportBank(self, event):
        bank_num_in = self.bnkNInput.GetValue()
        if not bank_num_in:
            wx.MessageBox('Please input the bank number!',
                          'Error', wx.OK | wx.ICON_ERROR)
            return
        else:
            if not bank_num_in.isdigit():
                wx.MessageBox("Please input an positive integer as the bank number!",
                              'Error', wx.OK | wx.ICON_ERROR)
                return
        if len(self.sofq_plot_initilized) > 0 and len(self.bragg_plot_initilized):
            if not self.sofq_plot_initilized[self.sofq_bank_nums - 1] or \
                not self.bragg_plot_initilized[self.bragg_bank_nums - 1]:
                wx.MessageBox('Please calibrate the data first!',
                            'Error', wx.OK | wx.ICON_ERROR)
                return
        else:
            wx.MessageBox('Please calibrate the data first!',
                          'Error', wx.OK | wx.ICON_ERROR)
            return
        difcInput = self.difcInput.GetValue()
        difaInput = self.difaInput.GetValue()
        dzInput = self.dzInput.GetValue()
        if not difcInput:
            wx.MessageBox('Please input the difc value from Bragg refinement!',
                          'Error', wx.OK | wx.ICON_ERROR)
            return
        else:
            if not any([item.isnumeric() for item in difcInput.strip().split(".")]):
                wx.MessageBox('Please input an invalid difc value from Bragg refinement!',
                              'Error', wx.OK | wx.ICON_ERROR)
                return
            else:
                difcInputVal = float(difcInput)
        if not difaInput:
            wx.MessageBox('Please input the difa value from Bragg refinement!',
                          'Error', wx.OK | wx.ICON_ERROR)
            return
        else:
            if not any([item.isnumeric() for item in difcInput.strip().split(".")]):
                wx.MessageBox('Please input an invalid difa value from Bragg refinement!',
                              'Error', wx.OK | wx.ICON_ERROR)
                return
            else:
                difaInputVal = float(difaInput)
        if not dzInput:
            wx.MessageBox('Please input the dzero value from Bragg refinement!',
                          'Error', wx.OK | wx.ICON_ERROR)
            return
        else:
            if not any([item.isnumeric() for item in difcInput.strip().split(".")]):
                wx.MessageBox('Please input an invalid dzero value from Bragg refinement!',
                              'Error', wx.OK | wx.ICON_ERROR)
                return
            else:
                dzInputVal = float(dzInput)

        if not platform.system() == "Windows":
            if os.path.exists(self.path_hist_sofq):
                hist_file = open(self.path_hist_sofq, "r")
                line = hist_file.readline()
                if line:
                    self.default_dir = line.strip()
                hist_file.close()
        else:
            pass

        if not self.default_dir:
            export_file = wx.FileDialog(self, 'Save calibrated S(Q) data',
                                        wildcard='S(Q) (*.sq)|*.sq|All Files|*',
                                        style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        else:
            export_file = wx.FileDialog(self, 'Save calibrated S(Q) data',
                                        defaultDir=self.default_dir,
                                        wildcard='S(Q) (*.sq)|*.sq|All Files|*',
                                        style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

        try:
            if export_file.ShowModal() == wx.ID_CANCEL:
                return
            else:
                export_file_write = open(export_file.GetPath(), "w")
                export_file_write.write(str(len(self.sofq_data[self.sofq_bank_nums - 1])) + "\n")
                export_file_write.write("# Calibrated S(Q) - Bank-" +
                                        bank_num_in.strip() + "\n")
                sofq_bank_data_temp = []
                for item in self.sofq_data[self.sofq_bank_nums - 1]:
                    tof_temp = float(self.inDifcInput.GetValue()) * (2 * np.pi / item[0])
                    if difaInputVal > 0:
                        d_temp = -difcInputVal / (2 * difaInputVal) + \
                            np.sqrt(tof_temp / difaInputVal + (difcInputVal / (2 * difaInputVal))**2
                                    - dzInputVal / difaInputVal)
                    elif difaInputVal < 0:
                        d_temp = -difcInputVal / (2 * difaInputVal) - \
                            np.sqrt(tof_temp / difaInputVal + (difcInputVal / (2 * difaInputVal))**2
                                    - dzInputVal / difaInputVal)
                    else:
                        d_temp = (tof_temp - dzInputVal) / difcInputVal
                    q_temp = 2 * np.pi / d_temp

                    sofq_bank_data_temp.append([q_temp, item[1]])

                    export_file_write.write(
                        "{0:12.5f}{1:15.7f}\n".format(q_temp, item[1]))

                export_file_write.close()

                time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                if self.outText.GetValue():
                    self.outText.SetValue(self.outText.GetValue() + "\n" + time_str + "\n" +
                                        "Calibrated S(Q) data for bank-" + bank_num_in.strip() +
                                        " exported:" + "\n" + export_file.GetPath() + "\n")
                else:
                    self.outText.SetValue(self.outText.GetValue() + time_str + "\n" +
                                          "Calibrated S(Q) data for bank-" + bank_num_in.strip() +
                                          " exported:" + "\n" + export_file.GetPath() + "\n")
                self.outText.SetValue(self.outText.GetValue() +
                                      "\nExported bank # = " + bank_num_in.strip() + "\n" +
                                      "Input Difc = " + self.inDifcInput.GetValue() + "\n" +
                                      "Output Difc = " + difcInput + "\n" +
                                      "Output Difa = " + difaInput + "\n" +
                                      "Output Dzero = " + dzInput + "\n")

                self.sofq_banks_data[bank_num_in] = sofq_bank_data_temp
                self.difcIn_banks_data[bank_num_in] = self.inDifcInput.GetValue()
                self.difcInput_banks_data[bank_num_in] = difcInput
                self.difaInput_banks_data[bank_num_in] = difaInput
                self.dzeroInput_banks_data[bank_num_in] = dzInput

        finally:
            export_file.Destroy()

    def save_log(self, event):
        if not self.outText.GetValue():
            wx.MessageBox('Empty log! Nothing to save!',
                          'Error', wx.OK | wx.ICON_ERROR)
            return
        else:
            if not platform.system() == "Windows":
                if os.path.exists(self.path_hist_sofq):
                    hist_file = open(self.path_hist_sofq, "r")
                    line = hist_file.readline()
                    if line:
                        self.default_dir = line.strip()
                    hist_file.close()
            else:
                pass

            if not self.default_dir:
                export_log = wx.FileDialog(self, 'Save Log',
                                           wildcard='log file (*.log)|*.log|All Files|*',
                                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            else:
                export_log = wx.FileDialog(self, 'Save Log',
                                           defaultDir=self.default_dir,
                                           wildcard='log file (*.log)|*.log|All Files|*',
                                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

            try:
                if export_log.ShowModal() == wx.ID_CANCEL:
                    return
                else:
                    export_log_write = open(export_log.GetPath(), "w")
                    export_log_write.write(self.outText.GetValue())
                    export_log_write.close()
            finally:
                export_log.Destroy()

class MyPopupMenu(wx.Menu):
    def __init__(self, textCont, textSelect, textCtrl):
        wx.Menu.__init__(self)

        self.textCont = textCont
        self.textSelect = textSelect

        self.dataObj = wx.TextDataObject()
        self.dataObj.SetText(textCont)
        self.dataObj1 = wx.TextDataObject()
        self.dataObj1.SetText(textSelect)
        self.outText = textCtrl

        item = wx.MenuItem(self, wx.NewIdRef(count=1), "Copy")
        self.Append(item)
        self.Bind(wx.EVT_MENU, self.OnCopy, item)

        item = wx.MenuItem(self, wx.NewIdRef(count=1), "Clear")
        self.Append(item)
        self.Bind(wx.EVT_MENU, self.OnClear, item)

    def OnCopy(self, event):
        if wx.TheClipboard.Open():
            if self.textSelect == "":
                wx.TheClipboard.SetData(self.dataObj)
                wx.TheClipboard.Close()
            else:
                wx.TheClipboard.SetData(self.dataObj1)
                wx.TheClipboard.Close()
        else:
            wx.LogError("Unable to open the clipboard")

    def OnClear(self, event):
        self.outText.SetValue("")


class MyPopupMenu1(wx.Menu):
    def __init__(self, textCont, textSelect, textCtrl):
        wx.Menu.__init__(self)

        self.textCont = textCont
        self.textSelect = textSelect

        self.dataObj = wx.TextDataObject()
        self.dataObj.SetText(textCont)
        self.dataObj1 = wx.TextDataObject()
        self.dataObj1.SetText(textSelect)
        self.outText = textCtrl

        item = wx.MenuItem(self, wx.NewIdRef(count=1), "Copy")
        self.Append(item)
        self.Bind(wx.EVT_MENU, self.OnCopy, item)

    def OnCopy(self, event):
        if wx.TheClipboard.Open():
            if self.textSelect == "":
                wx.TheClipboard.SetData(self.dataObj)
                wx.TheClipboard.Close()
            else:
                wx.TheClipboard.SetData(self.dataObj1)
                wx.TheClipboard.Close()
        else:
            wx.LogError("Unable to open the clipboard")


class helpFrame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, title="Help page",
                          pos=wx.DefaultPosition,
                          size=wx.Size(1000, 700))
                        #   style=wx.MINIMIZE_BOX |
                        #   wx.SYSTEM_MENU |
                        #   wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        if getattr(sys, 'frozen', False):
            # frozen
            package_directory = os.path.dirname(sys.executable)
        else:
            # unfrozen
            package_directory = os.path.dirname(os.path.abspath(__file__))

        ico = wx.Icon(os.path.join(package_directory, "stuff",
                                   "icon.ico"), wx.BITMAP_TYPE_ICO)
        self.SetIcon(ico)
        
        help_doc_loc = os.path.join(package_directory, "stuff","help.txt")

        self.panel = helpPanel(self, help_doc_loc)

        self.Show()

    def Destroy(self):
        return wx.Frame.Destroy(self)


class helpPanel(wx.Panel):
    def __init__(self, parent, help_doc_loc):

        wx.Panel.__init__(self, parent)
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        
        self.help_doc_loc = help_doc_loc
        
        mainMainS = wx.FlexGridSizer(1, 1, 0, 0)
        mainMainS.SetFlexibleDirection(wx.BOTH)
        mainMainS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)
        
        self.outText = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString,
                                   wx.DefaultPosition,
                                   wx.DefaultSize, wx.TE_MULTILINE |
                                   wx.TE_READONLY | wx.TE_WORDWRAP)
        self.outText.Bind(wx.EVT_CHAR, self.OnSelectAll)
        self.outText.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        
        mainMainS.AddMany([(self.outText, 1, wx.EXPAND, 5)])
        
        mainMainS.AddGrowableRow(0, 1)
        mainMainS.AddGrowableCol(0, 1)
        
        font1 = wx.Font(13, wx.MODERN, wx.NORMAL,
                        wx.NORMAL, False, u'Consolas')
        self.outText.SetFont(font1)

        with open(self.help_doc_loc) as fobj:
            for line in fobj:
                self.outText.WriteText(line)
        
        self.SetSizer(mainMainS)
        self.Layout()
        
    def OnSelectAll(self, event):
        keyInput = event.GetKeyCode()
        if keyInput == 1:  # 1 stands for 'ctrl+a'
            self.outText.SelectAll()
            pass
        event.Skip()

    def OnRightDown(self, event):
        select_temp = self.outText.GetSelection()
        menu = MyPopupMenu1(self.outText.GetValue(),
                            self.outText.GetValue()[int(select_temp[0]):
                                int(select_temp[1])], self.outText)
        self.outText.PopupMenu(menu, event.GetPosition())
        menu.Destroy()


class detailsFrame(wx.Frame):
    
    def __init__(self):
        wx.Frame.__init__(self, None, title="Documentation page",
                          pos=wx.DefaultPosition,
                          size=wx.Size(1000, 700))
                        #   style=wx.MINIMIZE_BOX |
                        #   wx.SYSTEM_MENU |
                        #   wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        if getattr(sys, 'frozen', False):
            # frozen
            package_directory = os.path.dirname(sys.executable)
        else:
            # unfrozen
            package_directory = os.path.dirname(os.path.abspath(__file__))
        
        ico = wx.Icon(os.path.join(package_directory, "stuff",
                                   "icon.ico"), wx.BITMAP_TYPE_ICO)
        self.SetIcon(ico)
        
        details_doc_loc = os.path.join(package_directory, "stuff","doc.txt")

        self.panel = detailsPanel(self, details_doc_loc)

        self.Show()

    def Destroy(self):
        return wx.Frame.Destroy(self)


class detailsPanel(wx.Panel):
    def __init__(self, parent, details_doc_loc):

        wx.Panel.__init__(self, parent)
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        
        self.details_doc_loc = details_doc_loc
        
        mainMainS = wx.FlexGridSizer(1, 1, 0, 0)
        mainMainS.SetFlexibleDirection(wx.BOTH)
        mainMainS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)
        
        self.outText = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString,
                                   wx.DefaultPosition,
                                   wx.DefaultSize, wx.TE_MULTILINE |
                                   wx.TE_READONLY | wx.TE_WORDWRAP)
        self.outText.Bind(wx.EVT_CHAR, self.OnSelectAll)
        self.outText.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        
        mainMainS.AddMany([(self.outText, 1, wx.EXPAND, 5)])
        
        mainMainS.AddGrowableRow(0, 1)
        mainMainS.AddGrowableCol(0, 1)
        
        font1 = wx.Font(13, wx.MODERN, wx.NORMAL,
                        wx.NORMAL, False, u'Consolas')
        self.outText.SetFont(font1)
        
        with open(self.details_doc_loc) as fobj:
            for line in fobj:
                self.outText.WriteText(line)
        
        self.SetSizer(mainMainS)
        self.Layout()
        
    def OnSelectAll(self, event):
        keyInput = event.GetKeyCode()
        if keyInput == 1:  # 1 stands for 'ctrl+a'
            self.outText.SelectAll()
            pass
        event.Skip()

    def OnRightDown(self, event):
        select_temp = self.outText.GetSelection()
        menu = MyPopupMenu1(self.outText.GetValue(),
                            self.outText.GetValue()[int(select_temp[0]):
                                int(select_temp[1])], self.outText)
        self.outText.PopupMenu(menu, event.GetPosition())
        menu.Destroy()


class MainFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, None, title='SofQ_Calib',
                          size=wx.Size(1200, 750),
                          style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        if getattr(sys, 'frozen', False):
            # frozen
            package_directory = os.path.dirname(sys.executable)
        else:
            # unfrozen
            package_directory = os.path.dirname(os.path.abspath(__file__))

        # package_directory = os.path.dirname(os.path.abspath(__file__))
        # package_directory = os.path.dirname(os.path.abspath('.'))
        ico = wx.Icon(os.path.join(package_directory, "stuff",
                                   "icon.ico"), wx.BITMAP_TYPE_ICO)
        self.SetIcon(ico)
        
        path_hist_sofq = os.path.join(package_directory, "stuff", ".last_sofq")
        path_hist_bragg = os.path.join(package_directory, "stuff", ".last_bragg")

        self.panel = CanvasPanel(self, path_hist_sofq, path_hist_bragg)
        self.panel.draw()

        self.help_frame = []
        self.details_frame = []
        
        self.InitUI()

    def InitUI(self):

        menubar = wx.MenuBar()
        
        fileMenu = wx.Menu()
        quitItem = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        
        helpMenu = wx.Menu()
        helpItem = helpMenu.Append(wx.ID_ANY, 'Help', 'Help page')
        detailsItem = helpMenu.Append(wx.ID_ANY, 'Documentation', 'Technical details')
        aboutItem = helpMenu.Append(wx.ID_ANY, 'About', 'About page')
        
        menubar.Append(fileMenu, '&File')
        menubar.Append(helpMenu, '&Help')
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.OnCloseWindow, quitItem)
        self.Bind(wx.EVT_MENU, self.open_help_frame, helpItem)
        self.Bind(wx.EVT_MENU, self.open_details_frame, detailsItem)
        self.Bind(wx.EVT_MENU, self.open_about_frame, aboutItem)

    def open_help_frame(self, event):
        self.help_frame.append(helpFrame())
        
    def open_details_frame(self, event):
        self.details_frame.append(detailsFrame())
        
    def open_about_frame(self, event):
        text_body = "Version: 1.0" + "\n" + \
                    "Date: 27-Sep-19" + "\n" + \
                    "Platform: Windows/Linux/MacOS" + "\n" + \
                    "Author: Yuanpeng Zhang" + "\n" +\
                    "Affiliation: NIST & ORNL" + "\n" + \
                    "Contact: zyroc1990@gmail.com"
            
        wx.MessageBox(text_body, 'About', wx.OK | wx.ICON_INFORMATION)

    def OnCloseWindow(self, event):
        try:
            for item in self.help_frame:
                try:
                    item.Destroy()
                except RuntimeError:
                    pass
                except AttributeError:
                    pass
        except RuntimeError:
            pass
        except AttributeError:
            pass
        
        try:
            for item in self.details_frame:
                try:
                    item.Destroy()
                except RuntimeError:
                    pass
                except AttributeError:
                    pass
        except RuntimeError:
            pass
        except AttributeError:
            pass
        
        try:
            for item in self.panel.frame:
                try:
                    item.Destroy()
                except RuntimeError:
                    pass
                except AttributeError:
                    pass
        except RuntimeError:
            pass
        except AttributeError:
            pass
        
        self.Destroy()
    
    def Destroy(self):
        return wx.Frame.Destroy(self)

def main():
    app = wx.App()
    fr = MainFrame(wx.Frame)
    fr.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()
