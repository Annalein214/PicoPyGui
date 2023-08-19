from PyQt5 import QtWidgets, QtCore
MyGui=QtWidgets

from code.gui.main import CentralWidget

class ApplicationWindow(MyGui.QMainWindow):
    '''
    this class controls the window itself
    geometry, location, and basic functionality
    also routes settings to other widgets
    tidy up when app is closed: closes all threads once window is closed
    '''
    
    def __init__(self, daq, 
                    log, opts, 
                    settings, graph, hw, hplot
                    ):
        MyGui.QMainWindow.__init__(self)

        # preparations
        self.log  = log # common log
        self.daq = daq
        self.opts=opts # currently not used, but might be useful to get sys.argv here
        self.settings=settings
        self.graph=graph
        self.hw=hw
        self.hplot=hplot
        
        self.windowOutline()
        self.windowAttributes()

        # construct the inner part of the window
        self.main_widget = CentralWidget(self, log, daq, settings, graph, hw, hplot)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.daq.close()
        try: self.hw.close()
        except: self.log.warning("Hardware thread already closed")
        self.log.endLogging() # only adds a print
        self.fileQuit()

    def windowAttributes(self):

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("PicoPyGui")

        self.file_menu = MyGui.QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.help_menu = MyGui.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        #used in centralwidget, not here 
        #self.statusBar().showMessage("Statusbar", 2000) 

    def windowOutline(self):

        # detect window size
        desktop = MyGui.QDesktopWidget()
        screen_size = QtCore.QRectF(desktop.screenGeometry(desktop.primaryScreen()))
        screen_x = screen_size.x() + screen_size.width()
        screen_y = screen_size.y() + screen_size.height()
        self.log.info("Screen with size %i x %i px detected" %(screen_x,screen_y))
        
        # calculate geometry
        self.left_minimum_size=(750,500)
        self.right_width=450
        self.right_tab_width=self.right_width-30 # not smaller than 30
        self.right_tab_minimum_height=700
        self.window_position=(50,50)
        self.window_size=[self.left_minimum_size[0]+self.right_width+50, 
                          max(self.left_minimum_size[1], self.right_tab_minimum_height)+50] # x, y
        self.log.info("Window minimum size is %d x %d px"%tuple(self.window_size))

        # above were minimal requirements. If you like a bigger window, change it here:
        #if self.window_size[1]<screen_y+400: self.window_size[1]+=400
        #if self.window_size[0]<screen_y+100: self.window_size[0]+=100

        # just to be sure, check size again
        if self.window_size[1]>screen_y or self.window_size[0]>screen_x:
            raise RuntimeError("Window is too big for screen!!")

        # make it so
        self.setGeometry(self.window_position[0], self.window_position[1], self.window_size[0], self.window_size[1])

