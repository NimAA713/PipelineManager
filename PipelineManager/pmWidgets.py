from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
from pmScene import Scene
from pmGraphicsView import pmGView
from Nodes.task_node import taskNode
from Nodes.edge import edge

### ============================================ ###


class pmUI(QWidget):
    def __init__(self, parent=None):
        super(pmUI, self).__init__(parent)
        self.setMouseTracking(True)

        self.ssFile = "qss/nodesStyle.qss"
        self.loadStylesheet(self.ssFile)

        self.initUI()

    def initUI(self):

        self.setGeometry(0, 50, 1200, 1000)
        self.Layout = QVBoxLayout()
        self.Layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.Layout)

        self.scene = Scene()
        self.gScene = self.scene.gScene

        self.addNodes()

        self.view = pmGView(self.gScene, self)

        self.layout().addWidget(self.view)

        self.setWindowTitle("Pipeline Manager")
        self.show()

    def addNodes(self):
        task_node1 = taskNode(self.scene, sockets=[1, 2, 3, 4])
        task_node1.setPos(-400, 150)
        task_node1.gNode.title = "Project Task 1"
        task_node2 = taskNode(self.scene, "Project Task 2", sockets=[1, 2, 3, 4])
        task_node2.setPos(-100, -400)
        task_node3 = taskNode(self.scene, "Project Task 3", sockets=[1, 2, 3, 4])
        task_node3.setPos(200, -100)

    def loadStylesheet(self, qss):
        file = QFile(qss)
        file.open(QFile.ReadOnly | QFile.Text)
        style = file.readAll()
        QApplication.instance().setStyleSheet(str(style).encode("utf-8"))
