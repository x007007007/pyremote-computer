from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import xmlrpc.client

from PIL import ImageGrab
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGridLayout, QWidget, QCheckBox, QSystemTrayIcon, \
    QSpacerItem, QSizePolicy, QMenu, QAction, QStyle, qApp
from PyQt5.QtCore import QSize, QThread
import pyautogui

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


class RPCThread(QThread):

    def screen_shot(self):
        img = ImageGrab.grab()
        return xmlrpc.client.Binary(img.tobytes()), img.size, img.mode

    def run(self):
        # Create server
        print("start XMLRPC")
        try:
            with SimpleXMLRPCServer(('0.0.0.0', 8889),
                                    requestHandler=RequestHandler, allow_none=True) as server:
                server.register_introspection_functions()
                server.register_function(self.screen_shot, 'screenshot')
                server.register_instance(pyautogui, allow_dotted_names=True)
                self.rpc_server = server
                server.serve_forever()
        except:
            import traceback
            traceback.print_exc()

    def shutdown(self):
        self.rpc_server.shutdown()
        print("stop service")

class MainWindow(QMainWindow):
    """
         Сheckbox and system tray icons.
         Will initialize in the constructor.
    """
    check_box = None
    tray_icon = None

    # Override the class constructor
    def __init__(self):
        # Be sure to call the super class method
        QMainWindow.__init__(self)
        self.setMinimumSize(QSize(480, 80))  # Set sizes
        self.setWindowTitle("remote control")  # Set a title
        central_widget = QWidget(self)  # Create a central widget
        self.setCentralWidget(central_widget)  # Set the central widget
        grid_layout = QGridLayout(self)  # Create a QGridLayout
        central_widget.setLayout(grid_layout)  # Set the layout into the central widget
        grid_layout.addWidget(QLabel("远程控制器", self), 0, 0)

        # Add a checkbox, which will depend on the behavior of the program when the window is closed
        self.message = QLabel('start server')
        grid_layout.addWidget(self.message, 1, 0)
        grid_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding), 2, 0)

        # Init QSystemTrayIcon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))

        '''
            Define and add steps to work with the system tray icon
            show - show window
            hide - hide window
            exit - exit from application
        '''
        show_action = QAction("Show", self)
        quit_action = QAction("Exit", self)
        self.start_action = QAction("Start", self)
        self.stop_action = QAction("Stop", self)
        self.start_action.triggered.connect(self.start_server)
        self.stop_action.triggered.connect(self.stop_server)
        self.stop_action.setDisabled(True)

        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(qApp.quit)
        tray_menu = QMenu()
        tray_menu.addAction(self.start_action)
        tray_menu.addAction(self.stop_action)
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    # Override closeEvent, to intercept the window closing event
    # The window will be closed only if there is no check mark in the check box
    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Tray Program",
            "Application was minimized to Tray",
            QSystemTrayIcon.Information,
            2000
        )


    def start_server(self):
        self.stop_action.setEnabled(True)
        self.start_action.setEnabled(False)
        print('hi')
        self.rpc_server = RPCThread()

        self.rpc_server.start()


    def stop_server(self):
        self.start_action.setEnabled(True)
        self.stop_action.setEnabled(False)
        self.rpc_server.shutdown()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mw = MainWindow()
    # mw.show()
    sys.exit(app.exec())