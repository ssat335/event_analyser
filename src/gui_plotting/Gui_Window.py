""" Standard imports """

"""
    Author: Shameer Sathar
    Description: Provide Gui Interface.
"""

from multiprocessing import Process
# Main GUI support

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, USE_PYSIDE
from pyqtgraph.dockarea import *

from gui_plotting.Gui_FileMenu import GuiFileMenu

class GuiWindow(QtCore.QObject):

    def __init__(self, parent=None):
        """
        Initialise the properties of the GUI. This part of the code sets the docks, sizes
        :return: NULL
        """
        super(GuiWindow, self).__init__(parent)


    def setupUi(self, MainWindow):

        MainWindow.setObjectName("MainWindow")

        # MENUBAR
        self.ui_menubar = GuiFileMenu()