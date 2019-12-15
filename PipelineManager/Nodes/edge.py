from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
from math import *

directEdge = 1
polyEdge = 2


class edge:
    def __init__(self, scene, startSocket, endSocket, type=directEdge):
        self.scene = scene
        self.start = startSocket
        self.end = endSocket

        self.start.edges.append(self)
        if self.end is not None:
            self.end.edges.append(self)

        self.gEdge = gEdge_direct(self) if type==directEdge else gEdge_poly(self)
        if type==polyEdge:
            self.start.node.connected.append(self.end.node.gNode)

        self.updatePositions()

        self.scene.gScene.addItem(self.gEdge)
        self.scene.addEdge(self)


    def updatePositions(self):
        _sourcePos = self.start.getSocketPosition()
        _sourcePos[0] += self.start.node.gNode.pos().x()
        _sourcePos[1] += self.start.node.gNode.pos().y()
        self.gEdge.setSource(*_sourcePos)
        if self.end is not None:
            _endPos = self.end.getSocketPosition()
            _endPos[0] += self.end.node.gNode.pos().x()
            _endPos[1] += self.end.node.gNode.pos().y()
            self.gEdge.setDestination(*_endPos)
        else:
            self.gEdge.setDestination(*_sourcePos)
        self.update()

    def update(self):
        self.gEdge.update()

    def removeFromSocket(self):
        if self.start is not None:
            self.start.edges.remove(self)
        if self.end is not None:
            self.start.node.connected.remove(self.end.node.gNode)
            self.end.edges.remove(self)

        self.start = None
        self.end = None

    def remove(self):
        self.removeFromSocket()
        self.scene.gScene.removeItem(self.gEdge)
        self.gEdge = None
        try:
            self.scene.removeEdge(self)
        except ValueError:
            pass

    def __str__(self):
        return "<Edge %s>" % hex(id(self))


class pmGEdge(QGraphicsPathItem):
    def __init__(self, edge, parent=None):
        super(pmGEdge, self).__init__(parent)

        self.setFlag(QGraphicsItem.ItemIsSelectable)

        self.edge = edge
        self._color = QColor("#afafaf")
        self._pen = QPen(self._color)
        self._pen.setWidthF(2.0)
        self._colorSelect = QColor("#afaf00")
        self._penSelec = QPen(self._colorSelect)
        self._penSelec.setWidthF(3.0)

        self.dragPen = QPen(QColor("#50ff50"))
        self.dragPen.setStyle(Qt.DotLine)
        self.dragPen.setWidthF(2.0)

        self.arrowSize = 10
        self.offset = self.arrowSize + 5

        self.points = []
        self.posSource = [0, 0]
        self.posDestination = [200, 200]

    def setSource(self, x, y):
        self.posSource = [x, y]

    def setDestination(self, x, y):
        self.posDestination = [x, y]

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        self.setZValue(-1 if self.isSelected() else -2)
        self.sX, self.sY = self.posSource
        self.dX, self.dY = self.posDestination

        if self.edge.end is None:
            self.setZValue(1)
            self.updatePath()
            painter.setPen(self.dragPen)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(self.path())
        else:
            self.startPos = self.edge.start.position
            self.endPos = self.edge.end.position
            if self.endPos == left: self.dX -= self.arrowSize
            elif self.endPos == top: self.dY -= self.arrowSize
            elif self.endPos == right: self.dX += self.arrowSize
            else: self.dY += self.arrowSize
            self.difX = (self.dX - self.sX)/2
            if self.sX > self.dX: self.difX *= -1
            self.difY = (self.dY - self.sY)/2
            if self.sY > self.dY: self.difY *= -1

            pointA_x, pointA_y = self.updatePath()
            painter.setPen(self._pen if not self.isSelected() else self._penSelec)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(self.path())

            length = sqrt(((pointA_x - self.dX)**2) + ((pointA_y - self.dY)**2))
            angle = atan2(self.dY - pointA_y, self.dX - pointA_x)
            rotation = degrees(atan2(pointA_y - self.dY, self.dX - pointA_x)) + 90
            self.endX, self.endY = (pointA_x + length * cos(angle), pointA_y + length * sin(angle))
            p = ((self.endX + self.arrowSize * sin(radians(rotation)), self.endY + self.arrowSize * cos(radians(rotation))),
                (self.endX + self.arrowSize * sin(radians(rotation-120)), self.endY + self.arrowSize * cos(radians(rotation-120))),
                (self.endX + self.arrowSize * sin(radians(rotation+120)), self.endY + self.arrowSize * cos(radians(rotation+120)))
            )
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(self._color) if not self.isSelected() else QBrush(self._colorSelect))
            head = QPolygon([
                QPoint(p[0][0], p[0][1]),
                QPoint(p[1][0], p[1][1]),
                QPoint(p[2][0], p[2][1])
            ])
            painter.drawPolygon(head)

    def shape(self):
        qp = QPainterPathStroker()
        qp.setWidth(5)
        return qp.createStroke(self.path()).simplified()

    def updatePath(self):
        raise NotImplemented("This Class has to be overriden in a child class")

    def __str__(self):
        return "<gEdge %s>" % hex(id(self))


class gEdge_direct(pmGEdge):
    def updatePath(self):
        dist = (self.dX - self.sX) * 0.5
        if self.sX > self.dX: dist *= -1
        path = QPainterPath(QPointF(self.sX, self.sY))
        _length = sqrt(((self.sX - self.dX)**2) + ((self.sY - self.dY)**2)) - 5
        _angle = atan2(self.dY - self.sY, self.dX - self.sX)
        _endX, _endY = (self.sX + _length * cos(_angle), self.sY + _length * sin(_angle))
        path.lineTo(_endX , _endY)
        self.setPath(path)

left, top, right, bottom = 1, 2, 3, 4


class gEdge_poly(pmGEdge):
    def updatePath(self):
        path = QPainterPath()
        Line = QPolygonF()
        if self.startPos == left:
            if self.endPos == left:
                if self.dX < self.sX:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.dX-self.offset, self.sY),
                        QPointF(self.dX-self.offset, self.dY),
                        QPointF(self.dX, self.dY)
                    ]
                else:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX-self.offset, self.sY),
                        QPointF(self.sX-self.offset, self.dY),
                        QPointF(self.dX, self.dY)
                    ]
            elif self.endPos == top:
                if self.dX <= self.sX-self.offset and self.dY >= self.sY+self.offset:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.dX, self.sY),
                        QPointF(self.dX, self.dY)
                    ]
                elif self.dX < self.sX-self.offset*2 and self.dY < self.sY+self.offset:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX-self.difX, self.sY),
                        QPointF(self.dX+self.difX, self.dY-self.offset),
                        QPointF(self.dX, self.dY-self.offset),
                        QPointF(self.dX, self.dY)
                    ]
                elif self.dX >= self.sX-self.offset*2 and self.dY <= self.sY+self.offset*2:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX-self.offset, self.sY),
                        QPointF(self.sX-self.offset, self.dY-self.offset),
                        QPointF(self.dX, self.dY-self.offset),
                        QPointF(self.dX, self.dY)
                    ]
                else:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX-self.offset, self.sY),
                        QPointF(self.sX-self.offset, self.sY+self.difY),
                        QPointF(self.dX, self.dY-self.difY),
                        QPointF(self.dX, self.dY)
                    ]
            elif self.endPos == right:
                if self.dX < self.sX-self.offset*2:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX-self.difX, self.sY),
                        QPointF(self.dX+self.difX, self.dY),
                        QPointF(self.dX, self.dY)
                    ]
                elif self.dX >= self.sX-self.offset*2 and self.dY < self.sY:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX-self.offset, self.sY),
                        QPointF(self.sX-self.offset, self.sY-self.difY),
                        QPointF(self.dX+self.offset, self.sY-self.difY),
                        QPointF(self.dX+self.offset, self.dY),
                        QPointF(self.dX, self.dY)
                    ]
                else:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX-self.offset, self.sY),
                        QPointF(self.sX-self.offset, self.sY+self.difY),
                        QPointF(self.dX+self.offset, self.sY+self.difY),
                        QPointF(self.dX+self.offset, self.dY),
                        QPointF(self.dX, self.dY)
                    ]
            else:
                if self.dX <= self.sX-self.offset*2 and self.dY >= self.sY-self.offset:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX-self.difX, self.sY),
                        QPointF(self.dX+self.difX, self.dY+self.offset),
                        QPointF(self.dX, self.dY+self.offset),
                        QPointF(self.dX, self.dY)
                    ]
                elif self.dX <= self.sX-self.offset and self.dY < self.sY-self.offset:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.dX, self.sY),
                        QPointF(self.dX, self.dY)
                    ]
                elif self.dX > self.sX-self.offset and self.dY <= self.sY-self.offset*2:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX-self.offset, self.sY),
                        QPointF(self.sX-self.offset, self.sY-self.difY),
                        QPointF(self.dX, self.dY+self.difY),
                        QPointF(self.dX, self.dY)
                    ]
                else:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX-self.offset, self.sY),
                        QPointF(self.sX-self.offset, self.dY+self.offset),
                        QPointF(self.dX, self.dY+self.offset),
                        QPointF(self.dX, self.dY)
                    ]
        elif self.startPos == top:
            if self.endPos == left:
                if self.dX <= self.sX+self.offset*2 and self.dY >= self.sY-self.offset*2:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX, self.sY-self.offset),
                        QPointF(self.dX-self.offset, self.sY-self.offset),
                        QPointF(self.dX-self.offset, self.dY),
                        QPointF(self.dX, self.dY)
                    ]
                elif self.dX <= self.sX+self.offset and self.dY < self.sY-self.offset*2:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX, self.sY-self.difY),
                        QPointF(self.dX-self.offset, self.dY+self.difY),
                        QPointF(self.dX-self.offset, self.dY),
                        QPointF(self.dX, self.dY)
                    ]
                elif self.dX > self.sX-self.offset and self.dY <= self.sY-self.offset:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX, self.dY),
                        QPointF(self.dX, self.dY)
                    ]
                else:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX, self.sY-self.offset),
                        QPointF(self.sX+self.difX, self.sY-self.offset),
                        QPointF(self.dX-self.difX, self.dY),
                        QPointF(self.dX, self.dY)
                    ]
            elif self.endPos == top:
                if self.dY > self.sY:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX, self.sY-self.offset),
                        QPointF(self.dX, self.sY-self.offset),
                        QPointF(self.dX, self.dY)
                    ]
                else:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX, self.dY-self.offset),
                        QPointF(self.dX, self.dY-self.offset),
                        QPointF(self.dX, self.dY)
                    ]
            elif self.endPos == right:
                if self.dX <= self.sX-self.offset*2 and self.dY >= self.sY-self.offset:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX, self.sY-self.offset),
                        QPointF(self.sX-self.difX, self.sY-self.offset),
                        QPointF(self.dX+self.difX, self.dY),
                        QPointF(self.dX, self.dY)
                    ]
                elif self.dX < self.sX-self.offset and self.dY < self.sY+self.offset:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX, self.dY),
                        QPointF(self.dX, self.dY)
                    ]
                elif self.dX >= self.sX-self.offset*2 and self.dY <= self.sY-self.offset*2:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX, self.sY-self.difY),
                        QPointF(self.dX+self.offset, self.sY-self.difY),
                        QPointF(self.dX+self.offset, self.dY),
                        QPointF(self.dX, self.dY)
                    ]
                else:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX, self.sY-self.offset),
                        QPointF(self.dX+self.offset, self.sY-self.offset),
                        QPointF(self.dX+self.offset, self.dY),
                        QPointF(self.dX, self.dY)
                    ]
            else:
                if self.sY <= self.dY+self.offset*2 and self.dX < self.sX:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX, self.sY-self.offset),
                        QPointF(self.sX-self.difX, self.sY-self.offset),
                        QPointF(self.dX+self.difX, self.dY+self.offset),
                        QPointF(self.dX, self.dY+self.offset),
                        QPointF(self.dX, self.dY)
                    ]
                elif self.sY > self.dY+self.offset*2:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX, self.sY-self.difY),
                        QPointF(self.dX, self.dY+self.difY),
                        QPointF(self.dX, self.dY)
                    ]
                else:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX, self.sY-self.offset),
                        QPointF(self.sX+self.difX, self.sY-self.offset),
                        QPointF(self.dX-self.difX, self.dY+self.offset),
                        QPointF(self.dX, self.dY+self.offset),
                        QPointF(self.dX, self.dY)
                    ]
        elif self.startPos == right:
            if self.endPos == left:
                if self.dX <= self.sX+self.offset*2 and self.dY > self.sY:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX+self.offset, self.sY),
                        QPointF(self.sX+self.offset, self.sY+self.difY),
                        QPointF(self.dX-self.offset, self.sY+self.difY),
                        QPointF(self.dX-self.offset, self.dY),
                        QPointF(self.dX, self.dY)
                    ]
                elif self.dX < self.sX+self.offset*2:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX+self.offset, self.sY),
                        QPointF(self.sX+self.offset, self.sY-self.difY),
                        QPointF(self.dX-self.offset, self.sY-self.difY),
                        QPointF(self.dX-self.offset, self.dY),
                        QPointF(self.dX, self.dY)
                    ]
                else:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX+self.difX, self.sY),
                        QPointF(self.dX-self.difX, self.dY),
                        QPointF(self.dX, self.dY)
                    ]
            elif self.endPos == top:
                if self.dX <= self.sX+self.offset and self.dY >= self.sY+self.offset*2:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX+self.offset, self.sY),
                        QPointF(self.sX+self.offset, self.sY+self.difY),
                        QPointF(self.dX, self.dY-self.difY),
                        QPointF(self.dX, self.dY)
                    ]
                elif self.dX < self.sX+self.offset*2 and self.dY < self.sY+self.offset*2:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX+self.offset, self.sY),
                        QPointF(self.sX+self.offset, self.dY-self.offset),
                        QPointF(self.dX, self.dY-self.offset),
                        QPointF(self.dX, self.dY)
                    ]
                elif self.dX >= self.sX+self.offset*2 and self.dY <= self.sY+self.offset:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX+self.difX, self.sY),
                        QPointF(self.dX-self.difX, self.dY-self.offset),
                        QPointF(self.dX, self.dY-self.offset),
                        QPointF(self.dX, self.dY)
                    ]
                else:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.dX, self.sY),
                        QPointF(self.dX, self.dY)
                    ]
            elif self.endPos == right:
                if self.dX < self.sX:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX+self.offset, self.sY),
                        QPointF(self.sX+self.offset, self.dY),
                        QPointF(self.dX, self.dY)
                    ]
                else:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.dX+self.offset, self.sY),
                        QPointF(self.dX+self.offset, self.dY),
                        QPointF(self.dX, self.dY)
                    ]
            else:
                if self.dX <= self.sX+self.offset*2 and self.dY >= self.sY-self.offset*2:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX+self.offset, self.sY),
                        QPointF(self.sX+self.offset, self.dY+self.offset),
                        QPointF(self.dX, self.dY+self.offset),
                        QPointF(self.dX, self.dY)
                    ]
                elif self.dX < self.sX+self.offset and self.dY < self.sY-self.offset*2:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX+self.offset, self.sY),
                        QPointF(self.sX+self.offset, self.sY-self.difY),
                        QPointF(self.dX, self.dY+self.difY),
                        QPointF(self.dX, self.dY)
                    ]
                elif self.dX >= self.sX+self.offset and self.dY <= self.sY-self.offset:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.dX, self.sY),
                        QPointF(self.dX, self.dY)
                    ]
                else:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX+self.difX, self.sY),
                        QPointF(self.dX-self.difX, self.dY+self.offset),
                        QPointF(self.dX, self.dY+self.offset),
                        QPointF(self.dX, self.dY)
                    ]
        elif self.startPos == bottom:
            if self.endPos == left:
                if self.dX <= self.sX+self.offset and self.dY >= self.sY+self.offset*2:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX, self.sY+self.difY),
                        QPointF(self.dX-self.offset, self.dY-self.difY),
                        QPointF(self.dX-self.offset, self.dY),
                        QPointF(self.dX, self.dY)
                    ]
                elif self.dX < self.sX+self.offset*2 and self.dY < self.sY+self.offset*2:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX, self.sY+self.offset),
                        QPointF(self.dX-self.offset, self.sY+self.offset),
                        QPointF(self.dX-self.offset, self.dY),
                        QPointF(self.dX, self.dY)
                    ]
                elif self.dX >= self.sX+self.offset*2 and self.dY <= self.sY+self.offset:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX, self.sY+self.offset),
                        QPointF(self.sX+self.difX, self.sY+self.offset),
                        QPointF(self.dX-self.difX, self.dY),
                        QPointF(self.dX, self.dY)
                    ]
                else:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX, self.dY),
                        QPointF(self.dX, self.dY)
                    ]
            elif self.endPos == top:
                if self.sY < self.dY-self.offset*2:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX, self.sY+self.difY),
                        QPointF(self.dX, self.dY-self.difY),
                        QPointF(self.dX, self.dY)
                    ]
                elif self.dX < self.sX and self.dY <= self.sY+self.offset*2:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX, self.sY+self.offset),
                        QPointF(self.sX-self.difX, self.sY+self.offset),
                        QPointF(self.dX+self.difX, self.dY-self.offset),
                        QPointF(self.dX, self.dY-self.offset),
                        QPointF(self.dX, self.dY)
                    ]
                else:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX, self.sY+self.offset),
                        QPointF(self.sX+self.difX, self.sY+self.offset),
                        QPointF(self.dX-self.difX, self.dY-self.offset),
                        QPointF(self.dX, self.dY-self.offset),
                        QPointF(self.dX, self.dY)
                    ]
            elif self.endPos == right:
                if self.dX <= self.sX-self.offset and self.dY >= self.sY+self.offset:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX, self.dY),
                        QPointF(self.dX, self.dY)
                    ]
                elif self.dX < self.sX-self.offset*2 and self.dY < self.sY+self.offset:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX, self.sY+self.offset),
                        QPointF(self.sX-self.difX, self.sY+self.offset),
                        QPointF(self.dX+self.difX, self.dY),
                        QPointF(self.dX, self.dY)
                    ]
                elif self.dX >= self.sX-self.offset*2 and self.dY <= self.sY+self.offset*2:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX, self.sY+self.offset),
                        QPointF(self.dX+self.offset, self.sY+self.offset),
                        QPointF(self.dX+self.offset, self.dY),
                        QPointF(self.dX, self.dY)
                    ]
                else:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX, self.sY+self.difY),
                        QPointF(self.dX+self.offset, self.dY-self.difY),
                        QPointF(self.dX+self.offset, self.dY),
                        QPointF(self.dX, self.dY)
                    ]
            else:
                if self.dY > self.sY:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX, self.dY+self.offset),
                        QPointF(self.dX, self.dY+self.offset),
                        QPointF(self.dX, self.dY)
                    ]
                else:
                    self.points = [
                        QPointF(self.sX, self.sY),
                        QPointF(self.sX, self.sY+self.offset),
                        QPointF(self.dX, self.sY+self.offset),
                        QPointF(self.dX, self.dY)
                    ]
        Line.append(self.points)
        path.addPolygon(Line)
        self.setPath(path)
        return map(float, str(self.points[-2]).split("(")[1].split(")")[0].split(","))


class gEdge_cut(QGraphicsPathItem):
    def __init__(self, scene, start, end, parent=None):
        self.scene = scene
        self.start = start
        self.end = end if end is not None else start
        super(gEdge_cut, self).__init__(parent)

        self.pen = QPen(QColor("#dfdf00"), 4)
        self.pen.setCapStyle(Qt.RoundCap)

        self.scene.gScene.addItem(self)

    def setEndPos(self, pos):
        self.end = pos

    def remove(self):
        self.scene.gScene.removeItem(self)

    def updatePath(self):
        path = QPainterPath(QPointF(self.start.x(), self.start.y()))
        path.lineTo(self.end.x(), self.end.y())
        self.setPath(path)

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        self.updatePath()
        painter.setPen(self.pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self.path())
