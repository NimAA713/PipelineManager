from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

left, top, right, bottom = 1, 2, 3, 4


class socket():
    def __init__(self, node, index=0, position=left):
        self.node = node
        self.index = index
        self.position = position

        self.gSocket = pmGSocket(self)
        _x, _y = self.getSocketPosition()
        self.gSocket.setPos(_x, _y)

        self.edges = []

    def getSocketPosition(self):
        return self.node.getSocketPosition(self.index, self.position)

    def setConnectedEdge(self, edge=None):
        if edge not in self.edges:
            self.edges.append(edge)


class pmGSocket(QGraphicsItem):
    def __init__(self, socket):
        super(pmGSocket, self).__init__(socket.node.gNode)
        self.socket = socket
        self.gNode = self.socket.node.gNode
        self.setVisible(False)

        self.hover = False
        self.radius = 7
        self.stroke = 2

        self.fill_normal = QColor("#909090")
        self._brush = QBrush(self.fill_normal)
        self.fill_hover = QColor("#fff")
        self._brush_hover = QBrush(self.fill_hover)
        self.fill_connected = QColor("#5a3")
        self._brush_connected = QBrush(self.fill_connected)

        self.stroke_normal = QColor("#000")
        self._pen = QPen(self.stroke_normal)
        self._pen.setWidthF(self.stroke)
        self.stroke_selected = QColor("#ce7")
        self._pen_selected = QPen(self.stroke_selected)
        self._pen_selected.setWidthF(self.stroke)

    def hoverEnterEvent(self, event):
        super(pmGSocket, self).hoverEnterEvent(event)
        self.hover = True
        print "hover in"

    def hoverLeaveEvent(self, event):
        super(pmGSocket, self).hoverEnterEvent(event)
        self.hover = False

    def boundingRect(self):
        return QRectF(
            -self.radius - self.stroke,
            -self.radius - self.stroke,
            2*(self.radius + self.stroke),
            2*(self.radius + self.stroke)
        ).normalized()

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        if self.hover:
            painter.setBrush(self._brush_hover)
        else:
            painter.setBrush(self._brush_connected if self.socket.edges else self._brush)
        painter.setPen(self._pen_selected if self.gNode.isSelected() else self._pen)
        painter.drawEllipse(-self.radius, -self.radius, 2*self.radius, 2*self.radius)
