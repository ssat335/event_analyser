"""
    Author: Shameer Sathar
    Description: A module of processing the training data.
"""
import sys
sys.path.append('..')


from pyqtgraph.Qt import QtGui

class GuiFileMenu(QtGui.QMenuBar):

    def __init__(self, parent=None):
        '''
        Initialise dock window properties
        '''
        super(GuiFileMenu, self).__init__(parent)
        self.ui_menubar = QtGui.QMenuBar()
        self.menu = self.ui_menubar.addMenu('&File')
        self.add_menu_contents()



    def add_menu_contents(self):
        ## Exit 
        self.quitAction = QtGui.QAction('Close', self)
        self.quitAction.setStatusTip('Quit the program')
        self.quitAction.setShortcut('Ctrl+Q')

        self.menu.addAction(self.quitAction)
