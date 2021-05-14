import wx
import wx.aui
import sys
import os
import platform

if platform.system() == "Windows":
    import ctypes
    myappid = 'ornl.rmcp2p.1.0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


class nr_v6_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        mainS = wx.FlexGridSizer(1, 2, 0, 0)
        mainS.SetFlexibleDirection(wx.BOTH)
        mainS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subSL = wx.FlexGridSizer(3, 1, 0, 0)
        subSL.SetFlexibleDirection(wx.BOTH)
        subSL.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subSL1a = wx.FlexGridSizer(1, 3, 0, 0)
        subSL1a.SetFlexibleDirection(wx.BOTH)
        subSL1a.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        fn_static = wx.StaticText(
            self, wx.ID_ANY, u"File name: ",
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.fn_text = wx.TextCtrl(self, wx.ID_ANY,
                                   wx.EmptyString,
                                   wx.DefaultPosition, wx.DefaultSize)
        fileBButton = wx.Button(
            self, wx.ID_ANY, u"Browse file", wx.DefaultPosition,
            wx.DefaultSize, 0)

        subSL1a.AddMany([(fn_static, 1, wx.EXPAND, 5),
                        (self.fn_text, 1, wx.EXPAND, 5),
                        (fileBButton, 1, wx.EXPAND, 5)])
        subSL1a.AddGrowableCol(1, 1)

        subSL1 = wx.FlexGridSizer(2, 1, 0, 0)
        subSL1.SetFlexibleDirection(wx.BOTH)
        subSL1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        afButton = wx.Button(
            self, wx.ID_ANY, u"Add data file to project", wx.DefaultPosition,
            wx.DefaultSize, 0)

        subSL1.AddMany([(subSL1a, 1, wx.EXPAND, 5),
                        (afButton, 1, wx.EXPAND, 5)])
        subSL1.AddGrowableCol(0, 1)

        subSL2 = wx.FlexGridSizer(5, 4, 0, 0)
        subSL2.SetFlexibleDirection(wx.BOTH)
        subSL2.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        dt_static = wx.StaticText(
            self, wx.ID_ANY, u"Data type:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.dt_comb = wx.ComboBox(self, id=wx.ID_ANY, value="G(r)",
                                   pos=wx.DefaultPosition,
                                   size=wx.DefaultSize,
                                   choices=['G(r)', 'D(r)', 'G(r)P',
                                            'T(r)', 'G\'(r)'],
                                   validator=wx.DefaultValidator,
                                   style=wx.CB_READONLY)
        typeQButton = wx.Button(
            self, wx.ID_ANY, u"<-?", wx.DefaultPosition,
            wx.DefaultSize, 0)

        subSL2a = wx.FlexGridSizer(1, 2, 0, 0)
        subSL2a.SetFlexibleDirection(wx.BOTH)
        subSL2a.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subSL2a.AddMany([(self.dt_comb, 1, wx.EXPAND, 5),
                         (typeQButton, 1, wx.EXPAND, 5)])
        subSL2a.AddGrowableCol(0, 1)
        subSL2a.AddGrowableCol(1, 1)

        ft_static = wx.StaticText(
            self, wx.ID_ANY, u"Fit type:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.ft_comb = wx.ComboBox(self, id=wx.ID_ANY, value="G(r)",
                                   pos=wx.DefaultPosition,
                                   size=wx.DefaultSize,
                                   choices=['G(r)', 'D(r)', 'G(r)P',
                                            'T(r)', 'G\'(r)'],
                                   validator=wx.DefaultValidator,
                                   style=wx.CB_READONLY)
        typeQ1Button = wx.Button(
            self, wx.ID_ANY, u"<-?", wx.DefaultPosition,
            wx.DefaultSize, 0)

        subSL2b = wx.FlexGridSizer(1, 2, 0, 0)
        subSL2b.SetFlexibleDirection(wx.BOTH)
        subSL2b.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subSL2b.AddMany([(self.ft_comb, 1, wx.EXPAND, 5),
                         (typeQ1Button, 1, wx.EXPAND, 5)])
        subSL2b.AddGrowableCol(0, 1)
        subSL2b.AddGrowableCol(1, 1)

        fo_static = wx.StaticText(
            self, wx.ID_ANY, u"Fit offset:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.fo_comb = wx.ComboBox(self, id=wx.ID_ANY, value="No",
                                   pos=wx.DefaultPosition,
                                   size=wx.DefaultSize,
                                   choices=['No', 'Yes'],
                                   validator=wx.DefaultValidator,
                                   style=wx.CB_READONLY)

        fs_static = wx.StaticText(
            self, wx.ID_ANY, u"Fit scale:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.fs_comb = wx.ComboBox(self, id=wx.ID_ANY, value="No",
                                   pos=wx.DefaultPosition,
                                   size=wx.DefaultSize,
                                   choices=['No', 'Yes'],
                                   validator=wx.DefaultValidator,
                                   style=wx.CB_READONLY)

        co_static = wx.StaticText(
            self, wx.ID_ANY, u"Constant offset:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.co_text = wx.TextCtrl(self, wx.ID_ANY,
                                   wx.EmptyString,
                                   wx.DefaultPosition, wx.DefaultSize)

        weight_static = wx.StaticText(
            self, wx.ID_ANY, u"Weight:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.weight_text = wx.TextCtrl(self, wx.ID_ANY,
                                       wx.EmptyString,
                                       wx.DefaultPosition, wx.DefaultSize)

        sp_static = wx.StaticText(
            self, wx.ID_ANY, u"Start point:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.sp_text = wx.TextCtrl(self, wx.ID_ANY,
                                   wx.EmptyString,
                                   wx.DefaultPosition, wx.DefaultSize)

        ep_static = wx.StaticText(
            self, wx.ID_ANY, u"End point:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.ep_text = wx.TextCtrl(self, wx.ID_ANY,
                                   wx.EmptyString,
                                   wx.DefaultPosition, wx.DefaultSize)

        subSL2.AddMany([(dt_static, 1, wx.EXPAND, 5),
                        (subSL2a, 1, wx.EXPAND, 5),
                        (ft_static, 1, wx.EXPAND, 5),
                        (subSL2b, 1, wx.EXPAND, 5),
                        (fo_static, 1, wx.EXPAND, 5),
                        (self.fo_comb, 1, wx.EXPAND, 5),
                        (fs_static, 1, wx.EXPAND, 5),
                        (self.fs_comb, 1, wx.EXPAND, 5),
                        (co_static, 1, wx.EXPAND, 5),
                        (self.co_text, 1, wx.EXPAND, 5),
                        (weight_static, 1, wx.EXPAND, 5),
                        (self.weight_text, 1, wx.EXPAND, 5),
                        (sp_static, 1, wx.EXPAND, 5),
                        (self.sp_text, 1, wx.EXPAND, 5),
                        (ep_static, 1, wx.EXPAND, 5),
                        (self.ep_text, 1, wx.EXPAND, 5)])
        subSL2.AddGrowableCol(0, 1)
        subSL2.AddGrowableCol(1, 1)
        subSL2.AddGrowableCol(2, 1)
        subSL2.AddGrowableCol(3, 1)

        prepButton = wx.Button(
            self, wx.ID_ANY, u"Prepare->", wx.DefaultPosition,
            wx.DefaultSize, 0)

        subSL.AddMany([(subSL1, 1, wx.EXPAND, 5),
                       (subSL2, 1, wx.EXPAND, 5),
                       (prepButton, 1, wx.EXPAND, 5)])
        subSL.AddGrowableCol(0, 1)

        subSR = wx.FlexGridSizer(3, 1, 0, 0)
        subSR.SetFlexibleDirection(wx.BOTH)
        subSR.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        ec_static = wx.StaticText(
            self, wx.ID_ANY, u"Editable composer:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.ec_text = wx.TextCtrl(self, wx.ID_ANY,
                                   wx.EmptyString,
                                   wx.DefaultPosition, wx.DefaultSize)
        compButton = wx.Button(
            self, wx.ID_ANY, u"Compose", wx.DefaultPosition,
            wx.DefaultSize, 0)

        subSR.AddMany([(ec_static, 1, wx.EXPAND, 5),
                       (self.ec_text, 1, wx.EXPAND, 5),
                       (compButton, 1, wx.EXPAND, 5)])
        subSR.AddGrowableRow(1, 1)
        subSR.AddGrowableCol(0, 1)

        mainS.AddMany([(subSL, 1, wx.EXPAND, 5),
                       (subSR, 1, wx.EXPAND, 5)])
        mainS.AddGrowableRow(0, 1)
        # mainS.AddGrowableCol(0, 1)
        mainS.AddGrowableCol(1, 1)

        self.SetSizer(mainS)
        self.Layout()


class xray_v6_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        mainS = wx.FlexGridSizer(1, 2, 0, 0)
        mainS.SetFlexibleDirection(wx.BOTH)
        mainS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subSL = wx.FlexGridSizer(4, 1, 0, 0)
        subSL.SetFlexibleDirection(wx.BOTH)
        subSL.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subSL1 = wx.FlexGridSizer(1, 3, 0, 0)
        subSL1.SetFlexibleDirection(wx.BOTH)
        subSL1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        fn_static = wx.StaticText(
            self, wx.ID_ANY, u"File name: ",
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.fn_text = wx.TextCtrl(self, wx.ID_ANY,
                                   wx.EmptyString,
                                   wx.DefaultPosition, wx.DefaultSize)
        fileBButton = wx.Button(
            self, wx.ID_ANY, u"Browse file", wx.DefaultPosition,
            wx.DefaultSize, 0)

        subSL1.AddMany([(fn_static, 1, wx.EXPAND, 5),
                        (self.fn_text, 1, wx.EXPAND, 5),
                        (fileBButton, 1, wx.EXPAND, 5)])
        subSL1.AddGrowableCol(1, 1)

        subSL2 = wx.FlexGridSizer(5, 4, 0, 0)
        subSL2.SetFlexibleDirection(wx.BOTH)
        subSL2.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        dt_static = wx.StaticText(
            self, wx.ID_ANY, u"Data type:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.dt_comb = wx.ComboBox(self, id=wx.ID_ANY, value="F(Q)",
                                   pos=wx.DefaultPosition,
                                   size=wx.DefaultSize,
                                   choices=['F(Q)'],
                                   validator=wx.DefaultValidator,
                                   style=wx.CB_READONLY)
        typeQButton = wx.Button(
            self, wx.ID_ANY, u"<-?", wx.DefaultPosition,
            wx.DefaultSize, 0)

        subSL2a = wx.FlexGridSizer(1, 2, 0, 0)
        subSL2a.SetFlexibleDirection(wx.BOTH)
        subSL2a.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subSL2a.AddMany([(self.dt_comb, 1, wx.EXPAND, 5),
                         (typeQButton, 1, wx.EXPAND, 5)])
        subSL2a.AddGrowableCol(0, 1)
        subSL2a.AddGrowableCol(1, 1)

        ft_static = wx.StaticText(
            self, wx.ID_ANY, u"Fit type:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.ft_comb = wx.ComboBox(self, id=wx.ID_ANY, value="F(Q)",
                                   pos=wx.DefaultPosition,
                                   size=wx.DefaultSize,
                                   choices=['F(Q)'],
                                   validator=wx.DefaultValidator,
                                   style=wx.CB_READONLY)
        typeQ1Button = wx.Button(
            self, wx.ID_ANY, u"<-?", wx.DefaultPosition,
            wx.DefaultSize, 0)

        subSL2b = wx.FlexGridSizer(1, 2, 0, 0)
        subSL2b.SetFlexibleDirection(wx.BOTH)
        subSL2b.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subSL2b.AddMany([(self.ft_comb, 1, wx.EXPAND, 5),
                         (typeQ1Button, 1, wx.EXPAND, 5)])
        subSL2b.AddGrowableCol(0, 1)
        subSL2b.AddGrowableCol(1, 1)

        fo_static = wx.StaticText(
            self, wx.ID_ANY, u"Fit offset:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.fo_comb = wx.ComboBox(self, id=wx.ID_ANY, value="No",
                                   pos=wx.DefaultPosition,
                                   size=wx.DefaultSize,
                                   choices=['No', 'Yes'],
                                   validator=wx.DefaultValidator,
                                   style=wx.CB_READONLY)

        fs_static = wx.StaticText(
            self, wx.ID_ANY, u"Fit scale:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.fs_comb = wx.ComboBox(self, id=wx.ID_ANY, value="No",
                                   pos=wx.DefaultPosition,
                                   size=wx.DefaultSize,
                                   choices=['No', 'Yes'],
                                   validator=wx.DefaultValidator,
                                   style=wx.CB_READONLY)

        co_static = wx.StaticText(
            self, wx.ID_ANY, u"Constant offset:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.co_text = wx.TextCtrl(self, wx.ID_ANY,
                                   wx.EmptyString,
                                   wx.DefaultPosition, wx.DefaultSize)

        conv_static = wx.StaticText(
            self, wx.ID_ANY, u"Convolve:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.conv_comb = wx.ComboBox(self, id=wx.ID_ANY, value="Yes",
                                     pos=wx.DefaultPosition,
                                     size=wx.DefaultSize,
                                     choices=['Yes', 'No'],
                                     validator=wx.DefaultValidator,
                                     style=wx.CB_READONLY)
        convQButton = wx.Button(
            self, wx.ID_ANY, u"<-?", wx.DefaultPosition,
            wx.DefaultSize, 0)

        subSL2c = wx.FlexGridSizer(1, 2, 0, 0)
        subSL2c.SetFlexibleDirection(wx.BOTH)
        subSL2c.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subSL2c.AddMany([(self.conv_comb, 1, wx.EXPAND, 5),
                         (convQButton, 1, wx.EXPAND, 5)])
        subSL2c.AddGrowableCol(0, 1)
        subSL2c.AddGrowableCol(1, 1)

        normt_static = wx.StaticText(
            self, wx.ID_ANY, u"Norm type:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.normt_comb = wx.ComboBox(self, id=wx.ID_ANY, value="<f^2>",
                                      pos=wx.DefaultPosition,
                                      size=wx.DefaultSize,
                                      choices=['<f^2>', '<f>^2'],
                                      validator=wx.DefaultValidator,
                                      style=wx.CB_READONLY)
        normtQButton = wx.Button(
            self, wx.ID_ANY, u"<-?", wx.DefaultPosition,
            wx.DefaultSize, 0)

        subSL2d = wx.FlexGridSizer(1, 2, 0, 0)
        subSL2d.SetFlexibleDirection(wx.BOTH)
        subSL2d.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subSL2d.AddMany([(self.normt_comb, 1, wx.EXPAND, 5),
                         (normtQButton, 1, wx.EXPAND, 5)])
        subSL2d.AddGrowableCol(0, 1)
        subSL2d.AddGrowableCol(1, 1)

        rso_static = wx.StaticText(
            self, wx.ID_ANY, u"r-space only:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.rso_comb = wx.ComboBox(self, id=wx.ID_ANY, value="No",
                                    pos=wx.DefaultPosition,
                                    size=wx.DefaultSize,
                                    choices=['No', 'Yes'],
                                    validator=wx.DefaultValidator,
                                    style=wx.CB_READONLY)

        subSL2.AddMany([(dt_static, 1, wx.EXPAND, 5),
                        (subSL2a, 1, wx.EXPAND, 5),
                        (ft_static, 1, wx.EXPAND, 5),
                        (subSL2b, 1, wx.EXPAND, 5),
                        (fo_static, 1, wx.EXPAND, 5),
                        (self.fo_comb, 1, wx.EXPAND, 5),
                        (fs_static, 1, wx.EXPAND, 5),
                        (self.fs_comb, 1, wx.EXPAND, 5),
                        (co_static, 1, wx.EXPAND, 5),
                        (self.co_text, 1, wx.EXPAND, 5),
                        (conv_static, 1, wx.EXPAND, 5),
                        (subSL2c, 1, wx.EXPAND, 5),
                        (normt_static, 1, wx.EXPAND, 5),
                        (subSL2d, 1, wx.EXPAND, 5),
                        (rso_static, 1, wx.EXPAND, 5),
                        (self.rso_comb, 1, wx.EXPAND, 5)])
        subSL2.AddGrowableCol(0, 1)
        subSL2.AddGrowableCol(1, 1)
        subSL2.AddGrowableCol(2, 1)
        subSL2.AddGrowableCol(3, 1)

        subSL3 = wx.FlexGridSizer(4, 5, 0, 0)
        subSL3.SetFlexibleDirection(wx.BOTH)
        subSL3.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        xqf_static = wx.StaticText(
            self, wx.ID_ANY, u"X-ray Q-space fit:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.xqf_text1 = wx.TextCtrl(self, wx.ID_ANY,
                                     wx.EmptyString,
                                     pos=wx.DefaultPosition,
                                     size=(75, -1))
        self.xqf_text2 = wx.TextCtrl(self, wx.ID_ANY,
                                     wx.EmptyString,
                                     pos=wx.DefaultPosition,
                                     size=(75, -1))
        self.xqf_text3 = wx.TextCtrl(self, wx.ID_ANY,
                                     wx.EmptyString,
                                     pos=wx.DefaultPosition,
                                     size=(75, -1))
        xqfUButton = wx.Button(
            self, wx.ID_ANY, u"Update", wx.DefaultPosition,
            wx.DefaultSize, 0)

        xqp_static = wx.StaticText(
            self, wx.ID_ANY, u"X-ray Q-space Paras:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.xqp_comb = wx.ComboBox(self, id=wx.ID_ANY, value="1",
                                    pos=wx.DefaultPosition,
                                    size=wx.DefaultSize,
                                    choices=['1'],
                                    validator=wx.DefaultValidator,
                                    style=wx.CB_READONLY)
        self.xqp_text1 = wx.TextCtrl(self, wx.ID_ANY,
                                     wx.EmptyString,
                                     pos=wx.DefaultPosition,
                                     size=(75, -1))
        self.xqp_text2 = wx.TextCtrl(self, wx.ID_ANY,
                                     wx.EmptyString,
                                     pos=wx.DefaultPosition,
                                     size=(75, -1))
        self.xqp_text3 = wx.TextCtrl(self, wx.ID_ANY,
                                     wx.EmptyString,
                                     pos=wx.DefaultPosition,
                                     size=(75, -1))

        xrf_static = wx.StaticText(
            self, wx.ID_ANY, u"X-ray r-space fit:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.xrf_text1 = wx.TextCtrl(self, wx.ID_ANY,
                                     wx.EmptyString,
                                     pos=wx.DefaultPosition,
                                     size=(75, -1))
        self.xrf_text2 = wx.TextCtrl(self, wx.ID_ANY,
                                     wx.EmptyString,
                                     pos=wx.DefaultPosition,
                                     size=(75, -1))
        self.xrf_text3 = wx.TextCtrl(self, wx.ID_ANY,
                                     wx.EmptyString,
                                     pos=wx.DefaultPosition,
                                     size=(75, -1))
        xrfUButton = wx.Button(
            self, wx.ID_ANY, u"Update", wx.DefaultPosition,
            wx.DefaultSize, 0)

        xrp_static = wx.StaticText(
            self, wx.ID_ANY, u"X-ray r-space Paras:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.xrp_comb = wx.ComboBox(self, id=wx.ID_ANY, value="1",
                                    pos=wx.DefaultPosition,
                                    size=wx.DefaultSize,
                                    choices=['1'],
                                    validator=wx.DefaultValidator,
                                    style=wx.CB_READONLY)
        self.xrp_text1 = wx.TextCtrl(self, wx.ID_ANY,
                                     wx.EmptyString,
                                     pos=wx.DefaultPosition,
                                     size=(75, -1))
        self.xrp_text2 = wx.TextCtrl(self, wx.ID_ANY,
                                     wx.EmptyString,
                                     pos=wx.DefaultPosition,
                                     size=(75, -1))
        self.xrp_text3 = wx.TextCtrl(self, wx.ID_ANY,
                                     wx.EmptyString,
                                     pos=wx.DefaultPosition,
                                     size=(75, -1))

        subSL3.AddMany([(xqf_static, 1, wx.EXPAND, 5),
                        (self.xqf_text1, 1, wx.EXPAND, 5),
                        (self.xqf_text2, 1, wx.EXPAND, 5),
                        (self.xqf_text3, 1, wx.EXPAND, 5),
                        (xqfUButton, 1, wx.EXPAND, 5),
                        (xqp_static, 1, wx.EXPAND, 5),
                        (self.xqp_comb, 1, wx.EXPAND, 5),
                        (self.xqp_text1, 1, wx.EXPAND, 5),
                        (self.xqp_text2, 1, wx.EXPAND, 5),
                        (self.xqp_text3, 1, wx.EXPAND, 5),
                        (xrf_static, 1, wx.EXPAND, 5),
                        (self.xrf_text1, 1, wx.EXPAND, 5),
                        (self.xrf_text2, 1, wx.EXPAND, 5),
                        (self.xrf_text3, 1, wx.EXPAND, 5),
                        (xrfUButton, 1, wx.EXPAND, 5),
                        (xrp_static, 1, wx.EXPAND, 5),
                        (self.xrp_comb, 1, wx.EXPAND, 5),
                        (self.xrp_text1, 1, wx.EXPAND, 5),
                        (self.xrp_text2, 1, wx.EXPAND, 5),
                        (self.xrp_text3, 1, wx.EXPAND, 5)])
        subSL3.AddGrowableCol(0, 1)
        subSL3.AddGrowableCol(1, 1)
        subSL3.AddGrowableCol(2, 1)
        subSL3.AddGrowableCol(3, 1)

        subSRa0 = wx.FlexGridSizer(1, 2, 0, 0)
        subSRa0.SetFlexibleDirection(wx.BOTH)
        subSRa0.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        xIButton = wx.Button(
            self, wx.ID_ANY, u"Learn about input boxes",
            wx.DefaultPosition,
            wx.DefaultSize, 0)
        afButton = wx.Button(
            self, wx.ID_ANY, u"Add data file to project",
            wx.DefaultPosition,
            wx.DefaultSize, 0)

        subSRa0.AddMany([(afButton, 1, wx.EXPAND, 5),
                         (xIButton, 1, wx.EXPAND, 5)])
        subSRa0.AddGrowableCol(0, 1)
        subSRa0.AddGrowableCol(1, 1)

        subSL.AddMany([(subSL1, 1, wx.EXPAND, 5),
                       (subSRa0, 1, wx.EXPAND, 5),
                       (subSL2, 1, wx.EXPAND, 5),
                       (subSL3, 1, wx.EXPAND, 5)])
        # subSL.AddGrowableRow(3, 1)
        subSL.AddGrowableCol(0, 1)

        subSR = wx.FlexGridSizer(4, 1, 0, 0)
        subSR.SetFlexibleDirection(wx.BOTH)
        subSR.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        prepButton = wx.Button(
            self, wx.ID_ANY, u"Prepare\\|/", wx.DefaultPosition,
            wx.DefaultSize, 0)

        ec_static = wx.StaticText(
            self, wx.ID_ANY, u"Editable composer:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.ec_text = wx.TextCtrl(self, wx.ID_ANY,
                                   wx.EmptyString,
                                   wx.DefaultPosition, wx.DefaultSize)
        compButton = wx.Button(
            self, wx.ID_ANY, u"Compose", wx.DefaultPosition,
            wx.DefaultSize, 0)

        subSR.AddMany([(prepButton, 1, wx.EXPAND, 5),
                       (ec_static, 1, wx.EXPAND, 5),
                       (self.ec_text, 1, wx.EXPAND, 5),
                       (compButton, 1, wx.EXPAND, 5)])
        subSR.AddGrowableRow(2, 1)
        subSR.AddGrowableCol(0, 1)

        mainS.AddMany([(subSL, 1, wx.EXPAND, 5),
                       (subSR, 1, wx.EXPAND, 5)])
        # mainS.AddGrowableRow(0, 1)
        # mainS.AddGrowableCol(0, 1)
        mainS.AddGrowableCol(1, 1)

        self.SetSizer(mainS)
        self.Layout()


class bragg_v6_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        mainMainS = wx.FlexGridSizer(1, 2, 0, 0)
        mainMainS.SetFlexibleDirection(wx.BOTH)
        mainMainS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        mainS = wx.FlexGridSizer(3, 1, 0, 0)
        mainS.SetFlexibleDirection(wx.BOTH)
        mainS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subS1 = wx.FlexGridSizer(2, 2, 0, 0)
        subS1.SetFlexibleDirection(wx.BOTH)
        subS1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subS1a = wx.FlexGridSizer(1, 2, 0, 0)
        subS1a.SetFlexibleDirection(wx.BOTH)
        subS1a.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        pt_static = wx.StaticText(
            self, wx.ID_ANY, u"Bragg profile:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.pt_comb = wx.ComboBox(self, id=wx.ID_ANY, value="GSAS3",
                                   pos=wx.DefaultPosition,
                                   size=wx.DefaultSize,
                                   choices=['GSAS1', 'GSAS2', 'GSAS3',
                                            'XRAY2', 'GSAS1_ABS0',
                                            'GSAS2_ABS0', 'GSAS3_ABS0',
                                            'XRAY_ABS0'],
                                   validator=wx.DefaultValidator,
                                   style=wx.CB_READONLY)
        subS1a.AddMany([(pt_static, 1, wx.EXPAND, 5),
                        (self.pt_comb, 1, wx.EXPAND, 5)])
        subS1a.AddGrowableCol(0, 1)
        subS1a.AddGrowableCol(1, 1)

        subS1b = wx.FlexGridSizer(1, 2, 0, 0)
        subS1b.SetFlexibleDirection(wx.BOTH)
        subS1b.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        fb_static = wx.StaticText(
            self, wx.ID_ANY, u"Fast Bragg:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.fb_comb = wx.ComboBox(self, id=wx.ID_ANY, value="Yes",
                                   pos=wx.DefaultPosition,
                                   size=wx.DefaultSize,
                                   choices=['Yes', 'No'],
                                   validator=wx.DefaultValidator,
                                   style=wx.CB_READONLY)
        subS1b.AddMany([(fb_static, 1, wx.EXPAND, 5),
                        (self.fb_comb, 1, wx.EXPAND, 5)])
        subS1b.AddGrowableCol(0, 1)
        subS1b.AddGrowableCol(1, 1)

        lgfButton = wx.Button(
            self, wx.ID_ANY, u"Load GSAS files", wx.DefaultPosition,
            wx.DefaultSize, 0)
        ltfButton = wx.Button(
            self, wx.ID_ANY, u"Load Topas files", wx.DefaultPosition,
            wx.DefaultSize, 0)

        subS1.AddMany([(subS1a, 1, wx.EXPAND, 5),
                       (subS1b, 1, wx.EXPAND, 5),
                       (lgfButton, 1, wx.EXPAND, 5),
                       (ltfButton, 1, wx.EXPAND, 5)])
        subS1.AddGrowableCol(0, 1)
        subS1.AddGrowableCol(1, 1)

        subS2 = wx.FlexGridSizer(4, 4, 0, 0)
        subS2.SetFlexibleDirection(wx.BOTH)
        subS2.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        spc_static = wx.StaticText(
            self, wx.ID_ANY, u"Supercell:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.spc_1 = wx.TextCtrl(self, wx.ID_ANY,
                                 wx.EmptyString,
                                 wx.DefaultPosition, wx.DefaultSize)
        self.spc_2 = wx.TextCtrl(self, wx.ID_ANY,
                                 wx.EmptyString,
                                 wx.DefaultPosition, wx.DefaultSize)
        self.spc_3 = wx.TextCtrl(self, wx.ID_ANY,
                                 wx.EmptyString,
                                 wx.DefaultPosition, wx.DefaultSize)
        weight_static = wx.StaticText(
            self, wx.ID_ANY, u"Weight:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.weight_text = wx.TextCtrl(self, wx.ID_ANY,
                                       wx.EmptyString,
                                       wx.DefaultPosition, wx.DefaultSize)
        md_static = wx.StaticText(
            self, wx.ID_ANY, u"Min d-spacing:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.md_text = wx.TextCtrl(self, wx.ID_ANY,
                                   wx.EmptyString,
                                   wx.DefaultPosition, wx.DefaultSize)
        ws_static = wx.StaticText(
            self, wx.ID_ANY, u"Weight residual:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.ws_comb = wx.ComboBox(self, id=wx.ID_ANY, value="Yes",
                                   pos=wx.DefaultPosition,
                                   size=wx.DefaultSize,
                                   choices=['Yes', 'No'],
                                   validator=wx.DefaultValidator,
                                   style=wx.CB_READONLY)
        wsQButton = wx.Button(
            self, wx.ID_ANY, u"<-?", wx.DefaultPosition,
            wx.DefaultSize, 0)
        h1_static = wx.StaticText(
            self, wx.ID_ANY, u"", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        rc_static = wx.StaticText(
            self, wx.ID_ANY, u"Recalculate:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.rc_comb = wx.ComboBox(self, id=wx.ID_ANY, value="Yes",
                                   pos=wx.DefaultPosition,
                                   size=wx.DefaultSize,
                                   choices=['Yes', 'No'],
                                   validator=wx.DefaultValidator,
                                   style=wx.CB_READONLY)
        rcQButton = wx.Button(
            self, wx.ID_ANY, u"<-?", wx.DefaultPosition,
            wx.DefaultSize, 0)
        h2_static = wx.StaticText(
            self, wx.ID_ANY, u"", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)

        subS2.AddMany([(spc_static, 1, wx.EXPAND, 5),
                       (self.spc_1, 1, wx.EXPAND, 5),
                       (self.spc_2, 1, wx.EXPAND, 5),
                       (self.spc_3, 1, wx.EXPAND, 5),
                       (weight_static, 1, wx.EXPAND, 5),
                       (self.weight_text, 1, wx.EXPAND, 5),
                       (md_static, 1, wx.EXPAND, 5),
                       (self.md_text, 1, wx.EXPAND, 5),
                       (ws_static, 1, wx.EXPAND, 5),
                       (self.ws_comb, 1, wx.EXPAND, 5),
                       (wsQButton, 1, wx.EXPAND, 5),
                       (h1_static, 1, wx.EXPAND, 5),
                       (rc_static, 1, wx.EXPAND, 5),
                       (self.rc_comb, 1, wx.EXPAND, 5),
                       (rcQButton, 1, wx.EXPAND, 5),
                       (h2_static, 1, wx.EXPAND, 5)])
        subS2.AddGrowableCol(0, 1)
        subS2.AddGrowableCol(1, 1)
        subS2.AddGrowableCol(2, 1)
        subS2.AddGrowableCol(3, 1)

        prepButton = wx.Button(
            self, wx.ID_ANY, u"Prepare->", wx.DefaultPosition,
            wx.DefaultSize, 0)

        mainS.AddMany([(subS1, 1, wx.EXPAND, 5),
                       (subS2, 1, wx.EXPAND, 5),
                       (prepButton, 1, wx.EXPAND, 5)])

        ec_static = wx.StaticText(
            self, wx.ID_ANY, u"Editable composer:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.ec_text = wx.TextCtrl(self, wx.ID_ANY,
                                   wx.EmptyString,
                                   wx.DefaultPosition, wx.DefaultSize)
        compButton = wx.Button(
            self, wx.ID_ANY, u"Compose", wx.DefaultPosition,
            wx.DefaultSize, 0)

        subSR = wx.FlexGridSizer(3, 1, 0, 0)
        subSR.SetFlexibleDirection(wx.BOTH)
        subSR.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subSR.AddMany([(ec_static, 1, wx.EXPAND, 5),
                       (self.ec_text, 1, wx.EXPAND, 5),
                       (compButton, 1, wx.EXPAND, 5)])
        subSR.AddGrowableRow(1, 1)
        subSR.AddGrowableCol(0, 1)

        mainMainS.AddMany([(mainS, 1, wx.EXPAND, 5),
                           (subSR, 1, wx.EXPAND, 5)])
        mainMainS.AddGrowableRow(0, 1)
        mainMainS.AddGrowableCol(1, 1)

        self.SetSizer(mainMainS)
        self.Layout()


class exafs_v6_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        mainS = wx.FlexGridSizer(1, 2, 0, 0)
        mainS.SetFlexibleDirection(wx.BOTH)
        mainS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        mainSL = wx.FlexGridSizer(5, 1, 0, 0)
        mainSL.SetFlexibleDirection(wx.BOTH)
        mainSL.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subSL1 = wx.FlexGridSizer(1, 3, 0, 0)
        subSL1.SetFlexibleDirection(wx.BOTH)
        subSL1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        fn_static = wx.StaticText(
            self, wx.ID_ANY, u"File name: ",
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.fn_text = wx.TextCtrl(self, wx.ID_ANY,
                                   wx.EmptyString,
                                   wx.DefaultPosition, wx.DefaultSize)
        fileBButton = wx.Button(
            self, wx.ID_ANY, u"Browse file", wx.DefaultPosition,
            wx.DefaultSize, 0)

        subSL1.AddMany([(fn_static, 1, wx.EXPAND, 5),
                        (self.fn_text, 1, wx.EXPAND, 5),
                        (fileBButton, 1, wx.EXPAND, 5)])
        subSL1.AddGrowableCol(1, 1)

        addTPButton = wx.Button(
            self, wx.ID_ANY, u"Add file to project", wx.DefaultPosition,
            wx.DefaultSize, 0)

        subSL2 = wx.FlexGridSizer(1, 4, 0, 0)
        subSL2.SetFlexibleDirection(wx.BOTH)
        subSL2.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        absT_static = wx.StaticText(
            self, wx.ID_ANY, u"Absorbing atom type: ",
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.absT_comb = wx.ComboBox(self, id=wx.ID_ANY, value="",
                                     pos=wx.DefaultPosition,
                                     size=wx.DefaultSize,
                                     choices=[''],
                                     validator=wx.DefaultValidator,
                                     style=wx.CB_READONLY)
        fs_static = wx.StaticText(
            self, wx.ID_ANY, u"Fit space: ",
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.fs_comb = wx.ComboBox(self, id=wx.ID_ANY, value="r-space",
                                   pos=wx.DefaultPosition,
                                   size=wx.DefaultSize,
                                   choices=['r-space', 'k-space'],
                                   validator=wx.DefaultValidator,
                                   style=wx.CB_READONLY)

        subSL2.AddMany([(absT_static, 1, wx.EXPAND, 5),
                        (self.absT_comb, 1, wx.EXPAND, 5),
                        (fs_static, 1, wx.EXPAND, 5),
                        (self.fs_comb, 1, wx.EXPAND, 5)])
        subSL2.AddGrowableCol(0, 1)
        subSL2.AddGrowableCol(1, 1)
        subSL2.AddGrowableCol(2, 1)
        subSL2.AddGrowableCol(3, 1)

        subSL3 = wx.FlexGridSizer(2, 4, 0, 0)
        subSL3.SetFlexibleDirection(wx.BOTH)
        subSL3.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        rs_static = wx.StaticText(
            self, wx.ID_ANY, u"R spacing: ",
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.rs_text = wx.TextCtrl(self, wx.ID_ANY,
                                   wx.EmptyString,
                                   wx.DefaultPosition, wx.DefaultSize)
        kp_static = wx.StaticText(
            self, wx.ID_ANY, u"k power: ",
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.kp_comb = wx.ComboBox(self, id=wx.ID_ANY, value="2",
                                   pos=wx.DefaultPosition,
                                   size=wx.DefaultSize,
                                   choices=['1', '2', '3'],
                                   validator=wx.DefaultValidator,
                                   style=wx.CB_READONLY)
        eo_static = wx.StaticText(
            self, wx.ID_ANY, u"Energy offset: ",
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.eo_text = wx.TextCtrl(self, wx.ID_ANY,
                                   wx.EmptyString,
                                   wx.DefaultPosition, wx.DefaultSize)
        wf_static = wx.StaticText(
            self, wx.ID_ANY, u"Weight: ",
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.wf_text = wx.TextCtrl(self, wx.ID_ANY,
                                   wx.EmptyString,
                                   wx.DefaultPosition, wx.DefaultSize)

        subSL3.AddMany([(rs_static, 1, wx.EXPAND, 5),
                        (self.rs_text, 1, wx.EXPAND, 5),
                        (kp_static, 1, wx.EXPAND, 5),
                        (self.kp_comb, 1, wx.EXPAND, 5),
                        (eo_static, 1, wx.EXPAND, 5),
                        (self.eo_text, 1, wx.EXPAND, 5),
                        (wf_static, 1, wx.EXPAND, 5),
                        (self.wf_text, 1, wx.EXPAND, 5)])
        subSL3.AddGrowableCol(0, 1)
        subSL3.AddGrowableCol(1, 1)
        subSL3.AddGrowableCol(2, 1)
        subSL3.AddGrowableCol(3, 1)

        prepButton = wx.Button(
            self, wx.ID_ANY, u"Prepare->", wx.DefaultPosition,
            wx.DefaultSize, 0)

        mainSL.AddMany([(subSL1, 1, wx.EXPAND, 5),
                        (addTPButton, 1, wx.EXPAND, 5),
                        (subSL2, 1, wx.EXPAND, 5),
                        (subSL3, 1, wx.EXPAND, 5),
                        (prepButton, 1, wx.EXPAND, 5)])

        ec_static = wx.StaticText(
            self, wx.ID_ANY, u"Editable composer:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.ec_text = wx.TextCtrl(self, wx.ID_ANY,
                                   wx.EmptyString,
                                   wx.DefaultPosition, wx.DefaultSize)
        compButton = wx.Button(
            self, wx.ID_ANY, u"Compose", wx.DefaultPosition,
            wx.DefaultSize, 0)

        subSR = wx.FlexGridSizer(3, 1, 0, 0)
        subSR.SetFlexibleDirection(wx.BOTH)
        subSR.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subSR.AddMany([(ec_static, 1, wx.EXPAND, 5),
                       (self.ec_text, 1, wx.EXPAND, 5),
                       (compButton, 1, wx.EXPAND, 5)])
        subSR.AddGrowableRow(1, 1)
        subSR.AddGrowableCol(0, 1)

        mainS.AddMany([(mainSL, 1, wx.EXPAND, 5),
                       (subSR, 1, wx.EXPAND, 5)])
        mainS.AddGrowableRow(0, 1)
        mainS.AddGrowableCol(1, 1)

        self.SetSizer(mainS)
        self.Layout()


class const_v6_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        self.const_multi_notebook = wx.Notebook(self, wx.ID_ANY,
                                                wx.DefaultPosition,
                                                wx.DefaultSize, wx.NB_TOP)

        self.const_dw_panel = const_dw_panel(self.const_multi_notebook)
        self.const_multi_notebook.AddPage(self.const_dw_panel,
                                          u"Distance window",
                                          True)

        self.const_pot_panel = const_pot_panel(self.const_multi_notebook)
        self.const_multi_notebook.AddPage(self.const_pot_panel,
                                          u"Potential constraint",
                                          False)

        self.const_bvs_panel = const_bvs_panel(self.const_multi_notebook)
        self.const_multi_notebook.AddPage(self.const_bvs_panel,
                                          u"Bond valence sum",
                                          False)

        mainS = wx.FlexGridSizer(1, 1, 0, 0)
        mainS.SetFlexibleDirection(wx.BOTH)
        mainS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        mainS.AddMany([(self.const_multi_notebook, 1, wx.EXPAND, 5)])
        mainS.AddGrowableRow(0, 1)
        mainS.AddGrowableCol(0, 1)

        self.SetSizer(mainS)
        self.Layout()


class const_dw_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        mainS = wx.FlexGridSizer(3, 1, 0, 0)
        mainS.SetFlexibleDirection(wx.BOTH)
        mainS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        dwcButton = wx.Button(
            self, wx.ID_ANY, u"Configure distance window constraint",
            wx.DefaultPosition,
            wx.DefaultSize, 0)
        self.dwc_text = wx.TextCtrl(self, wx.ID_ANY,
                                    wx.EmptyString,
                                    wx.DefaultPosition, wx.DefaultSize)
        dwccButton = wx.Button(
            self, wx.ID_ANY, u"Compose", wx.DefaultPosition,
            wx.DefaultSize, 0)

        mainS.AddMany([(dwcButton, 1, wx.EXPAND, 5),
                       (self.dwc_text, 1, wx.EXPAND, 5),
                       (dwccButton, 1, wx.EXPAND, 5)])
        mainS.AddGrowableRow(1, 1)
        mainS.AddGrowableCol(0, 1)

        self.SetSizer(mainS)
        self.Layout()


class const_pot_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        mainS = wx.FlexGridSizer(1, 2, 0, 0)
        mainS.SetFlexibleDirection(wx.BOTH)
        mainS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subSL = wx.FlexGridSizer(11, 1, 0, 0)
        subSL.SetFlexibleDirection(wx.BOTH)
        subSL.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subSL1 = wx.StaticLine(self, wx.ID_ANY, size=(-1, -1),
                               style=wx.LI_HORIZONTAL)
        bond_s_static = wx.StaticText(
            self, wx.ID_ANY, u"Bond stretch", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        subSL2 = wx.StaticLine(self, wx.ID_ANY, size=(-1, -1),
                               style=wx.LI_HORIZONTAL)

        subSLa1 = wx.FlexGridSizer(1, 2, 0, 0)
        subSLa1.SetFlexibleDirection(wx.BOTH)
        subSLa1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subSLa11 = wx.FlexGridSizer(2, 4, 0, 0)
        subSLa11.SetFlexibleDirection(wx.BOTH)
        subSLa11.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        atom1_bs_static = wx.StaticText(
            self, wx.ID_ANY, u"Atom-1:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        at1_choices = []
        self.atom1_type = wx.ComboBox(self, id=wx.ID_ANY, value="",
                                      pos=wx.DefaultPosition,
                                      size=(50, -1),
                                      choices=at1_choices,
                                      validator=wx.DefaultValidator,
                                      style=wx.CB_READONLY)
        atom2_bs_static = wx.StaticText(
            self, wx.ID_ANY, u"Atom-2:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        at2_choices = []
        self.atom2_type = wx.ComboBox(self, id=wx.ID_ANY, value="",
                                      pos=wx.DefaultPosition,
                                      size=(50, -1),
                                      choices=at2_choices,
                                      validator=wx.DefaultValidator,
                                      style=wx.CB_READONLY)
        bs_ep_static = wx.StaticText(
            self, wx.ID_ANY, u"Energy parameter (eV):", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.bs_ep_text = wx.TextCtrl(self, wx.ID_ANY,
                                      wx.EmptyString,
                                      pos=wx.DefaultPosition,
                                      size=(50, -1))
        bs_el_static = wx.StaticText(
            self, wx.ID_ANY, u"Equilibrium length (ang):", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.bs_el_text = wx.TextCtrl(self, wx.ID_ANY,
                                      wx.EmptyString,
                                      pos=wx.DefaultPosition,
                                      size=(50, -1))
        subSLa11.AddMany([(atom1_bs_static, 1, wx.EXPAND, 5),
                          (self.atom1_type, 1, wx.EXPAND, 5),
                          (atom2_bs_static, 1, wx.EXPAND, 5),
                          (self.atom2_type, 1, wx.EXPAND, 5),
                          (bs_ep_static, 1, wx.EXPAND, 5),
                          (self.bs_ep_text, 1, wx.EXPAND, 5),
                          (bs_el_static, 1, wx.EXPAND, 5),
                          (self.bs_el_text, 1, wx.EXPAND, 5)])
        subSLa11.AddGrowableRow(0, 1)
        subSLa11.AddGrowableRow(1, 1)
        # subSLa11.AddGrowableCol(0, 1)
        # subSLa11.AddGrowableCol(1, 1)

        updateButton = wx.Button(
            self, wx.ID_ANY, u"Update", wx.DefaultPosition,
            wx.DefaultSize, 0)

        subSLa1.AddMany([(subSLa11, 1, wx.EXPAND, 5),
                         (updateButton, 1, wx.EXPAND, 5)])
        # subSLa1.AddGrowableRow(0, 1)
        # subSLa1.AddGrowableCol(0, 1)

        subSL3 = wx.StaticLine(self, wx.ID_ANY, size=(-1, -1),
                               style=wx.LI_HORIZONTAL)
        angle_static = wx.StaticText(
            self, wx.ID_ANY, u"Bond angle", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        subSL4 = wx.StaticLine(self, wx.ID_ANY, size=(-1, -1),
                               style=wx.LI_HORIZONTAL)

        subSLa2 = wx.FlexGridSizer(1, 2, 0, 0)
        subSLa2.SetFlexibleDirection(wx.BOTH)
        subSLa2.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subSLa21 = wx.FlexGridSizer(2, 1, 0, 0)
        subSLa21.SetFlexibleDirection(wx.BOTH)
        subSLa21.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subSLa211 = wx.FlexGridSizer(1, 6, 0, 0)
        subSLa211.SetFlexibleDirection(wx.BOTH)
        subSLa211.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        a_atom1_bs_static = wx.StaticText(
            self, wx.ID_ANY, u"Atom-1:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        a_at1_choices = []
        self.a_atom1_type = wx.ComboBox(self, id=wx.ID_ANY, value="",
                                        pos=wx.DefaultPosition,
                                        size=(50, -1),
                                        choices=a_at1_choices,
                                        validator=wx.DefaultValidator,
                                        style=wx.CB_READONLY)
        a_atom2_bs_static = wx.StaticText(
            self, wx.ID_ANY, u"Atom-2:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        a_at2_choices = []
        self.a_atom2_type = wx.ComboBox(self, id=wx.ID_ANY, value="",
                                        pos=wx.DefaultPosition,
                                        size=(50, -1),
                                        choices=a_at2_choices,
                                        validator=wx.DefaultValidator,
                                        style=wx.CB_READONLY)
        a_atom3_bs_static = wx.StaticText(
            self, wx.ID_ANY, u"Atom-3:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        a_at3_choices = []
        self.a_atom3_type = wx.ComboBox(self, id=wx.ID_ANY, value="",
                                        pos=wx.DefaultPosition,
                                        size=(50, -1),
                                        choices=a_at3_choices,
                                        validator=wx.DefaultValidator,
                                        style=wx.CB_READONLY)
        subSLa211.AddMany([(a_atom1_bs_static, 1, wx.EXPAND, 5),
                           (self.a_atom1_type, 1, wx.EXPAND, 5),
                           (a_atom2_bs_static, 1, wx.EXPAND, 5),
                           (self.a_atom2_type, 1, wx.EXPAND, 5),
                           (a_atom3_bs_static, 1, wx.EXPAND, 5),
                           (self.a_atom3_type, 1, wx.EXPAND, 5)])
        subSLa211.AddGrowableCol(0, 1)
        subSLa211.AddGrowableCol(2, 1)
        subSLa211.AddGrowableCol(4, 1)

        subSLa212 = wx.FlexGridSizer(2, 4, 0, 0)
        subSLa212.SetFlexibleDirection(wx.BOTH)
        subSLa212.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        a_bs_ep_static = wx.StaticText(
            self, wx.ID_ANY, u"Energy parameter (eV):", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.a_bs_ep_text = wx.TextCtrl(self, wx.ID_ANY,
                                        wx.EmptyString,
                                        pos=wx.DefaultPosition,
                                        size=(50, -1))
        a_bs_ea_static = wx.StaticText(
            self, wx.ID_ANY, u"Equilibrium angle (deg):", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.a_bs_ea_text = wx.TextCtrl(self, wx.ID_ANY,
                                        wx.EmptyString,
                                        pos=wx.DefaultPosition,
                                        size=(50, -1))
        a_bs_l1l_static = wx.StaticText(
            self, wx.ID_ANY, u"Leg-1 length (ang):", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.a_bs_l1l_text = wx.TextCtrl(self, wx.ID_ANY,
                                         wx.EmptyString,
                                         pos=wx.DefaultPosition,
                                         size=(50, -1))
        a_bs_l2l_static = wx.StaticText(
            self, wx.ID_ANY, u"Leg-2 length (ang):", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.a_bs_l2l_text = wx.TextCtrl(self, wx.ID_ANY,
                                         wx.EmptyString,
                                         pos=wx.DefaultPosition,
                                         size=(50, -1))
        subSLa212.AddMany([(a_bs_ep_static, 1, wx.EXPAND, 5),
                           (self.a_bs_ep_text, 1, wx.EXPAND, 5),
                           (a_bs_ea_static, 1, wx.EXPAND, 5),
                           (self.a_bs_ea_text, 1, wx.EXPAND, 5),
                           (a_bs_l1l_static, 1, wx.EXPAND, 5),
                           (self.a_bs_l1l_text, 1, wx.EXPAND, 5),
                           (a_bs_l2l_static, 1, wx.EXPAND, 5),
                           (self.a_bs_l2l_text, 1, wx.EXPAND, 5)])

        subSLa21.AddMany([(subSLa211, 1, wx.EXPAND, 5),
                          (subSLa212, 1, wx.EXPAND, 5)])

        a_updateButton = wx.Button(
            self, wx.ID_ANY, u"Update", wx.DefaultPosition,
            wx.DefaultSize, 0)

        subSLa2.AddMany([(subSLa21, 1, wx.EXPAND, 5),
                         (a_updateButton, 1, wx.EXPAND, 5)])
        subSLa2.AddGrowableCol(1, 1)

        static_line_1 = wx.StaticLine(self, wx.ID_ANY, size=(-1, -1),
                                      style=wx.LI_HORIZONTAL)

        subSL5 = wx.FlexGridSizer(2, 2, 0, 0)
        subSL5.SetFlexibleDirection(wx.BOTH)
        subSL5.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subSL51 = wx.FlexGridSizer(1, 3, 0, 0)
        subSL51.SetFlexibleDirection(wx.BOTH)
        subSL51.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        bs_bs_static = wx.StaticText(
            self, wx.ID_ANY, u"Bond search +/-:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.bs_bs_text = wx.TextCtrl(self, wx.ID_ANY,
                                      wx.EmptyString,
                                      pos=wx.DefaultPosition,
                                      size=(50, -1))
        self.bs_bs_combo = wx.ComboBox(self, id=wx.ID_ANY, value="",
                                       pos=wx.DefaultPosition,
                                       size=(50, -1),
                                       choices=["%", "ang"],
                                       validator=wx.DefaultValidator,
                                       style=wx.CB_READONLY)

        subSL51.AddMany([(bs_bs_static, 1, wx.EXPAND, 5),
                         (self.bs_bs_text, 1, wx.EXPAND, 5),
                         (self.bs_bs_combo, 1, wx.EXPAND, 5)])
        subSL51.AddGrowableCol(0, 1)

        subSL52 = wx.FlexGridSizer(1, 3, 0, 0)
        subSL52.SetFlexibleDirection(wx.BOTH)
        subSL52.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        bs_as_static = wx.StaticText(
            self, wx.ID_ANY, u"Angle search +/-:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.bs_as_text = wx.TextCtrl(self, wx.ID_ANY,
                                      wx.EmptyString,
                                      pos=wx.DefaultPosition,
                                      size=(50, -1))
        self.bs_as_combo = wx.ComboBox(self, id=wx.ID_ANY, value="",
                                       pos=wx.DefaultPosition,
                                       size=(50, -1),
                                       choices=["%", "deg"],
                                       validator=wx.DefaultValidator,
                                       style=wx.CB_READONLY)

        subSL52.AddMany([(bs_as_static, 1, wx.EXPAND, 5),
                         (self.bs_as_text, 1, wx.EXPAND, 5),
                         (self.bs_as_combo, 1, wx.EXPAND, 5)])
        subSL52.AddGrowableCol(0, 1)

        subSL53 = wx.FlexGridSizer(1, 2, 0, 0)
        subSL53.SetFlexibleDirection(wx.BOTH)
        subSL53.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        bs_t_static = wx.StaticText(
            self, wx.ID_ANY, u"Temperature (K):", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.bs_t_text = wx.TextCtrl(self, wx.ID_ANY,
                                     wx.EmptyString,
                                     pos=wx.DefaultPosition,
                                     size=(100, -1))

        subSL53.AddMany([(bs_t_static, 1, wx.EXPAND, 5),
                         (self.bs_t_text, 1, wx.EXPAND, 5)])
        subSL53.AddGrowableCol(0, 1)

        bs_holder_static = wx.StaticText(
            self, wx.ID_ANY, u"", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)

        subSL5.AddMany([(subSL51, 1, wx.EXPAND, 5),
                        (subSL52, 1, wx.EXPAND, 5),
                        (subSL53, 1, wx.EXPAND, 5),
                        (bs_holder_static, 1, wx.EXPAND, 5)])
        subSL5.AddGrowableCol(0, 1)
        subSL5.AddGrowableCol(1, 1)

        prepButton = wx.Button(
            self, wx.ID_ANY, u"Prepare->", wx.DefaultPosition,
            wx.DefaultSize, 0)

        subSL.AddMany([(subSL1, 1, wx.EXPAND, 5),
                       (bond_s_static, 1, wx.EXPAND, 5),
                       (subSL2, 1, wx.EXPAND, 5),
                       (subSLa1, 1, wx.EXPAND, 5),
                       (subSL3, 1, wx.EXPAND, 5),
                       (angle_static, 1, wx.EXPAND, 5),
                       (subSL4, 1, wx.EXPAND, 5),
                       (subSLa2, 1, wx.EXPAND, 5),
                       (static_line_1, 1, wx.EXPAND, 5),
                       (subSL5, 1, wx.EXPAND, 5),
                       (prepButton, 1, wx.EXPAND, 5)])
        # subSL.AddGrowableRow(0, 1)
        # subSL.AddGrowableCol(0, 1)

        subSR = wx.FlexGridSizer(3, 1, 0, 0)
        subSR.SetFlexibleDirection(wx.BOTH)
        subSR.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        ec_static = wx.StaticText(
            self, wx.ID_ANY, u"Editable composer:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.ec_text = wx.TextCtrl(self, wx.ID_ANY,
                                   wx.EmptyString,
                                   wx.DefaultPosition, wx.DefaultSize)
        compButton = wx.Button(
            self, wx.ID_ANY, u"Compose", wx.DefaultPosition,
            wx.DefaultSize, 0)

        subSR.AddMany([(ec_static, 1, wx.EXPAND, 5),
                       (self.ec_text, 1, wx.EXPAND, 5),
                       (compButton, 1, wx.EXPAND, 5)])
        subSR.AddGrowableRow(1, 1)
        subSR.AddGrowableCol(0, 1)

        mainS.AddMany([(subSL, 1, wx.EXPAND, 5),
                       (subSR, 1, wx.EXPAND, 5)])
        mainS.AddGrowableRow(0, 1)
        # mainS.AddGrowableCol(0, 1)
        mainS.AddGrowableCol(1, 1)

        self.SetSizer(mainS)
        self.Layout()


class const_bvs_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        mainS = wx.FlexGridSizer(3, 1, 0, 0)
        mainS.SetFlexibleDirection(wx.BOTH)
        mainS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        bvscButton = wx.Button(
            self, wx.ID_ANY, u"Configure bond valence sum constraint",
            wx.DefaultPosition,
            wx.DefaultSize, 0)
        self.bvsc_text = wx.TextCtrl(self, wx.ID_ANY,
                                     wx.EmptyString,
                                     wx.DefaultPosition, wx.DefaultSize)
        bvsccButton = wx.Button(
            self, wx.ID_ANY, u"Compose", wx.DefaultPosition,
            wx.DefaultSize, 0)

        mainS.AddMany([(bvscButton, 1, wx.EXPAND, 5),
                       (self.bvsc_text, 1, wx.EXPAND, 5),
                       (bvsccButton, 1, wx.EXPAND, 5)])
        mainS.AddGrowableRow(1, 1)
        mainS.AddGrowableCol(0, 1)

        self.SetSizer(mainS)
        self.Layout()


class adv_v6_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        mainS = wx.FlexGridSizer(1, 1, 0, 0)
        mainS.SetFlexibleDirection(wx.BOTH)
        mainS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.SetSizer(mainS)
        self.Layout()


class adv_v6_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        self.adv_multi_notebook = wx.Notebook(self, wx.ID_ANY,
                                              wx.DefaultPosition,
                                              wx.DefaultSize, wx.NB_TOP)

        self.adv_scxd_panel = adv_scxd_panel(self.adv_multi_notebook)
        self.adv_multi_notebook.AddPage(self.adv_scxd_panel,
                                        u"Single crystal X-ray diffuse",
                                        True)

        mainS = wx.FlexGridSizer(1, 1, 0, 0)
        mainS.SetFlexibleDirection(wx.BOTH)
        mainS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        mainS.AddMany([(self.adv_multi_notebook, 1, wx.EXPAND, 5)])
        mainS.AddGrowableRow(0, 1)
        mainS.AddGrowableCol(0, 1)

        self.SetSizer(mainS)
        self.Layout()


class adv_scxd_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        mainMainS = wx.FlexGridSizer(1, 2, 0, 0)
        mainMainS.SetFlexibleDirection(wx.BOTH)
        mainMainS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        mainSR = wx.FlexGridSizer(3, 1, 0, 0)
        mainSR.SetFlexibleDirection(wx.BOTH)
        mainSR.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        ec_static = wx.StaticText(
            self, wx.ID_ANY, u"Editable composer:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.ec_text = wx.TextCtrl(self, wx.ID_ANY,
                                   wx.EmptyString,
                                   wx.DefaultPosition, wx.DefaultSize)
        compButton = wx.Button(
            self, wx.ID_ANY, u"Compose", wx.DefaultPosition,
            wx.DefaultSize, 0)

        mainSR.AddMany([(ec_static, 1, wx.EXPAND, 5),
                       (self.ec_text, 1, wx.EXPAND, 5),
                       (compButton, 1, wx.EXPAND, 5)])
        mainSR.AddGrowableRow(1, 1)
        mainSR.AddGrowableCol(0, 1)

        mainS = wx.FlexGridSizer(6, 1, 0, 0)
        mainS.SetFlexibleDirection(wx.BOTH)
        mainS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subS1 = wx.FlexGridSizer(1, 3, 0, 0)
        subS1.SetFlexibleDirection(wx.BOTH)
        subS1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        fn_static = wx.StaticText(
            self, wx.ID_ANY, u"File name: ",
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.fn_text = wx.TextCtrl(self, wx.ID_ANY,
                                   wx.EmptyString,
                                   wx.DefaultPosition, wx.DefaultSize)
        fileBButton = wx.Button(
            self, wx.ID_ANY, u"Browse file", wx.DefaultPosition,
            wx.DefaultSize, 0)

        subS1.AddMany([(fn_static, 1, wx.EXPAND, 5),
                       (self.fn_text, 1, wx.EXPAND, 5),
                       (fileBButton, 1, wx.EXPAND, 5)])
        subS1.AddGrowableRow(0, 1)
        subS1.AddGrowableCol(1, 1)

        afButton = wx.Button(
            self, wx.ID_ANY, u"Add file to project",
            wx.DefaultPosition,
            wx.DefaultSize, 0)

        subS2 = wx.FlexGridSizer(2, 4, 0, 0)
        subS2.SetFlexibleDirection(wx.BOTH)
        subS2.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        fs_static = wx.StaticText(
            self, wx.ID_ANY, u"Fit scale:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.fs_comb = wx.ComboBox(self, id=wx.ID_ANY, value="No",
                                   pos=wx.DefaultPosition,
                                   size=wx.DefaultSize,
                                   choices=['Yes', 'No'],
                                   validator=wx.DefaultValidator,
                                   style=wx.CB_READONLY)
        fo_static = wx.StaticText(
            self, wx.ID_ANY, u"Fit offset:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.fo_comb = wx.ComboBox(self, id=wx.ID_ANY, value="No",
                                   pos=wx.DefaultPosition,
                                   size=wx.DefaultSize,
                                   choices=['Yes', 'No'],
                                   validator=wx.DefaultValidator,
                                   style=wx.CB_READONLY)
        const_s_static = wx.StaticText(
            self, wx.ID_ANY, u"Constant scale: ",
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.cs_text = wx.TextCtrl(self, wx.ID_ANY,
                                   wx.EmptyString,
                                   wx.DefaultPosition, wx.DefaultSize)
        const_o_static = wx.StaticText(
            self, wx.ID_ANY, u"Constant offset: ",
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.co_text = wx.TextCtrl(self, wx.ID_ANY,
                                   wx.EmptyString,
                                   wx.DefaultPosition, wx.DefaultSize)
        subS2.AddMany([(fs_static, 1, wx.EXPAND, 5),
                       (self.fs_comb, 1, wx.EXPAND, 5),
                       (fo_static, 1, wx.EXPAND, 5),
                       (self.fo_comb, 1, wx.EXPAND, 5),
                       (const_s_static, 1, wx.EXPAND, 5),
                       (self.cs_text, 1, wx.EXPAND, 5),
                       (const_o_static, 1, wx.EXPAND, 5),
                       (self.co_text, 1, wx.EXPAND, 5)])
        subS2.AddGrowableRow(0, 1)

        subS3 = wx.FlexGridSizer(1, 7, 0, 0)
        subS3.SetFlexibleDirection(wx.BOTH)
        subS3.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        weight_static = wx.StaticText(
            self, wx.ID_ANY, u"Weight: ",
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.weight_text = wx.TextCtrl(self, wx.ID_ANY,
                                       wx.EmptyString,
                                       wx.DefaultPosition, size=(80, -1))
        kernel_static = wx.StaticText(
            self, wx.ID_ANY, u"Kernel3D: ",
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.kernel_text1 = wx.TextCtrl(self, wx.ID_ANY,
                                        wx.EmptyString,
                                        wx.DefaultPosition, size=(40, -1))
        self.kernel_text2 = wx.TextCtrl(self, wx.ID_ANY,
                                        wx.EmptyString,
                                        wx.DefaultPosition, size=(40, -1))
        self.kernel_text3 = wx.TextCtrl(self, wx.ID_ANY,
                                        wx.EmptyString,
                                        wx.DefaultPosition, size=(40, -1))
        qButton1 = wx.Button(
            self, wx.ID_ANY, u"<-?", wx.DefaultPosition,
            wx.DefaultSize, 0)

        subS3.AddMany([(weight_static, 1, wx.EXPAND, 5),
                       (self.weight_text, 1, wx.EXPAND, 5),
                       (kernel_static, 1, wx.EXPAND, 5),
                       (self.kernel_text1, 1, wx.EXPAND, 5),
                       (self.kernel_text2, 1, wx.EXPAND, 5),
                       (self.kernel_text3, 1, wx.EXPAND, 5),
                       (qButton1, 1, wx.EXPAND, 5)])
        subS3.AddGrowableRow(0, 1)
        subS3.AddGrowableCol(6, 1)

        subS4 = wx.FlexGridSizer(1, 2, 0, 0)
        subS4.SetFlexibleDirection(wx.BOTH)
        subS4.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)
        ist_static = wx.StaticText(
            self, wx.ID_ANY, u"Intensity scale type: ",
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.ist_comb = wx.ComboBox(self, id=wx.ID_ANY, value="Linear",
                                    pos=wx.DefaultPosition,
                                    size=wx.DefaultSize,
                                    choices=['Linear', 'Logarithmic'],
                                    validator=wx.DefaultValidator,
                                    style=wx.CB_READONLY)
        subS4.AddMany([(ist_static, 1, wx.EXPAND, 5),
                       (self.ist_comb, 1, wx.EXPAND, 5)])
        subS4.AddGrowableRow(0, 1)
        subS4.AddGrowableCol(1, 1)

        prepButton = wx.Button(
            self, wx.ID_ANY, u"Prepare->", wx.DefaultPosition,
            wx.DefaultSize, 0)

        mainS.AddMany([(subS1, 1, wx.EXPAND, 5),
                       (afButton, 1, wx.EXPAND, 5),
                       (subS2, 1, wx.EXPAND, 5),
                       (subS3, 1, wx.EXPAND, 5),
                       (subS4, 1, wx.EXPAND, 5),
                       (prepButton, 1, wx.EXPAND, 5)])

        mainMainS.AddMany([(mainS, 1, wx.EXPAND, 5),
                           (mainSR, 1, wx.EXPAND, 5)])
        mainMainS.AddGrowableRow(0, 1)
        mainMainS.AddGrowableCol(1, 1)

        self.SetSizer(mainMainS)
        self.Layout()


class others_v6_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        mainS = wx.FlexGridSizer(3, 1, 0, 0)
        mainS.SetFlexibleDirection(wx.BOTH)
        mainS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.others_text = wx.TextCtrl(self, wx.ID_ANY,
                                       wx.EmptyString,
                                       wx.DefaultPosition, wx.DefaultSize)
        otherscButton = wx.Button(
            self, wx.ID_ANY, u"Compose",
            wx.DefaultPosition,
            wx.DefaultSize, 0)
        othersAFButton = wx.Button(
            self, wx.ID_ANY, u"Add necessary files to project",
            wx.DefaultPosition,
            wx.DefaultSize, 0)

        mainS.AddMany([(self.others_text, 1, wx.EXPAND, 5),
                       (otherscButton, 1, wx.EXPAND, 5),
                       (othersAFButton, 1, wx.EXPAND, 5)])
        mainS.AddGrowableRow(0, 1)
        mainS.AddGrowableCol(0, 1)

        self.SetSizer(mainS)
        self.Layout()


class nq_v6_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        mainS = wx.FlexGridSizer(1, 2, 0, 0)
        mainS.SetFlexibleDirection(wx.BOTH)
        mainS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subSL = wx.FlexGridSizer(3, 1, 0, 0)
        subSL.SetFlexibleDirection(wx.BOTH)
        subSL.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subSL1a = wx.FlexGridSizer(1, 3, 0, 0)
        subSL1a.SetFlexibleDirection(wx.BOTH)
        subSL1a.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        fn_static = wx.StaticText(
            self, wx.ID_ANY, u"File name: ",
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.fn_text = wx.TextCtrl(self, wx.ID_ANY,
                                   wx.EmptyString,
                                   wx.DefaultPosition, wx.DefaultSize)
        fileBButton = wx.Button(
            self, wx.ID_ANY, u"Browse file", wx.DefaultPosition,
            wx.DefaultSize, 0)

        subSL1a.AddMany([(fn_static, 1, wx.EXPAND, 5),
                         (self.fn_text, 1, wx.EXPAND, 5),
                         (fileBButton, 1, wx.EXPAND, 5)])
        subSL1a.AddGrowableCol(1, 1)

        subSL1 = wx.FlexGridSizer(2, 1, 0, 0)
        subSL1.SetFlexibleDirection(wx.BOTH)
        subSL1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        afButton = wx.Button(
            self, wx.ID_ANY, u"Add data file to project", wx.DefaultPosition,
            wx.DefaultSize, 0)

        subSL1.AddMany([(subSL1a, 1, wx.EXPAND, 5),
                        (afButton, 1, wx.EXPAND, 5)])
        subSL1.AddGrowableCol(0, 1)

        subSL2 = wx.FlexGridSizer(5, 4, 0, 0)
        subSL2.SetFlexibleDirection(wx.BOTH)
        subSL2.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        dt_static = wx.StaticText(
            self, wx.ID_ANY, u"Data type:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.dt_comb = wx.ComboBox(self, id=wx.ID_ANY, value="S(Q)",
                                   pos=wx.DefaultPosition,
                                   size=wx.DefaultSize,
                                   choices=['S(Q)', 'F(Q)'],
                                   validator=wx.DefaultValidator,
                                   style=wx.CB_READONLY)
        typeQButton = wx.Button(
            self, wx.ID_ANY, u"<-?", wx.DefaultPosition,
            wx.DefaultSize, 0)

        subSL2a = wx.FlexGridSizer(1, 2, 0, 0)
        subSL2a.SetFlexibleDirection(wx.BOTH)
        subSL2a.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subSL2a.AddMany([(self.dt_comb, 1, wx.EXPAND, 5),
                         (typeQButton, 1, wx.EXPAND, 5)])
        subSL2a.AddGrowableCol(0, 1)
        subSL2a.AddGrowableCol(1, 1)

        ft_static = wx.StaticText(
            self, wx.ID_ANY, u"Fit type:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.ft_comb = wx.ComboBox(self, id=wx.ID_ANY, value="S(Q)",
                                   pos=wx.DefaultPosition,
                                   size=wx.DefaultSize,
                                   choices=['S(Q)', 'F(Q)'],
                                   validator=wx.DefaultValidator,
                                   style=wx.CB_READONLY)
        typeQ1Button = wx.Button(
            self, wx.ID_ANY, u"<-?", wx.DefaultPosition,
            wx.DefaultSize, 0)

        subSL2b = wx.FlexGridSizer(1, 2, 0, 0)
        subSL2b.SetFlexibleDirection(wx.BOTH)
        subSL2b.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subSL2b.AddMany([(self.ft_comb, 1, wx.EXPAND, 5),
                         (typeQ1Button, 1, wx.EXPAND, 5)])
        subSL2b.AddGrowableCol(0, 1)
        subSL2b.AddGrowableCol(1, 1)

        fo_static = wx.StaticText(
            self, wx.ID_ANY, u"Fit offset:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.fo_comb = wx.ComboBox(self, id=wx.ID_ANY, value="No",
                                   pos=wx.DefaultPosition,
                                   size=wx.DefaultSize,
                                   choices=['No', 'Yes'],
                                   validator=wx.DefaultValidator,
                                   style=wx.CB_READONLY)

        fs_static = wx.StaticText(
            self, wx.ID_ANY, u"Fit scale:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.fs_comb = wx.ComboBox(self, id=wx.ID_ANY, value="No",
                                   pos=wx.DefaultPosition,
                                   size=wx.DefaultSize,
                                   choices=['No', 'Yes'],
                                   validator=wx.DefaultValidator,
                                   style=wx.CB_READONLY)

        co_static = wx.StaticText(
            self, wx.ID_ANY, u"Constant offset:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.co_text = wx.TextCtrl(self, wx.ID_ANY,
                                   wx.EmptyString,
                                   wx.DefaultPosition, wx.DefaultSize)

        weight_static = wx.StaticText(
            self, wx.ID_ANY, u"Weight:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.weight_text = wx.TextCtrl(self, wx.ID_ANY,
                                       wx.EmptyString,
                                       wx.DefaultPosition, wx.DefaultSize)

        sp_static = wx.StaticText(
            self, wx.ID_ANY, u"Start point:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.sp_text = wx.TextCtrl(self, wx.ID_ANY,
                                   wx.EmptyString,
                                   wx.DefaultPosition, wx.DefaultSize)

        ep_static = wx.StaticText(
            self, wx.ID_ANY, u"End point:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.ep_text = wx.TextCtrl(self, wx.ID_ANY,
                                   wx.EmptyString,
                                   wx.DefaultPosition, wx.DefaultSize)

        conv_static = wx.StaticText(
            self, wx.ID_ANY, u"Convolve:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.conv_comb = wx.ComboBox(self, id=wx.ID_ANY, value="Yes",
                                     pos=wx.DefaultPosition,
                                     size=wx.DefaultSize,
                                     choices=['Yes', 'No'],
                                     validator=wx.DefaultValidator,
                                     style=wx.CB_READONLY)
        convQButton = wx.Button(
            self, wx.ID_ANY, u"<-?", wx.DefaultPosition,
            wx.DefaultSize, 0)

        subSL2c = wx.FlexGridSizer(1, 2, 0, 0)
        subSL2c.SetFlexibleDirection(wx.BOTH)
        subSL2c.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subSL2c.AddMany([(self.conv_comb, 1, wx.EXPAND, 5),
                         (convQButton, 1, wx.EXPAND, 5)])
        subSL2c.AddGrowableCol(0, 1)
        subSL2c.AddGrowableCol(1, 1)

        subSL2.AddMany([(dt_static, 1, wx.EXPAND, 5),
                        (subSL2a, 1, wx.EXPAND, 5),
                        (ft_static, 1, wx.EXPAND, 5),
                        (subSL2b, 1, wx.EXPAND, 5),
                        (fo_static, 1, wx.EXPAND, 5),
                        (self.fo_comb, 1, wx.EXPAND, 5),
                        (fs_static, 1, wx.EXPAND, 5),
                        (self.fs_comb, 1, wx.EXPAND, 5),
                        (co_static, 1, wx.EXPAND, 5),
                        (self.co_text, 1, wx.EXPAND, 5),
                        (weight_static, 1, wx.EXPAND, 5),
                        (self.weight_text, 1, wx.EXPAND, 5),
                        (sp_static, 1, wx.EXPAND, 5),
                        (self.sp_text, 1, wx.EXPAND, 5),
                        (ep_static, 1, wx.EXPAND, 5),
                        (self.ep_text, 1, wx.EXPAND, 5),
                        (conv_static, 1, wx.EXPAND, 5),
                        (subSL2c, 1, wx.EXPAND, 5)])
        subSL2.AddGrowableCol(0, 1)
        subSL2.AddGrowableCol(1, 1)
        subSL2.AddGrowableCol(2, 1)
        subSL2.AddGrowableCol(3, 1)

        prepButton = wx.Button(
            self, wx.ID_ANY, u"Prepare->", wx.DefaultPosition,
            wx.DefaultSize, 0)

        subSL.AddMany([(subSL1, 1, wx.EXPAND, 5),
                       (subSL2, 1, wx.EXPAND, 5),
                       (prepButton, 1, wx.EXPAND, 5)])
        subSL.AddGrowableCol(0, 1)

        subSR = wx.FlexGridSizer(3, 1, 0, 0)
        subSR.SetFlexibleDirection(wx.BOTH)
        subSR.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        ec_static = wx.StaticText(
            self, wx.ID_ANY, u"Editable composer:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.ec_text = wx.TextCtrl(self, wx.ID_ANY,
                                   wx.EmptyString,
                                   wx.DefaultPosition, wx.DefaultSize)
        compButton = wx.Button(
            self, wx.ID_ANY, u"Compose", wx.DefaultPosition,
            wx.DefaultSize, 0)

        subSR.AddMany([(ec_static, 1, wx.EXPAND, 5),
                       (self.ec_text, 1, wx.EXPAND, 5),
                       (compButton, 1, wx.EXPAND, 5)])
        subSR.AddGrowableRow(1, 1)
        subSR.AddGrowableCol(0, 1)

        mainS.AddMany([(subSL, 1, wx.EXPAND, 5),
                       (subSR, 1, wx.EXPAND, 5)])
        mainS.AddGrowableRow(0, 1)
        # mainS.AddGrowableCol(0, 1)
        mainS.AddGrowableCol(1, 1)

        self.SetSizer(mainS)
        self.Layout()


class nr_prep_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        mainS = wx.FlexGridSizer(1, 1, 0, 0)
        mainS.SetFlexibleDirection(wx.BOTH)
        mainS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.nr_prep_notebook = wx.Notebook(self, wx.ID_ANY,
                                            wx.DefaultPosition,
                                            wx.DefaultSize, wx.NB_BOTTOM)

        self.nr_v6_panel = nr_v6_panel(self.nr_prep_notebook)
        self.nr_prep_notebook.AddPage(self.nr_v6_panel, u"Version 6", True)

        mainS.AddMany([(self.nr_prep_notebook, 1, wx.EXPAND, 5)])
        mainS.AddGrowableRow(0, 1)
        mainS.AddGrowableCol(0, 1)

        self.SetSizer(mainS)
        self.Layout()


class nq_prep_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        mainS = wx.FlexGridSizer(2, 1, 0, 0)
        mainS.SetFlexibleDirection(wx.BOTH)
        mainS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.nq_prep_notebook = wx.Notebook(self, wx.ID_ANY,
                                            wx.DefaultPosition,
                                            wx.DefaultSize, wx.NB_BOTTOM)

        self.nq_v6_panel = nq_v6_panel(self.nq_prep_notebook)
        self.nq_prep_notebook.AddPage(self.nq_v6_panel, u"Version 6", True)

        mainS.AddMany([(self.nq_prep_notebook, 1, wx.EXPAND, 5)])
        mainS.AddGrowableRow(0, 1)
        mainS.AddGrowableCol(0, 1)

        self.SetSizer(mainS)
        self.Layout()


class xray_prep_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        mainS = wx.FlexGridSizer(1, 1, 0, 0)
        mainS.SetFlexibleDirection(wx.BOTH)
        mainS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.xray_prep_notebook = wx.Notebook(self, wx.ID_ANY,
                                              wx.DefaultPosition,
                                              wx.DefaultSize, wx.NB_BOTTOM)

        self.xray_v6_panel = xray_v6_panel(self.xray_prep_notebook)
        self.xray_prep_notebook.AddPage(self.xray_v6_panel, u"Version 6", True)

        mainS.AddMany([(self.xray_prep_notebook, 1, wx.EXPAND, 5)])
        mainS.AddGrowableRow(0, 1)
        mainS.AddGrowableCol(0, 1)

        self.SetSizer(mainS)
        self.Layout()


class bragg_prep_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        mainS = wx.FlexGridSizer(1, 1, 0, 0)
        mainS.SetFlexibleDirection(wx.BOTH)
        mainS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.bragg_prep_notebook = wx.Notebook(self, wx.ID_ANY,
                                               wx.DefaultPosition,
                                               wx.DefaultSize, wx.NB_BOTTOM)

        self.bragg_v6_panel = bragg_v6_panel(self.bragg_prep_notebook)
        self.bragg_prep_notebook.AddPage(self.bragg_v6_panel, u"Version 6", True)

        mainS.AddMany([(self.bragg_prep_notebook, 1, wx.EXPAND, 5)])
        mainS.AddGrowableRow(0, 1)
        mainS.AddGrowableCol(0, 1)

        self.SetSizer(mainS)
        self.Layout()


class exafs_prep_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        mainS = wx.FlexGridSizer(1, 1, 0, 0)
        mainS.SetFlexibleDirection(wx.BOTH)
        mainS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.exafs_prep_notebook = wx.Notebook(self, wx.ID_ANY,
                                            wx.DefaultPosition,
                                            wx.DefaultSize, wx.NB_BOTTOM)

        self.exafs_v6_panel = exafs_v6_panel(self.exafs_prep_notebook)
        self.exafs_prep_notebook.AddPage(self.exafs_v6_panel, u"Version 6", True)

        mainS.AddMany([(self.exafs_prep_notebook, 1, wx.EXPAND, 5)])
        mainS.AddGrowableRow(0, 1)
        mainS.AddGrowableCol(0, 1)

        self.SetSizer(mainS)
        self.Layout()


class const_prep_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        mainS = wx.FlexGridSizer(1, 1, 0, 0)
        mainS.SetFlexibleDirection(wx.BOTH)
        mainS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.const_prep_notebook = wx.Notebook(self, wx.ID_ANY,
                                               wx.DefaultPosition,
                                               wx.DefaultSize, wx.NB_BOTTOM)

        self.const_v6_panel = const_v6_panel(self.const_prep_notebook)
        self.const_prep_notebook.AddPage(self.const_v6_panel, u"Version 6",
                                         True)

        mainS.AddMany([(self.const_prep_notebook, 1, wx.EXPAND, 5)])
        mainS.AddGrowableRow(0, 1)
        mainS.AddGrowableCol(0, 1)

        self.SetSizer(mainS)
        self.Layout()


class adv_prep_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        mainS = wx.FlexGridSizer(1, 1, 0, 0)
        mainS.SetFlexibleDirection(wx.BOTH)
        mainS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.adv_prep_notebook = wx.Notebook(self, wx.ID_ANY,
                                             wx.DefaultPosition,
                                             wx.DefaultSize, wx.NB_BOTTOM)

        self.adv_v6_panel = adv_v6_panel(self.adv_prep_notebook)
        self.adv_prep_notebook.AddPage(self.adv_v6_panel, u"Version 6", True)

        mainS.AddMany([(self.adv_prep_notebook, 1, wx.EXPAND, 5)])
        mainS.AddGrowableRow(0, 1)
        mainS.AddGrowableCol(0, 1)

        self.SetSizer(mainS)
        self.Layout()


class others_prep_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        mainS = wx.FlexGridSizer(1, 1, 0, 0)
        mainS.SetFlexibleDirection(wx.BOTH)
        mainS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.others_prep_notebook = wx.Notebook(self, wx.ID_ANY,
                                                wx.DefaultPosition,
                                                wx.DefaultSize, wx.NB_BOTTOM)

        self.others_v6_panel = others_v6_panel(self.others_prep_notebook)
        self.others_prep_notebook.AddPage(self.others_v6_panel, u"Version 6",
                                          True)

        mainS.AddMany([(self.others_prep_notebook, 1, wx.EXPAND, 5)])
        mainS.AddGrowableRow(0, 1)
        mainS.AddGrowableCol(0, 1)

        self.SetSizer(mainS)
        self.Layout()


class fc_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        mainS = wx.FlexGridSizer(2, 1, 0, 0)
        mainS.SetFlexibleDirection(wx.BOTH)
        mainS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subS1 = wx.FlexGridSizer(1, 2, 0, 0)
        subS1.SetFlexibleDirection(wx.BOTH)
        subS1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subS1L = wx.FlexGridSizer(5, 2, 0, 0)
        subS1L.SetFlexibleDirection(wx.BOTH)
        subS1L.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        nd_static = wx.StaticText(
            self, wx.ID_ANY, u"Number density: ",
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.nd_text = wx.TextCtrl(self, wx.ID_ANY,
                                   wx.EmptyString,
                                   wx.DefaultPosition, wx.DefaultSize)
        at_static = wx.StaticText(
            self, wx.ID_ANY, u"Atom types: ", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.at_text = wx.TextCtrl(self, wx.ID_ANY,
                                   wx.EmptyString,
                                   wx.DefaultPosition, wx.DefaultSize)
        rs_static = wx.StaticText(
            self, wx.ID_ANY, u"R spacing: ", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.rs_text = wx.TextCtrl(self, wx.ID_ANY,
                                   wx.EmptyString,
                                   wx.DefaultPosition, wx.DefaultSize)
        tl_static = wx.StaticText(
            self, wx.ID_ANY, u"Time limitation: ", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.tl_text = wx.TextCtrl(self, wx.ID_ANY,
                                   wx.EmptyString,
                                   wx.DefaultPosition, wx.DefaultSize)
        sp_static = wx.StaticText(
            self, wx.ID_ANY, u"Save period: ", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.sp_text = wx.TextCtrl(self, wx.ID_ANY,
                                   wx.EmptyString,
                                   wx.DefaultPosition, wx.DefaultSize)

        subS1L.AddMany([(nd_static, 1, wx.EXPAND, 5),
                        (self.nd_text, 1, wx.EXPAND, 5),
                        (at_static, 1, wx.EXPAND | wx.ALIGN_RIGHT, 5),
                        (self.at_text, 1, wx.EXPAND | wx.ALIGN_RIGHT, 5),
                        (rs_static, 1, wx.EXPAND | wx.ALIGN_RIGHT, 5),
                        (self.rs_text, 1, wx.EXPAND | wx.ALIGN_RIGHT, 5),
                        (tl_static, 1, wx.EXPAND | wx.ALIGN_RIGHT, 5),
                        (self.tl_text, 1, wx.EXPAND | wx.ALIGN_RIGHT, 5),
                        (sp_static, 1, wx.EXPAND | wx.ALIGN_RIGHT, 5),
                        (self.sp_text, 1, wx.EXPAND | wx.ALIGN_RIGHT, 5)])
        subS1L.AddGrowableCol(1, 1)

        subS1R = wx.FlexGridSizer(5, 1, 0, 0)
        subS1R.SetFlexibleDirection(wx.BOTH)
        subS1R.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subS1R1 = wx.FlexGridSizer(1, 2, 0, 0)
        subS1R1.SetFlexibleDirection(wx.BOTH)
        subS1R1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        minDButton = wx.Button(
            self, wx.ID_ANY, u"Minimum distances", wx.DefaultPosition,
            wx.DefaultSize, 0)
        maxMButton = wx.Button(
            self, wx.ID_ANY, u"Maximum move", wx.DefaultPosition,
            wx.DefaultSize, 0)
        subS1R1.AddMany([(minDButton, 1, wx.EXPAND, 5),
                        (maxMButton, 1, wx.EXPAND, 5)])
        subS1R1.AddGrowableCol(0, 1)
        subS1R1.AddGrowableCol(1, 1)

        subS1R2 = wx.FlexGridSizer(2, 4, 0, 0)
        subS1R2.SetFlexibleDirection(wx.BOTH)
        subS1R2.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        ict_static = wx.StaticText(
            self, wx.ID_ANY, u"Config type in:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.ict_comb = wx.ComboBox(self, id=wx.ID_ANY, value="rmc6f",
                                    pos=wx.DefaultPosition,
                                    size=wx.DefaultSize,
                                    choices=['rmc6f', 'cfg'],
                                    validator=wx.DefaultValidator,
                                    style=wx.CB_READONLY)
        oct_static = wx.StaticText(
            self, wx.ID_ANY, u"Config type out:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.oct_comb = wx.ComboBox(self, id=wx.ID_ANY, value="rmc6f",
                                    pos=wx.DefaultPosition,
                                    size=wx.DefaultSize,
                                    choices=['rmc6f', 'cfg'],
                                    validator=wx.DefaultValidator,
                                    style=wx.CB_READONLY)

        igh_static = wx.StaticText(
            self, wx.ID_ANY, u"Ignore history:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.igh_comb = wx.ComboBox(self, id=wx.ID_ANY, value="yes",
                                    pos=wx.DefaultPosition,
                                    size=wx.DefaultSize,
                                    choices=['yes', 'no'],
                                    validator=wx.DefaultValidator,
                                    style=wx.CB_READONLY)
        wo_static = wx.StaticText(
            self, wx.ID_ANY, u"Adjust weight:", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.wo_comb = wx.ComboBox(self, id=wx.ID_ANY, value="no",
                                   pos=wx.DefaultPosition,
                                   size=wx.DefaultSize,
                                   choices=['yes', 'no'],
                                   validator=wx.DefaultValidator,
                                   style=wx.CB_READONLY)

        subS1R2.AddMany([(ict_static, 1, wx.EXPAND, 5),
                         (self.ict_comb, 1, wx.EXPAND, 5),
                         (oct_static, 1, wx.EXPAND, 5),
                         (self.oct_comb, 1, wx.EXPAND, 5),
                         (igh_static, 1, wx.EXPAND, 5),
                         (self.igh_comb, 1, wx.EXPAND, 5),
                         (wo_static, 1, wx.EXPAND, 5),
                         (self.wo_comb, 1, wx.EXPAND, 5)])
        subS1R2.AddGrowableCol(0, 1)
        subS1R2.AddGrowableCol(2, 1)

        subS1R4 = wx.FlexGridSizer(2, 3, 0, 0)
        subS1R4.SetFlexibleDirection(wx.BOTH)
        subS1R4.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        wop_static = wx.StaticText(
            self, wx.ID_ANY, u"Weight adjust control: ", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.wop_text = wx.TextCtrl(self, wx.ID_ANY,
                                    wx.EmptyString,
                                    wx.DefaultPosition, size=(80, -1))
        wopQButton = wx.Button(
            self, wx.ID_ANY, u"<-?", wx.DefaultPosition,
            wx.DefaultSize, 0)

        mo_static = wx.StaticText(
            self, wx.ID_ANY, u"Move out: ", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.mo_comb = wx.ComboBox(self, id=wx.ID_ANY, value="no",
                                   pos=wx.DefaultPosition,
                                   size=wx.DefaultSize,
                                   choices=['yes', 'no'],
                                   validator=wx.DefaultValidator,
                                   style=wx.CB_READONLY)
        moQButton = wx.Button(
            self, wx.ID_ANY, u"<-?", wx.DefaultPosition,
            wx.DefaultSize, 0)

        subS1R4.AddMany([(wop_static, 1, wx.EXPAND, 5),
                         (self.wop_text, 1, wx.EXPAND, 5),
                         (wopQButton, 1, wx.EXPAND, 5),
                         (mo_static, 1, wx.EXPAND, 5),
                         (self.mo_comb, 1, wx.EXPAND, 5),
                         (moQButton, 1, wx.EXPAND, 5)])
        subS1R4.AddGrowableCol(0, 1)
        subS1R4.AddGrowableCol(1, 1)
        subS1R4.AddGrowableCol(2, 1)

        subS1R.AddMany([(subS1R1, 1, wx.EXPAND, 5),
                        (subS1R2, 1, wx.EXPAND, 5),
                        (subS1R4, 1, wx.EXPAND, 5)])
        subS1R.AddGrowableCol(0, 1)

        subS1.AddMany([(subS1L, 1, wx.EXPAND, 5),
                       (subS1R, 1, wx.EXPAND, 5)])
        subS1.AddGrowableRow(0, 1)
        subS1.AddGrowableCol(0, 1)
        subS1.AddGrowableCol(1, 1)

        subS2 = wx.FlexGridSizer(1, 3, 0, 0)
        subS2.SetFlexibleDirection(wx.BOTH)
        subS2.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        aswapButton = wx.Button(
            self, wx.ID_ANY, u"Atoms swap", wx.DefaultPosition,
            wx.DefaultSize, 0)

        advMButton = wx.Button(
            self, wx.ID_ANY, u"Advanced mode", wx.DefaultPosition,
            wx.DefaultSize, 0)

        updateButton = wx.Button(
            self, wx.ID_ANY, u"Update", wx.DefaultPosition,
            wx.DefaultSize, 0)

        subS2.AddMany([(aswapButton, 1, wx.EXPAND, 5),
                       (advMButton, 1, wx.EXPAND, 5),
                       (updateButton, 1, wx.EXPAND, 5)])
        subS2.AddGrowableCol(0, 1)
        subS2.AddGrowableCol(1, 1)

        mainS.AddMany([(subS1, 1, wx.EXPAND, 5),
                       (subS2, 1, wx.EXPAND, 5)])
        mainS.AddGrowableRow(0, 1)
        mainS.AddGrowableCol(0, 1)

        self.SetSizer(mainS)
        self.Layout()


class meta_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        mainS = wx.FlexGridSizer(1, 2, 0, 0)
        mainS.SetFlexibleDirection(wx.BOTH)
        mainS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subS = wx.FlexGridSizer(6, 2, 0, 0)
        subS.SetFlexibleDirection(wx.BOTH)
        subS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        title_static = wx.StaticText(
            self, wx.ID_ANY, u"Title: ", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.title_text = wx.TextCtrl(self, wx.ID_ANY,
                                      wx.EmptyString,
                                      wx.DefaultPosition, wx.DefaultSize)
        material_static = wx.StaticText(
            self, wx.ID_ANY, u"Material: ", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.material_text = wx.TextCtrl(self, wx.ID_ANY,
                                         wx.EmptyString,
                                         wx.DefaultPosition, wx.DefaultSize)
        phase_static = wx.StaticText(
            self, wx.ID_ANY, u"Phase: ", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.phase_text = wx.TextCtrl(self, wx.ID_ANY,
                                      wx.EmptyString,
                                      wx.DefaultPosition, wx.DefaultSize)
        temp_static = wx.StaticText(
            self, wx.ID_ANY, u"Temperature: ", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.temp_text = wx.TextCtrl(self, wx.ID_ANY,
                                     wx.EmptyString,
                                     wx.DefaultPosition, wx.DefaultSize)
        press_static = wx.StaticText(
            self, wx.ID_ANY, u"Pressure: ", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.press_text = wx.TextCtrl(self, wx.ID_ANY,
                                      wx.EmptyString,
                                      wx.DefaultPosition, wx.DefaultSize)
        invest_static = wx.StaticText(
            self, wx.ID_ANY, u"Investigator: ", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.invest_text = wx.TextCtrl(self, wx.ID_ANY,
                                       wx.EmptyString,
                                       wx.DefaultPosition, wx.DefaultSize)

        subS.AddMany([(title_static, 1, wx.EXPAND, 5),
                      (self.title_text, 1, wx.EXPAND, 5),
                      (material_static, 1, wx.EXPAND | wx.ALIGN_RIGHT, 5),
                      (self.material_text, 1, wx.EXPAND | wx.ALIGN_RIGHT, 5),
                      (phase_static, 1, wx.EXPAND | wx.ALIGN_RIGHT, 5),
                      (self.phase_text, 1, wx.EXPAND | wx.ALIGN_RIGHT, 5),
                      (temp_static, 1, wx.EXPAND | wx.ALIGN_RIGHT, 5),
                      (self.temp_text, 1, wx.EXPAND | wx.ALIGN_RIGHT, 5),
                      (press_static, 1, wx.EXPAND | wx.ALIGN_RIGHT, 5),
                      (self.press_text, 1, wx.EXPAND | wx.ALIGN_RIGHT, 5),
                      (invest_static, 1, wx.EXPAND | wx.ALIGN_RIGHT, 5),
                      (self.invest_text, 1, wx.EXPAND | wx.ALIGN_RIGHT, 5)])
        subS.AddGrowableCol(1, 1)

        subS1 = wx.FlexGridSizer(3, 2, 0, 0)
        subS1.SetFlexibleDirection(wx.BOTH)
        subS1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        note_static = wx.StaticText(
            self, wx.ID_ANY, u"Notes on data: ", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.note_text = wx.TextCtrl(self, wx.ID_ANY,
                                     wx.EmptyString,
                                     wx.DefaultPosition, size=(-1, -1),
                                     style=wx.TE_MULTILINE)
        rmc_static = wx.StaticText(
            self, wx.ID_ANY, u"Notes on RMC: ", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.rmc_text = wx.TextCtrl(self, wx.ID_ANY,
                                    wx.EmptyString,
                                    wx.DefaultPosition, size=(-1, -1),
                                    style=wx.TE_MULTILINE)
        comment_static = wx.StaticText(
            self, wx.ID_ANY, u"Comments: ", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.comment_text = wx.TextCtrl(self, wx.ID_ANY,
                                        wx.EmptyString,
                                        wx.DefaultPosition, size=(-1, -1),
                                        style=wx.TE_MULTILINE)

        subS1.AddMany([(note_static, 1, wx.EXPAND, 5),
                       (self.note_text, 1, wx.EXPAND, 5),
                       (rmc_static, 1, wx.EXPAND | wx.ALIGN_RIGHT, 5),
                       (self.rmc_text, 1, wx.EXPAND | wx.ALIGN_RIGHT, 5),
                       (comment_static, 1, wx.EXPAND | wx.ALIGN_RIGHT, 5),
                       (self.comment_text, 1, wx.EXPAND | wx.ALIGN_RIGHT, 5)])
        subS1.AddGrowableRow(0, 1)
        subS1.AddGrowableRow(1, 1)
        subS1.AddGrowableRow(2, 1)
        subS1.AddGrowableCol(1, 1)

        mainS.AddMany([(subS, 1, wx.EXPAND, 5),
                       (subS1, 1, wx.EXPAND, 5)])
        mainS.AddGrowableRow(0, 1)
        mainS.AddGrowableCol(0, 1)
        mainS.AddGrowableCol(1, 1)

        self.SetSizer(mainS)
        self.Layout()


class ds_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        subS3 = wx.FlexGridSizer(2, 4, 0, 0)
        subS3.SetFlexibleDirection(wx.BOTH)
        subS3.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        nr_box = wx.CheckBox(self, label="Neutron r-space")
        nq_box = wx.CheckBox(self, label="Neutron Q-space")
        xray_box = wx.CheckBox(self, label="X-ray")
        bragg_box = wx.CheckBox(self, label="Bragg")
        exafs_box = wx.CheckBox(self, label="EXAFS")
        const_box = wx.CheckBox(self, label="Constraints")
        adv_box = wx.CheckBox(self, label="Advanced")

        subS3.AddMany([(nr_box, 1, wx.EXPAND, 5),
                       (nq_box, 1, wx.EXPAND, 5),
                       (xray_box, 1, wx.EXPAND | wx.ALIGN_RIGHT, 5),
                       (bragg_box, 1, wx.EXPAND | wx.ALIGN_RIGHT, 5),
                       (exafs_box, 1, wx.EXPAND | wx.ALIGN_RIGHT, 5),
                       (const_box, 1, wx.EXPAND | wx.ALIGN_RIGHT, 5),
                       (adv_box, 1, wx.EXPAND | wx.ALIGN_RIGHT, 5)])
        subS3.AddGrowableCol(0, 1)
        subS3.AddGrowableCol(1, 1)
        subS3.AddGrowableCol(2, 1)
        subS3.AddGrowableCol(3, 1)

        self.SetSizer(subS3)
        self.Layout()


class main_prep_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        mainMainS = wx.FlexGridSizer(1, 1, 0, 0)
        mainMainS.SetFlexibleDirection(wx.BOTH)
        mainMainS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.prep_notebook = wx.Notebook(self, wx.ID_ANY, wx.DefaultPosition,
                                         wx.DefaultSize, wx.NB_TOP)
        self.about_panel = wx.Panel(self.prep_notebook, wx.ID_ANY,
                                    wx.DefaultPosition, size=(-1, 100),
                                    style=wx.TAB_TRAVERSAL)

        about_cont = """Various data types available for RMC \
fitting are included in separate tabs. \n\
One can input parameters for data sections under their corresponding tabs.\n\n\
Specifically for X-ray total scattering data, the real and reciprocal \
space data are \n\
bundled together, and therefore one inputs parameters for both in a single tab.\n\n\
All contraints are included in a single tab 'Constraints'.\n\n\
Other advanced features like electron diffraction, single crystal diffuse \
scattering, etc. \n\
are included in another single "Advanced" tab.
        """

        atextS = wx.FlexGridSizer(3, 1, 0, 0)
        atextS.SetFlexibleDirection(wx.BOTH)
        atextS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        about_holder1 = wx.StaticText(
            self.about_panel, wx.ID_ANY, label="",
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.ALIGN_LEFT)

        about_text = wx.StaticText(
            self.about_panel, wx.ID_ANY, label=about_cont,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.ALIGN_LEFT)

        about_holder2 = wx.StaticText(
            self.about_panel, wx.ID_ANY, label="",
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.ALIGN_LEFT)

        font = wx.Font(14, wx.FONTFAMILY_ROMAN, wx.SLANT, wx.NORMAL)
        about_text.SetFont(font)

        atextS.AddMany([(about_holder1, 1, wx.EXPAND, 5),
                        (about_text, 1, wx.EXPAND, 5),
                        (about_holder2, 1, wx.EXPAND, 5)])
        atextS.AddGrowableRow(0, 1)
        atextS.AddGrowableRow(2, 1)
        atextS.AddGrowableCol(0, 1)

        self.about_panel.SetSizer(atextS)
        self.about_panel.Layout()

        self.prep_notebook.AddPage(self.about_panel, u"About", True)

        self.nr_panel = nr_prep_panel(self.prep_notebook)
        self.prep_notebook.AddPage(self.nr_panel, u"Neutron real-space", False)

        self.nq_panel = nq_prep_panel(self.prep_notebook)
        self.prep_notebook.AddPage(self.nq_panel, u"Neutron Q-space", False)

        self.xray_panel = xray_prep_panel(self.prep_notebook)
        self.prep_notebook.AddPage(self.xray_panel, u"X-ray",
                                   False)

        self.bragg_panel = bragg_prep_panel(self.prep_notebook)
        self.prep_notebook.AddPage(self.bragg_panel, u"Bragg",
                                   False)

        self.exafs_panel = exafs_prep_panel(self.prep_notebook)
        self.prep_notebook.AddPage(self.exafs_panel, u"EXAFS", False)

        self.const_panel = const_prep_panel(self.prep_notebook)
        self.prep_notebook.AddPage(self.const_panel, u"Constraints", False)

        self.adv_panel = adv_prep_panel(self.prep_notebook)
        self.prep_notebook.AddPage(self.adv_panel, u"Advanced", False)

        self.others_panel = others_prep_panel(self.prep_notebook)
        self.prep_notebook.AddPage(self.others_panel, u"Others", False)

        mainMainS.AddMany([(self.prep_notebook, 1, wx.EXPAND, 5)])
        mainMainS.AddGrowableRow(0, 1)
        mainMainS.AddGrowableCol(0, 1)

        self.SetSizer(mainMainS)
        self.Layout()


class pos_rmc_panel(wx.Panel):
    def __init__(self, parent):

        wx.Panel.__init__(self, parent)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        mainMainS = wx.FlexGridSizer(5, 1, 0, 0)
        mainMainS.SetFlexibleDirection(wx.BOTH)
        mainMainS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subS1 = wx.FlexGridSizer(1, 2, 0, 0)
        subS1.SetFlexibleDirection(wx.BOTH)
        subS1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.rmc_plotter_notebook = wx.Notebook(self, wx.ID_ANY,
                                                wx.DefaultPosition,
                                                wx.DefaultSize, wx.NB_TOP)
        self.rmc_plotter_panel = rmc_plotter_panel(self.rmc_plotter_notebook)
        self.rmc_plotter_notebook.AddPage(self.rmc_plotter_panel,
                                          u"RMC Plotter", True)

        self.cpc_notebook = wx.Notebook(self, wx.ID_ANY, wx.DefaultPosition,
                                        wx.DefaultSize, wx.NB_TOP)
        self.cpc_panel = cpc_panel(self.cpc_notebook)
        self.cpc_notebook.AddPage(self.cpc_panel,
                                  u"Config Plotter & Converter", True)

        subS1.AddMany([(self.rmc_plotter_notebook, 1, wx.EXPAND, 5),
                       (self.cpc_notebook, 1, wx.EXPAND, 5)])
        subS1.AddGrowableCol(0, 1)
        subS1.AddGrowableCol(1, 1)

        self.rmc_tools_notebook = wx.Notebook(self, wx.ID_ANY,
                                              wx.DefaultPosition,
                                              wx.DefaultSize, wx.NB_TOP)
        self.rmc_tools_panel = rmc_tools_panel(self.rmc_tools_notebook)
        self.rmc_tools_notebook.AddPage(self.rmc_tools_panel,
                                        u"RMC Tools", True)

        mainMainS.AddMany([(subS1, 1, wx.EXPAND, 5),
                           (self.rmc_tools_notebook, 1, wx.EXPAND, 5)])
        mainMainS.AddGrowableCol(0, 1)
        mainMainS.AddGrowableRow(1, 1)

        self.SetSizer(mainMainS)
        self.Layout()


class rmc_plotter_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        mainS = wx.FlexGridSizer(2, 1, 0, 0)
        mainS.SetFlexibleDirection(wx.BOTH)
        mainS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subS1 = wx.FlexGridSizer(1, 3, 0, 0)
        subS1.SetFlexibleDirection(wx.BOTH)
        subS1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        loadPButton = wx.Button(
            self, wx.ID_ANY, u"Load RMC Project", wx.DefaultPosition,
            wx.DefaultSize, 0)

        or_static = wx.StaticText(
            self, wx.ID_ANY, u"   or   ", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)

        loadRFButton = wx.Button(
            self, wx.ID_ANY, u"Select RMC folder", wx.DefaultPosition,
            wx.DefaultSize, 0)

        subS1.AddMany([(loadPButton, 1, wx.EXPAND, 5),
                       (or_static, 1, wx.EXPAND, 5),
                       (loadRFButton, 1, wx.EXPAND, 5)])
        subS1.AddGrowableCol(0, 1)
        subS1.AddGrowableCol(2, 1)

        lRPButton = wx.Button(
            self, wx.ID_ANY, u"Launch RMC plotter", wx.DefaultPosition,
            wx.DefaultSize, 0)

        mainS.AddMany([(subS1, 1, wx.EXPAND, 5),
                       (lRPButton, 1, wx.EXPAND, 5)])
        mainS.AddGrowableCol(0, 1)

        self.SetSizer(mainS)
        self.Layout()


class cpc_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        mainS = wx.FlexGridSizer(2, 1, 0, 0)
        mainS.SetFlexibleDirection(wx.BOTH)
        mainS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        lcpButton = wx.Button(
            self, wx.ID_ANY, u"Launch config plotter", wx.DefaultPosition,
            wx.DefaultSize, 0)

        lccButton = wx.Button(
            self, wx.ID_ANY, u"Launch config converter", wx.DefaultPosition,
            wx.DefaultSize, 0)

        mainS.AddMany([(lcpButton, 1, wx.EXPAND, 5),
                       (lccButton, 1, wx.EXPAND, 5)])
        mainS.AddGrowableCol(0, 1)

        self.SetSizer(mainS)
        self.Layout()


class rmc_tools_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        mainS = wx.FlexGridSizer(4, 1, 0, 0)
        mainS.SetFlexibleDirection(wx.BOTH)
        mainS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)
        
        subS1 = wx.FlexGridSizer(1, 2, 0, 0)
        subS1.SetFlexibleDirection(wx.BOTH)
        subS1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)
        
        rmc_ins_f_Button = wx.Button(
            self, wx.ID_ANY, u"Select RMCProfile installation directory",
            wx.DefaultPosition,
            wx.DefaultSize, 0)
        
        work_dir_Button = wx.Button(
            self, wx.ID_ANY, u"Select working directory", wx.DefaultPosition,
            wx.DefaultSize, 0)
        
        subS1.AddMany([(rmc_ins_f_Button, 1, wx.EXPAND, 5),
                       (work_dir_Button, 1, wx.EXPAND, 5)])
        subS1.AddGrowableCol(0, 1)
        subS1.AddGrowableCol(1, 1)
        
        subS2 = wx.FlexGridSizer(2, 4, 0, 0)
        subS2.SetFlexibleDirection(wx.BOTH)
        subS2.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)
        
        teButton = wx.Button(
            self, wx.ID_ANY, u"Thermal Ellipsoid", wx.DefaultPosition,
            wx.DefaultSize, 0)
        
        qButton1 = wx.Button(
            self, wx.ID_ANY, u"<-?", wx.DefaultPosition,
            wx.DefaultSize, 0)
        
        adButton = wx.Button(
            self, wx.ID_ANY, u"Angle distribution", wx.DefaultPosition,
            wx.DefaultSize, 0)
        
        qButton2 = wx.Button(
            self, wx.ID_ANY, u"<-?", wx.DefaultPosition,
            wx.DefaultSize, 0)
        
        uccButton = wx.Button(
            self, wx.ID_ANY, u"Unit cell collapse", wx.DefaultPosition,
            wx.DefaultSize, 0)
        
        qButton3 = wx.Button(
            self, wx.ID_ANY, u"<-?", wx.DefaultPosition,
            wx.DefaultSize, 0)
        
        hdButton = wx.Button(
            self, wx.ID_ANY, u"Histogram data", wx.DefaultPosition,
            wx.DefaultSize, 0)
        
        qButton4 = wx.Button(
            self, wx.ID_ANY, u"<-?", wx.DefaultPosition,
            wx.DefaultSize, 0)
        
        subS2.AddMany([(teButton, 1, wx.EXPAND, 5),
                       (qButton1, 1, wx.EXPAND, 5),
                       (adButton, 1, wx.EXPAND, 5),
                       (qButton2, 1, wx.EXPAND, 5),
                       (uccButton, 1, wx.EXPAND, 5),
                       (qButton3, 1, wx.EXPAND, 5),
                       (hdButton, 1, wx.EXPAND, 5),
                       (qButton4, 1, wx.EXPAND, 5)])
        subS2.AddGrowableCol(0, 1)
        subS2.AddGrowableCol(1, 1)
        subS2.AddGrowableCol(2, 1)
        subS2.AddGrowableCol(3, 1)
        
        ph_static = wx.StaticText(
            self, wx.ID_ANY, u"", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)        
        
        lrmcButton = wx.Button(
            self, wx.ID_ANY,
            u"Launch RMC terminal to get access to more tools",
            wx.DefaultPosition,
            wx.DefaultSize, 0)
        
        mainS.AddMany([(subS1, 1, wx.EXPAND, 5),
                       (ph_static, 1, wx.EXPAND, 5),
                       (subS2, 1, wx.EXPAND, 5),
                       (lrmcButton, 1, wx.EXPAND, 5)])
        mainS.AddGrowableCol(0, 1)
        mainS.AddGrowableRow(2, 1)

        self.SetSizer(mainS)
        self.Layout()


class rmc_main_panel(wx.Panel):
    def __init__(self, parent):

        self.sect_inc = ['No data section yet...']

        wx.Panel.__init__(self, parent)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        mainMainS = wx.FlexGridSizer(5, 1, 0, 0)
        mainMainS.SetFlexibleDirection(wx.BOTH)
        mainMainS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subS1 = wx.FlexGridSizer(1, 3, 0, 0)
        subS1.SetFlexibleDirection(wx.BOTH)
        subS1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        loadPButton = wx.Button(
            self, wx.ID_ANY, u"Open project", wx.DefaultPosition,
            wx.DefaultSize, 0)
        loadFButton = wx.Button(
            self, wx.ID_ANY, u"Open RMC folder", wx.DefaultPosition,
            wx.DefaultSize, 0)
        loadDButton = wx.Button(
            self, wx.ID_ANY, u"Open input (.dat) file", wx.DefaultPosition,
            wx.DefaultSize, 0)

        subS1.AddMany([(loadPButton, 1, wx.EXPAND, 5),
                       (loadFButton, 1, wx.EXPAND, 5),
                       (loadDButton, 1, wx.EXPAND, 5)])
        subS1.AddGrowableCol(0, 1)
        subS1.AddGrowableCol(1, 1)
        subS1.AddGrowableCol(2, 1)

        subS2 = wx.FlexGridSizer(1, 2, 0, 0)
        subS2.SetFlexibleDirection(wx.BOTH)
        subS2.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.meta_notebook = wx.Notebook(self, wx.ID_ANY, wx.DefaultPosition,
                                         wx.DefaultSize, wx.NB_TOP)
        self.meta_panel = meta_panel(self.meta_notebook)
        self.meta_notebook.AddPage(self.meta_panel, u"Metadata", True)

        self.fc_notebook = wx.Notebook(self, wx.ID_ANY, wx.DefaultPosition,
                                       wx.DefaultSize, wx.NB_TOP)
        self.fc_panel = fc_panel(self.fc_notebook)
        self.fc_notebook.AddPage(self.fc_panel, u"Flag and control", True)

        subS2.AddMany([(self.meta_notebook, 1, wx.EXPAND, 5),
                       (self.fc_notebook, 1, wx.EXPAND, 5)])
        subS2.AddGrowableCol(0, 1)
        subS2.AddGrowableCol(1, 1)

        subS3 = wx.FlexGridSizer(1, 2, 0, 0)
        subS3.SetFlexibleDirection(wx.BOTH)
        subS3.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.ds_notebook = wx.Notebook(self, wx.ID_ANY, wx.DefaultPosition,
                                       wx.DefaultSize, wx.NB_TOP)
        self.ds_panel = ds_panel(self.ds_notebook)
        self.ds_notebook.AddPage(self.ds_panel, u"Check to use in RMC", True)

        self.main_prep_panel = main_prep_panel(self)

        subS3R = wx.FlexGridSizer(2, 1, 0, 0)
        subS3R.SetFlexibleDirection(wx.BOTH)
        subS3R.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.sect_list = wx.ListBox(self, size=(-1, -1),
                                    choices=self.sect_inc,
                                    style=wx.LB_MULTIPLE)

        subS3R1 = wx.FlexGridSizer(1, 2, 0, 0)
        subS3R1.SetFlexibleDirection(wx.BOTH)
        subS3R1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        sname_static = wx.StaticText(
            self, wx.ID_ANY, label="Stem name: ",
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.ALIGN_LEFT)
        self.sname_text = wx.TextCtrl(self, wx.ID_ANY,
                                      wx.EmptyString,
                                      wx.DefaultPosition, size=(260, -1))
        subS3R1.AddMany([(sname_static, 1, wx.EXPAND, 5),
                         (self.sname_text, 1, wx.EXPAND, 5)])
        subS3R1.AddGrowableCol(1, 1)

        subS3R.AddMany([(self.sect_list, 1, wx.EXPAND, 5),
                        (subS3R1, 1, wx.EXPAND, 5)])
        subS3R.AddGrowableRow(0, 1)
        subS3R.AddGrowableCol(0, 1)

        subS3.AddMany([(self.main_prep_panel, 1, wx.EXPAND, 5),
                       (subS3R, 1, wx.EXPAND, 5)])
        subS3.AddGrowableCol(0, 1)
        subS3.AddGrowableRow(0, 1)

        subS4 = wx.FlexGridSizer(1, 3, 0, 0)
        subS4.SetFlexibleDirection(wx.BOTH)
        subS4.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        savePButton = wx.Button(
            self, wx.ID_ANY, u"Save project", wx.DefaultPosition,
            wx.DefaultSize, 0)
        saveFButton = wx.Button(
            self, wx.ID_ANY, u"Generate RMC folder", wx.DefaultPosition,
            wx.DefaultSize, 0)
        saveDButton = wx.Button(
            self, wx.ID_ANY, u"Generate input (.dat) file", wx.DefaultPosition,
            wx.DefaultSize, 0)

        subS4.AddMany([(savePButton, 1, wx.EXPAND, 5),
                       (saveFButton, 1, wx.EXPAND, 5),
                       (saveDButton, 1, wx.EXPAND, 5)])
        subS4.AddGrowableCol(0, 1)
        subS4.AddGrowableCol(1, 1)
        subS4.AddGrowableCol(2, 1)

        mainMainS.AddMany([(subS1, 1, wx.EXPAND, 5),
                           (subS2, 1, wx.EXPAND, 5),
                           (self.ds_notebook, 1, wx.EXPAND, 5),
                           (subS3, 1, wx.EXPAND, 5),
                           (subS4, 1, wx.EXPAND, 5)])
        mainMainS.AddGrowableCol(0, 1)
        mainMainS.AddGrowableRow(3, 1)

        self.SetSizer(mainMainS)
        self.Layout()


class config_prep_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        mainMainS = wx.FlexGridSizer(1, 3, 0, 0)
        mainMainS.SetFlexibleDirection(wx.BOTH)
        mainMainS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        leftS = wx.FlexGridSizer(3, 1, 0, 0)
        leftS.SetFlexibleDirection(wx.BOTH)
        leftS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        loadCButton = wx.Button(
            self, wx.ID_ANY, u"Load Input Structure", wx.DefaultPosition,
            wx.DefaultSize, 0)

        leftS1 = wx.FlexGridSizer(1, 2, 0, 0)
        leftS1.SetFlexibleDirection(wx.BOTH)
        leftS1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        opt_avail_static = wx.StaticText(
            self, wx.ID_ANY, u"Options available", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        opt_val_static = wx.StaticText(
            self, wx.ID_ANY, u"Option value list", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        opt_val_static1 = wx.StaticText(
            self, wx.ID_ANY, u"Option value input", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)

        leftS2 = wx.FlexGridSizer(2, 1, 0, 0)
        leftS2.SetFlexibleDirection(wx.BOTH)
        leftS2.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.opt_avail = ['Supercell dimension', 'Output format']
        opt_list = wx.ListBox(self, size=(-1, -1),
                              choices=self.opt_avail,
                              style=wx.LB_SINGLE)

        leftS2.AddMany([(opt_avail_static, 1, wx.EXPAND, 5),
                        (opt_list, 1, wx.EXPAND, 5)])
        leftS2.AddGrowableRow(1, 1)
        leftS2.AddGrowableCol(0, 1)

        leftS3 = wx.FlexGridSizer(6, 1, 0, 0)
        leftS3.SetFlexibleDirection(wx.BOTH)
        leftS3.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.opt_val = []
        val_list = wx.ListBox(self, size=(-1, -1),
                              choices=self.opt_val,
                              style=wx.LB_MULTIPLE)
        self.val_text = wx.TextCtrl(self, wx.ID_ANY,
                                    wx.EmptyString,
                                    wx.DefaultPosition, wx.DefaultSize)

        note_static = wx.StaticText(
            self, wx.ID_ANY, u"Note/Metadata", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.note_text = wx.TextCtrl(self, wx.ID_ANY,
                                     wx.EmptyString,
                                     wx.DefaultPosition, wx.DefaultSize)
        leftS3.AddMany([(opt_val_static, 1, wx.EXPAND, 5),
                        (val_list, 1, wx.EXPAND, 5),
                        (opt_val_static1, 1, wx.EXPAND, 5),
                        (self.val_text, 1, wx.EXPAND, 5),
                        (note_static, 1, wx.EXPAND, 5),
                        (self.note_text, 1, wx.EXPAND, 5)])
        leftS3.AddGrowableRow(1, 1)
        leftS3.AddGrowableRow(5, 1)
        leftS3.AddGrowableCol(0, 1)

        leftS1.AddMany([(leftS2, 1, wx.EXPAND, 5),
                        (leftS3, 1, wx.EXPAND, 5)])
        leftS1.AddGrowableRow(0, 1)
        leftS1.AddGrowableCol(0, 1)
        leftS1.AddGrowableCol(1, 1)

        helpButton = wx.Button(
            self, wx.ID_ANY, u"Documentation", wx.DefaultPosition,
            wx.DefaultSize, 0)

        leftS.AddMany([(loadCButton, 1, wx.EXPAND, 5),
                       (leftS1, 1, wx.EXPAND, 5),
                       (helpButton, 1, wx.EXPAND, 5)])
        leftS.AddGrowableRow(1, 1)
        leftS.AddGrowableCol(0, 1)

        middleS = wx.FlexGridSizer(3, 1, 0, 0)
        middleS.SetFlexibleDirection(wx.BOTH)
        middleS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        holder1 = wx.StaticText(
            self, wx.ID_ANY, u"", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        goButton = wx.Button(
            self, wx.ID_ANY, u"->", wx.DefaultPosition,
            size=(40, -1))
        holder2 = wx.StaticText(
            self, wx.ID_ANY, u"", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)

        middleS.AddMany([(holder1, 1, wx.EXPAND, 5),
                         (goButton, 1, wx.EXPAND, 5),
                         (holder2, 1, wx.EXPAND, 5)])
        middleS.AddGrowableRow(0, 1)
        middleS.AddGrowableRow(2, 1)

        rightS = wx.FlexGridSizer(2, 1, 0, 0)
        rightS.SetFlexibleDirection(wx.BOTH)
        rightS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        rightS1 = wx.FlexGridSizer(3, 2, 0, 0)
        rightS1.SetFlexibleDirection(wx.BOTH)
        rightS1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        loadFButton = wx.Button(
            self, wx.ID_ANY, u"Load flags", wx.DefaultPosition,
            size=(10, -1))
        saveFButton = wx.Button(
            self, wx.ID_ANY, u"Save flags", wx.DefaultPosition,
            size=(10, -1))
        opt_used_static = wx.StaticText(
            self, wx.ID_ANY, u"Options used", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        val_used_static = wx.StaticText(
            self, wx.ID_ANY, u"Value", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        self.opt_used = []
        opt_used_list = wx.ListBox(self, size=(-1, -1),
                                   choices=self.opt_used,
                                   style=wx.LB_SINGLE)
        val_used_text = wx.TextCtrl(self, wx.ID_ANY,
                                    wx.EmptyString,
                                    wx.DefaultPosition, wx.DefaultSize,
                                    wx.TE_MULTILINE | wx.TE_READONLY)
        rightS1.AddMany([(loadFButton, 1, wx.EXPAND, 5),
                         (saveFButton, 1, wx.EXPAND, 5),
                         (opt_used_static, 1, wx.EXPAND, 5),
                         (val_used_static, 1, wx.EXPAND, 5),
                         (opt_used_list, 1, wx.EXPAND, 5),
                         (val_used_text, 1, wx.EXPAND, 5)])
        rightS1.AddGrowableRow(2, 1)
        rightS1.AddGrowableCol(0, 1)
        rightS1.AddGrowableCol(1, 1)

        exportButton = wx.Button(
            self, wx.ID_ANY, u"Export Structure", wx.DefaultPosition,
            size=(10, -1))

        rightS.AddMany([(rightS1, 1, wx.EXPAND, 5),
                        (exportButton, 1, wx.EXPAND, 5)])
        rightS.AddGrowableRow(0, 1)
        rightS.AddGrowableCol(0, 1)

        mainMainS.AddMany([(leftS, 1, wx.EXPAND, 5),
                           (middleS, 1, wx.EXPAND, 5),
                           (rightS, 1, wx.EXPAND, 5)])
        mainMainS.AddGrowableRow(0, 1)
        mainMainS.AddGrowableCol(0, 1)
        mainMainS.AddGrowableCol(2, 1)

        self.SetSizer(mainMainS)
        self.Layout()


class data_proc_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        mainMainS = wx.FlexGridSizer(7, 1, 0, 0)
        mainMainS.SetFlexibleDirection(wx.BOTH)
        mainMainS.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subS1 = wx.FlexGridSizer(1, 3, 0, 0)
        subS1.SetFlexibleDirection(wx.BOTH)
        subS1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subS1a = wx.FlexGridSizer(4, 1, 0, 0)
        subS1a.SetFlexibleDirection(wx.BOTH)
        subS1a.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subS1aa = wx.FlexGridSizer(2, 1, 0, 0)
        subS1aa.SetFlexibleDirection(wx.BOTH)
        subS1aa.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subS1aaa = wx.FlexGridSizer(1, 2, 0, 0)
        subS1aaa.SetFlexibleDirection(wx.BOTH)
        subS1aaa.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        dpBButton = wx.Button(
            self, wx.ID_ANY, u"Load Files", wx.DefaultPosition,
            wx.DefaultSize, 0)
        dpFButton = wx.Button(
            self, wx.ID_ANY, u"Open Folder", wx.DefaultPosition,
            wx.DefaultSize, 0)
        dpPButton = wx.Button(
            self, wx.ID_ANY, u"Plot", wx.DefaultPosition,
            wx.DefaultSize, 0)

        subS1aaa.AddMany([(dpBButton, 1, wx.EXPAND, 5),
                          (dpFButton, 1, wx.EXPAND, 5)])
        subS1aaa.AddGrowableRow(0, 1)
        subS1aaa.AddGrowableCol(0, 1)
        subS1aaa.AddGrowableCol(1, 1)

        b_group = wx.FlexGridSizer(2, 1, 0, 0)
        b_group.SetFlexibleDirection(wx.BOTH)
        b_group.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)
        b_group.AddMany([(subS1aaa, 1, wx.EXPAND, 5),
                         (dpPButton, 1, wx.EXPAND, 5)])
        b_group.AddGrowableRow(0, 1)
        b_group.AddGrowableRow(1, 1)
        b_group.AddGrowableCol(0, 1)

        self.loaded_files = ['Load files/folder to plot']
        file_list = wx.ListBox(self, size=(-1, -1),
                               choices=self.loaded_files,
                               style=wx.LB_MULTIPLE)

        subS1aa.AddMany([(file_list, 1, wx.EXPAND, 5),
                         (b_group, 1, wx.EXPAND, 5)])
        subS1aa.AddGrowableRow(0, 1)
        subS1aa.AddGrowableCol(0, 1)

        subS1aL1 = wx.StaticLine(self, wx.ID_ANY, size=(-1, -1),
                                 style=wx.LI_HORIZONTAL)
        data_plotter_static = wx.StaticText(
            self, wx.ID_ANY, u"Data plotter", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        subS1aL2 = wx.StaticLine(self, wx.ID_ANY, size=(-1, -1),
                                 style=wx.LI_HORIZONTAL)

        subS1a.AddMany([(subS1aL1, 1, wx.EXPAND, 5),
                        (data_plotter_static, 1, wx.EXPAND, 5),
                        (subS1aL2, 1, wx.EXPAND, 5),
                        (subS1aa, 1, wx.EXPAND, 5)])
        subS1a.AddGrowableRow(3, 1)
        subS1a.AddGrowableCol(0, 1)

        subS1aLb = wx.StaticLine(self, wx.ID_ANY, size=(-1, -1),
                                 style=wx.LI_VERTICAL)

        subS1b = wx.FlexGridSizer(3, 2, 0, 0)
        subS1b.SetFlexibleDirection(wx.BOTH)
        subS1b.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        calib_merge_button = wx.Button(
            self, wx.ID_ANY, u"Calib and Merge", wx.DefaultPosition,
            wx.DefaultSize, 0)
        calib_merge_Q = wx.Button(
            self, wx.ID_ANY, u"<-?", wx.DefaultPosition,
            wx.DefaultSize, 0)
        rebin_button = wx.Button(
            self, wx.ID_ANY, u"Rebin", wx.DefaultPosition,
            wx.DefaultSize, 0)
        rebin_Q = wx.Button(
            self, wx.ID_ANY, u"<-?", wx.DefaultPosition,
            wx.DefaultSize, 0)
        stog_sec = wx.Button(
            self, wx.ID_ANY, u"SofQ2PDF", wx.DefaultPosition,
            wx.DefaultSize, 0)
        stog_sec_Q = wx.Button(
            self, wx.ID_ANY, u"<-?", wx.DefaultPosition,
            wx.DefaultSize, 0)
        bragg_sec = wx.Button(
            self, wx.ID_ANY, u"Topas2RMC", wx.DefaultPosition,
            wx.DefaultSize, 0)
        bragg_sec_Q = wx.Button(
            self, wx.ID_ANY, u"<-?", wx.DefaultPosition,
            wx.DefaultSize, 0)
        exafs_sec = wx.Button(
            self, wx.ID_ANY, u"EXAFS2RMC", wx.DefaultPosition,
            wx.DefaultSize, 0)
        exafs_sec_Q = wx.Button(
            self, wx.ID_ANY, u"<-?", wx.DefaultPosition,
            wx.DefaultSize, 0)

        subS1b.AddMany([(calib_merge_button, 1, wx.EXPAND, 5),
                        (calib_merge_Q, 1, wx.EXPAND, 5),
                        (rebin_button, 1, wx.EXPAND, 5),
                        (rebin_Q, 1, wx.EXPAND, 5),
                        (stog_sec, 1, wx.EXPAND, 5),
                        (stog_sec_Q, 1, wx.EXPAND, 5)])
        subS1b.AddGrowableCol(0, 1)
        subS1b.AddGrowableCol(1, 1)

        subS1bb = wx.FlexGridSizer(1, 2, 0, 0)
        subS1bb.SetFlexibleDirection(wx.BOTH)
        subS1bb.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subS1bb.AddMany([(bragg_sec, 1, wx.EXPAND, 5),
                         (bragg_sec_Q, 1, wx.EXPAND, 5)])
        subS1bb.AddGrowableCol(0, 1)
        subS1bb.AddGrowableCol(1, 1)

        subS1bbb = wx.FlexGridSizer(1, 2, 0, 0)
        subS1bbb.SetFlexibleDirection(wx.BOTH)
        subS1bbb.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subS1bbb.AddMany([(exafs_sec, 1, wx.EXPAND, 5),
                          (exafs_sec_Q, 1, wx.EXPAND, 5)])
        subS1bbb.AddGrowableCol(0, 1)
        subS1bbb.AddGrowableCol(1, 1)

        subS1bL1 = wx.StaticLine(self, wx.ID_ANY, size=(-1, -1),
                                 style=wx.LI_HORIZONTAL)
        ts_static = wx.StaticText(
            self, wx.ID_ANY, u"Total Scattering Data", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        subS1bL2 = wx.StaticLine(self, wx.ID_ANY, size=(-1, -1),
                                 style=wx.LI_HORIZONTAL)
        subS1bL3 = wx.StaticLine(self, wx.ID_ANY, size=(-1, -1),
                                 style=wx.LI_HORIZONTAL)
        bragg_static = wx.StaticText(
            self, wx.ID_ANY, u"Bragg Data", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        subS1bL4 = wx.StaticLine(self, wx.ID_ANY, size=(-1, -1),
                                 style=wx.LI_HORIZONTAL)
        subS1bL5 = wx.StaticLine(self, wx.ID_ANY, size=(-1, -1),
                                 style=wx.LI_HORIZONTAL)
        exafs_static = wx.StaticText(
            self, wx.ID_ANY, u"EXAFS Data", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        subS1bL6 = wx.StaticLine(self, wx.ID_ANY, size=(-1, -1),
                                 style=wx.LI_HORIZONTAL)

        holder = wx.StaticText(
            self, wx.ID_ANY, u"", wx.DefaultPosition,
            wx.DefaultSize,
            wx.ALIGN_CENTRE_HORIZONTAL)
        readme = wx.Button(
            self, wx.ID_ANY, u"README!", wx.DefaultPosition,
            wx.DefaultSize, 0)

        subS1bF = wx.FlexGridSizer(14, 1, 0, 0)
        subS1bF.SetFlexibleDirection(wx.BOTH)
        subS1bF.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        subS1bF.AddMany([(subS1bL1, 1, wx.EXPAND, 5),
                         (ts_static, 1, wx.EXPAND, 5),
                         (subS1bL2, 1, wx.EXPAND, 5),
                         (subS1b, 1, wx.EXPAND, 5),
                         (subS1bL3, 1, wx.EXPAND, 5),
                         (bragg_static, 1, wx.EXPAND, 5),
                         (subS1bL4, 1, wx.EXPAND, 5),
                         (subS1bb, 1, wx.EXPAND, 5),
                         (subS1bL5, 1, wx.EXPAND, 5),
                         (exafs_static, 1, wx.EXPAND, 5),
                         (subS1bL6, 1, wx.EXPAND, 5),
                         (subS1bbb, 1, wx.EXPAND, 5),
                         (holder, 1, wx.EXPAND, 5),
                         (readme, 1, wx.EXPAND, 5)
                         ])
        subS1bF.AddGrowableRow(12, 1)
        subS1bF.AddGrowableCol(0, 1)

        subS1.AddMany([(subS1a, 1, wx.EXPAND, 5),
                       (subS1aLb, 1, wx.EXPAND, 5),
                       (subS1bF, 1, wx.EXPAND, 5)])
        subS1.AddGrowableRow(0, 1)
        subS1.AddGrowableCol(0, 1)

        mainMainS.AddMany([(subS1, 1, wx.EXPAND, 5)])
        mainMainS.AddGrowableRow(0, 1)
        mainMainS.AddGrowableCol(0, 1)

        self.SetSizer(mainMainS)
        self.Layout()


class MainFrame (wx.Frame):

    def __init__(self, parent):
        wx.Frame.__init__(self, None, wx.ID_ANY, title=u"RMCP2P",
                          pos=wx.DefaultPosition, size=wx.Size(1000, 700),
                          style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        self.m_menubar1 = wx.MenuBar(0)
        self.files_menu = wx.Menu()
        self.m_menubar1.Append(self.files_menu, u"Files")

        self.help_menu = wx.Menu()
        self.m_menubar1.Append(self.help_menu, u"Help")

        self.SetMenuBar(self.m_menubar1)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.main_notebook = wx.Notebook(self, wx.ID_ANY, wx.DefaultPosition,
                                         wx.DefaultSize, wx.NB_TOP)

        self.welcome_panel = wx.Panel(self.main_notebook, wx.ID_ANY,
                                      wx.DefaultPosition, wx.DefaultSize,
                                      wx.TAB_TRAVERSAL, u"welcome_panel")
        wp_sizer = wx.BoxSizer(wx.VERTICAL)

        if getattr(sys, 'frozen', False):
            # frozen
            package_directory = os.path.dirname(sys.executable)
        else:
            # unfrozen
            package_directory = os.path.dirname(os.path.abspath(__file__))

        ico = wx.Icon(os.path.join(package_directory, "stuff",
                                   "rmc_logo.ico"), wx.BITMAP_TYPE_ICO)
        self.SetIcon(ico)

        self.rmc_logoI = wx.Image(os.path.join(package_directory, "stuff",
                                               "Complexmodelling_rmc.png"),
                                  wx.BITMAP_TYPE_PNG).ConvertToBitmap()

        self.rmc_logo = wx.StaticBitmap(self.welcome_panel, wx.ID_ANY,
                                        wx.Bitmap(
                                            self.rmc_logoI), wx.Point(-1, -1),
                                        wx.Size(400, 400), 0)
        self.rmc_logo.SetMinSize(wx.Size(400, 400))
        self.rmc_logo.SetMaxSize(wx.Size(400, 400))

        wp_sizer.Add(self.rmc_logo, 0, wx.ALIGN_CENTER, 5)

        rmc_intro = """RMCProfile is a package for fitting \
atomic structure against data of various types, based on Reverse \
Monte Carlo method. \
This GUI is created to make the workflow of using RMCProfile easier \
to follow, from the data and input configuration preparation, to main \
input setup and to post-analysis.
"""

        self.rmc_intro_label = wx.StaticText(self.welcome_panel, wx.ID_ANY,
                                             rmc_intro,
                                             wx.DefaultPosition,
                                             wx.DefaultSize, 0)
        self.rmc_intro_label.Wrap(-1)
        wp_sizer.Add(self.rmc_intro_label, 0, wx.ALL, 5)

        cite_label = """ [1] M. G. Tucker, D. A. Keen, M. T. Dove, A. L. \
Goodwin and Q. Hui, 2007 J. Phys.: Condens. Matter, 19, 335218; \
[2] Y. P. Zhang and M. G. Tucker, in preparation."""

        self.cite_label = wx.StaticText(self.welcome_panel, wx.ID_ANY,
                                        u"Citation: " + cite_label,
                                        wx.DefaultPosition,
                                        wx.DefaultSize, 0)
        self.cite_label.Wrap(-1)
        wp_sizer.Add(self.cite_label, 0, wx.ALL, 5)

        self.author_label = wx.StaticText(self.welcome_panel, wx.ID_ANY,
                                          u"GUI Author: Yuanpeng Zhang" +
                                          "; Email: zyroc1990@gmail.com",
                                          wx.DefaultPosition,
                                          wx.DefaultSize, 0)
        self.author_label.Wrap(-1)
        wp_sizer.Add(self.author_label, 0, wx.ALL, 5)

        self.welcome_panel.SetSizer(wp_sizer)
        self.welcome_panel.Layout()
        wp_sizer.Fit(self.welcome_panel)
        self.main_notebook.AddPage(self.welcome_panel, u"Welcome", True)

        self.prep_panel = wx.Panel(self.main_notebook, wx.ID_ANY,
                                   wx.DefaultPosition, wx.DefaultSize,
                                   wx.TAB_TRAVERSAL, u"prep_panel")
        prep_panel_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.prep_panel_splitter = wx.SplitterWindow(self.prep_panel,
                                                     wx.ID_ANY,
                                                     wx.DefaultPosition,
                                                     wx.DefaultSize, wx.SP_3D)
        self.prep_panel_splitter.Bind(wx.EVT_IDLE,
                                      self.prep_panel_splitterOnIdle)

        self.prep_panel_left = wx.Notebook(self.prep_panel_splitter, wx.ID_ANY,
                                           wx.DefaultPosition,
                                           size=(650, -1), style=wx.NB_TOP)

        self.data_proc_panel = data_proc_panel(self.prep_panel_left)

        self.config_prep_panel = config_prep_panel(self.prep_panel_left)

        self.prep_panel_left.AddPage(self.data_proc_panel,
                                     u"Data preparation", True)
        self.prep_panel_left.AddPage(self.config_prep_panel,
                                     u"Configuration preparation", False)

        self.prep_panel_right = wx.Notebook(self.prep_panel_splitter,
                                            wx.ID_ANY,
                                            wx.DefaultPosition,
                                            wx.DefaultSize, wx.NB_TOP)

        self.log_panel = wx.Panel(self.prep_panel_right, wx.ID_ANY,
                                  wx.DefaultPosition, wx.DefaultSize,
                                  wx.TAB_TRAVERSAL, u"data_proc_panel")

        fgSizer1 = wx.FlexGridSizer(2, 1, 0, 0)
        fgSizer1.SetFlexibleDirection(wx.BOTH)
        fgSizer1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.log_text = wx.TextCtrl(self.log_panel, wx.ID_ANY,
                                    wx.EmptyString,
                                    wx.DefaultPosition, wx.DefaultSize,
                                    wx.TE_MULTILINE | wx.TE_READONLY)

        self.export_log = wx.Button(self.log_panel, wx.ID_ANY,
                                    u"Export log", wx.DefaultPosition,
                                    wx.DefaultSize, 0)

        fgSizer1.AddMany([(self.log_text, 1, wx.EXPAND, 5),
                          (self.export_log, 1, wx.EXPAND, 5)])

        fgSizer1.AddGrowableRow(0, 1)
        fgSizer1.AddGrowableCol(0, 1)

        self.log_panel.SetSizer(fgSizer1)
        self.log_panel.Layout()
        fgSizer1.Fit(self.log_panel)

        self.prep_panel_right.AddPage(self.log_panel,
                                      u"Log", True)

        self.prep_panel_splitter.SplitVertically(self.prep_panel_left,
                                                 self.prep_panel_right, 0)
        self.prep_panel_splitter.SetSashGravity(0.5)

        prep_panel_sizer.Add(self.prep_panel_splitter, 1, wx.EXPAND, 5)

        self.prep_panel.SetSizer(prep_panel_sizer)
        self.prep_panel.Layout()
        prep_panel_sizer.Fit(self.prep_panel)

        self.main_notebook.AddPage(self.prep_panel, u"Preparation", False)

        self.rmc_main = rmc_main_panel(self.main_notebook)

        self.main_notebook.AddPage(self.rmc_main, u"RMC Main Input", False)

        self.post_rmc = pos_rmc_panel(self.main_notebook)

        self.main_notebook.AddPage(self.post_rmc, u"Post-RMC Analysis", False)

        main_sizer.Add(self.main_notebook, 1, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(main_sizer)
        self.Layout()

        self.Centre(wx.BOTH)

    def __del__(self):
        pass

    def prep_panel_splitterOnIdle(self, event):
        self.prep_panel_splitter.SetSashPosition(0)
        self.prep_panel_splitter.Unbind(wx.EVT_IDLE)

    def m_splitter2OnIdle(self, event):
        self.m_splitter2.SetSashPosition(0)
        self.m_splitter2.Unbind(wx.EVT_IDLE)


def main():
    app = wx.App()
    fr = MainFrame(wx.Frame)
    fr.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()
