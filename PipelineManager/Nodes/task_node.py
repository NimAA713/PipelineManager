from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
from socket import socket, left, right, top, bottom
from edge import pmGEdge


class taskNode():
    def __init__(self, scene, title="Undefiend Task", sockets=[]):
        self.scene = scene
        self.title = title

        self.gNode = pmGNode(self)
        self.scene.addNode(self)
        self.scene.gScene.addItem(self.gNode)

        self.connected = []
        self.sockets = []
        for i,item in enumerate(sockets):
            _socket = socket(node=self, index=i, position=item)
            self.sockets.append(_socket)

    @property
    def pos(self):
        return self.gNode.pos()
    def setPos(self, x, y):
        self.gNode.setPos(x, y)

    def getSocketPosition(self, index, position):
        if position in (left, right):
            x = 0 if position is left else self.gNode.width
            y = self.gNode.height/2
        if position in (top, bottom):
            x = self.gNode.width/2
            y = 0 if position is top else self.gNode.height
        return [x, y]

    def updateConnectedEdges(self):
        for socket in self.sockets:
            for edge in socket.edges:
                edge.updatePositions()

    def remove(self):
        for socket in self.sockets:
            for edge in socket.edges:
                edge.remove()
        self.scene.gScene.removeItem(self.gNode)
        self.gNode = None
        self.scene.removeNode(self)


class pmGNode(QGraphicsItem):
    def __init__(self, node, parent=None):
        super(pmGNode, self).__init__(parent)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsFocusable)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setAcceptHoverEvents(True)
        self.node = node

        self.width = 200
        self.height = 100
        self.bevel = 10
        self.titleSize = 35
        self.padding = 4
        self.socketRadius = 9

        self.pen_normal = QPen(QColor("#000"))
        self.pen_normal.setWidth(3)
        self.pen_select = QPen(QColor("#ce7"))
        self.pen_select.setWidth(4)
        self.fillBrush = QBrush(QColor("#aaa"))

        self.titleColor = QColor("#2f2f2f")
        self.titleBgColor = QBrush(QColor("#ccc"))
        self.titleFont = QFont("calibri", 12)

        self.titleItem = lableItem(self)
        self.titleItem.setDefaultTextColor(self.titleColor)
        self.titleItem.setFont(self.titleFont)
        self.titleItem.setTextWidth(self.width - 2*self.padding)
        titleOption = QTextOption(self.titleItem.document().defaultTextOption())
        titleOption.setAlignment(Qt.AlignCenter);
        self.titleItem.document().setDefaultTextOption(titleOption)
        self.titleItem.setX(self.padding)
        self.titleItem.setY((self.titleSize-self.titleItem.boundingRect().height())/2)

        self.title = self.node.title
        self._title = self.title

    def mouseMoveEvent(self, event):
        for item in self.node.scene.gScene.selectedItems():
            if type(item) == pmGNode:
                item.node.updateConnectedEdges()
        super(pmGNode, self).mouseMoveEvent(event)

    def hoverEnterEvent(self, event):
        self.socketVisibility(True)
        super(pmGNode, self).hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.socketVisibility(False)
        super(pmGNode, self).hoverEnterEvent(event)

    @property
    def title(self): return self._title
    @title.setter
    def title(self, value):
        self._title = value
        self.titleItem.setPlainText(self._title)

    def boundingRect(self):
        return QRectF(
            -self.socketRadius,
            -self.socketRadius,
            self.width+self.socketRadius*2,
            self.height+self.socketRadius*2
        ).normalized()

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        titlePath = QPainterPath()
        titlePath.setFillRule(Qt.WindingFill)
        titlePath.addRoundedRect(0, 0, self.width, self.titleSize, self.bevel, self.bevel)
        titlePath.addRect(0, self.titleSize-self.bevel, self.bevel, self.bevel)
        titlePath.addRect(self.width-self.bevel, self.titleSize-self.bevel, self.bevel, self.bevel)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.titleBgColor)
        painter.drawPath(titlePath.simplified())

        fillPath = QPainterPath()
        fillPath.setFillRule(Qt.WindingFill)
        fillPath.addRoundedRect(0, self.titleSize, self.width, self.height - self.titleSize, self.bevel, self.bevel)
        fillPath.addRect(0, self.titleSize, self.bevel, self.bevel)
        fillPath.addRect(self.width - self.bevel, self.titleSize, self.bevel, self.bevel)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.fillBrush)
        painter.drawPath(fillPath.simplified())

        rectStroke = QPainterPath()
        rectStroke.addRoundedRect(0, 0, self.width, self.height, self.bevel, self.bevel)
        painter.setPen(self.pen_normal if not self.isSelected() else self.pen_select)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(rectStroke.simplified())

    def shape(self):
        socketPath = QPainterPath()
        socketPath.setFillRule(Qt.WindingFill)
        socketPath.addEllipse(-self.socketRadius, self.height/2-self.socketRadius, self.socketRadius*2, self.socketRadius*2)
        socketPath.addEllipse(self.width/2-self.socketRadius, -self.socketRadius, self.socketRadius*2, self.socketRadius*2)
        socketPath.addEllipse(self.width-self.socketRadius, self.height/2-self.socketRadius, self.socketRadius*2, self.socketRadius*2)
        socketPath.addEllipse(self.width/2-self.socketRadius, self.height-self.socketRadius, self.socketRadius*2, self.socketRadius*2)
        socketPath.addRoundedRect(0, 0, self.width, self.height, self.bevel, self.bevel)
        return socketPath.simplified()

    def socketVisibility(self, bool):
        for socket in self.node.sockets:
            socket.gSocket.setVisible(bool)
            socket.gSocket.update()

    def __str__(self):
        return self._title


class lableItem(QGraphicsTextItem):
    def __init__(self, parent=None):
        super(lableItem, self).__init__(parent)
        self.parent = parent

    def focusOutEvent(self, event):
        super(lableItem, self).focusOutEvent(event)
        self.parent.node.scene.deleteMode = True
        self.setTextInteractionFlags(Qt.NoTextInteraction)

    def __str__(self):
        return "Lable of " + self.parent.title
