# -*- mode: python -*-
import wx
from topas4rmc import gui
import ctypes

myappid = 'ornl.topas4rmc.1.0'  # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


# inherit from the MainFrame created in wxFowmBuilder and create Topas2RMC
class Topas2RMC(gui.MainFrame):
    # constructor

    def __init__(self, parent):
        # initialize parent class
        gui.MainFrame.__init__(self, parent)


def main():
    app = wx.App(False)

    # create an object of Topas2RMC
    frame = Topas2RMC(None)
    # show the frame
    frame.Show(True)
    # start the applications
    app.MainLoop()


if __name__ == "__main__":
    main()
