from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
import math
from Nodes.task_node import pmGNode, lableItem


class Scene():
    def __init__(self):
        self.deleteMode = True
        self.nodes = []
        self.edges = []

        self.scene_w, self.scene_h = 64000, 64000

        self.gScene = pmGScene(self)
        self.gScene.setSceneSize(self.scene_w, self.scene_h)

    def addNode(self, node):
        self.nodes.append(node)

    def addEdge(self, edge):
        self.edges.append(edge)

    def removeNode(self, node):
        self.nodes.remove(node)

    def removeEdge(self, edge):
        self.edges.remove(edge)


class pmGScene(QGraphicsScene):
    def __init__(self, scene, parent=None):
        super(pmGScene, self).__init__(parent)
        self.scene = scene

        self.gSize = 200
        self.gSubdiv = 10
        self._bgColor = QColor("#282828")
        self._bgColor = QColor("#2f2f2f")
        self._lineColor = QColor("#202020")

        self._dotPen = QPen(self._lineColor)
        self._dotPen.setWidth(2)
        self._dotPen.setStyle(Qt.DotLine)

        self._solidPen = QPen(self._lineColor)
        self._solidPen.setWidth(2)

        self.setBackgroundBrush(self._bgColor)

    def setSceneSize(self, w, h):
        self.setSceneRect(-w//2, -h//2, w, h)

    def drawBackground(self, painter, rect):
        super(pmGScene, self).drawBackground(painter, rect)

        _l = int(math.floor(rect.left()))
        _r = int(math.ceil(rect.right()))
        _t = int(math.floor(rect.top()))
        _b = int(math.ceil(rect.bottom()))

        _firstVLine = _l - (_l % (self.gSize/self.gSubdiv))
        _firstHLine = _t - (_t % (self.gSize/self.gSubdiv))

        dotLines, solidLines = [], []
        for x in range(_firstVLine, _r, (self.gSize/self.gSubdiv)):
            if(x%self.gSize!=0): dotLines.append(QLine(x, _t, x, _b))
            else: solidLines.append(QLine(x, _t, x, _b))

        for y in range(_firstHLine, _b, (self.gSize/self.gSubdiv)):
            if(y%self.gSize!=0): dotLines.append(QLine(_l, y, _r, y))
            else: solidLines.append(QLine(_l, y, _r, y))

        painter.setPen(self._dotPen)
        painter.drawLines(dotLines)
        painter.setPen(self._solidPen)
        painter.drawLines(solidLines)
