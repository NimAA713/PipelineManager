from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
import warnings
from Nodes.task_node import pmGNode, lableItem
from Nodes.socket import pmGSocket
from Nodes.edge import *

defaultMode = 1
connectMode = 2
cutMode = 3

dragThreshold = 10


class pmGView(QGraphicsView):
    def __init__(self, gScene, parent=None):
        super(pmGView, self).__init__(gScene, parent)

        self.gScene = gScene
        self.initUI()
        self.setScene(self.gScene)

        self.mode = defaultMode

        self.zoom = 6
        self.zoomStep = 1
        self.zoomInFactor = 1.3
        self.zoomRange = [1, 9]
        self.zoomClamp = True
        self.zoomMode = True

    def initUI(self):
        self.setRenderHints(QPainter.Antialiasing | QPainter.HighQualityAntialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.RubberBandDrag)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonPress(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonPress(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonPress(event)
        else:
            super(pmGView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonRelease(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonRelease(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonRelease(event)
        else:
            super(pmGView, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        endPos = self.mapToScene(event.pos())
        if self.mode == connectMode:
            self.dragEdge.gEdge.setDestination(endPos.x(), endPos.y())
            self.dragEdge.gEdge.update()
        if self.mode == cutMode:
            self.cutEdge.setEndPos(endPos)
            self.cutEdge.update()
        super(pmGView, self).mouseMoveEvent(event)

    def middleMouseButtonPress(self, event):
        releaseEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                Qt.LeftButton, Qt.NoButton, event.modifiers())
        super(pmGView, self).mouseReleaseEvent(releaseEvent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setInteractive(False)
        eventProxy = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers())
        super(pmGView, self).mousePressEvent(eventProxy)

    def middleMouseButtonRelease(self, event):
        eventProxy = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                Qt.LeftButton, event.buttons() & Qt.LeftButton, event.modifiers())
        super(pmGView, self).mouseReleaseEvent(eventProxy)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setInteractive(True)

    def leftMouseButtonPress(self, event):
        item = self.getItemAtClick(event)

        self.lastMousePos = self.mapToScene(event.pos())
        if type(item) is pmGSocket and self.mode == defaultMode:
            self.mode = connectMode
            self.dragEdge_start(item)
            return
        if self.mode == connectMode:
            result = self.dragEdge_end(item)
            if result: return

        if item is None and self.mode == defaultMode:
            if event.modifiers() & Qt.AltModifier and event.modifiers() & Qt.ShiftModifier:
                startPos = self.mapToScene(event.pos())
                self.mode = cutMode
                self.cutEdge_start(startPos)
                fakeEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                        Qt.LeftButton, Qt.NoButton, event.modifiers())
                super(pmGView, self).mouseReleaseEvent(fakeEvent)
                return

        super(pmGView, self).mousePressEvent(event)

    def leftMouseButtonRelease(self, event):
        item = self.getItemAtClick(event)

        if self.mode == connectMode:
            if self.dist_ClickRelease_off(event):
                result = self.dragEdge_end(item)
                if result: return

        if self.mode == cutMode:
            self.cutEdge_end()
            return

        super(pmGView, self).mouseReleaseEvent(event)

    def rightMouseButtonPress(self, event):
        item = self.getItemAtClick(event)
        if isinstance(item, pmGEdge): print item.edge, "  conecting socket:  ", item.edge.start, "<--->", item.edge.end
        if isinstance(item, pmGSocket): print item.socket.edges
        if item is None:
            for edge in self.gScene.scene.edges:
                print edge
        super(pmGView, self).mousePressEvent(event)

    def rightMouseButtonRelease(self, event):
        super(pmGView, self).mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            item = self.getItemAtClick(event)
            if type(item) in (lableItem, pmGNode):
                self.gScene.scene.deleteMode = False
                self.lable = item if type(item) == lableItem else item.titleItem
                self.lable.setTextInteractionFlags(Qt.TextEditable)
        super(pmGView, self).mouseDoubleClickEvent(event)

    def keyPressEvent(self, event):
        if  event.key() == Qt.Key_Delete and self.gScene.scene.deleteMode:
            for item in self.gScene.selectedItems():
                if isinstance(item, pmGEdge):
                    item.edge.remove()
                elif hasattr(item, "node"):
                    item.node.remove()
        else:
            super(pmGView, self).keyPressEvent(event)

    def wheelEvent(self, event):
        zoomOutFactor = 1/self.zoomInFactor

        if event.angleDelta().y()>0:
            zoomFactor = self.zoomInFactor
            self.zoom += self.zoomStep
        else:
            zoomFactor = zoomOutFactor
            self.zoom -= self.zoomStep

        clamped = False
        if self.zoom<self.zoomRange[0]: self.zoom, clamped = self.zoomRange[0], True
        if self.zoom>self.zoomRange[1]: self.zoom, clamped = self.zoomRange[1], True

        if not clamped or self.zoomClamp is False:
            if self.zoomMode:
                self.scale(zoomFactor, zoomFactor)

    def getItemAtClick(self, event):
        return self.itemAt(event.pos())

    def dist_ClickRelease_off(self, event):
        self.newMousePos = self.mapToScene(event.pos())
        mouseDist = self.newMousePos - self.lastMousePos
        return (mouseDist.x()**2 + mouseDist.y()**2) > dragThreshold**2

    def dragEdge_start(self, item):
        self.startSocket = item.socket
        self.dragEdge = edge(self.gScene.scene, self.startSocket, None, type=1)

    def dragEdge_end(self, item):
        self.mode = defaultMode
        if type(item) is pmGSocket:
            self.endSocket = item.socket
            if self.endSocket.node.gNode not in self.startSocket.node.connected:
                if self.endSocket.node is not self.startSocket.node:
                    _newEdge = edge(self.gScene.scene, self.startSocket, self.endSocket, type=2)
                    _newEdge.update()
                    self.dragEdge.remove()
                    self.dragEdge = None
                    return True
            else:
                warnings.warn("Already connected to this Node!", Warning)
        self.dragEdge.remove()
        self.dragEdge = None
        return False

    def cutEdge_start(self, pos):
        self.startPos = pos
        self.cutEdge = gEdge_cut(self.gScene.scene, self.startPos, None,)

    def cutEdge_end(self):
        _edgeList = [edge for edge in self.gScene.scene.edges if edge.gEdge.shape().intersects(self.cutEdge.path())]
        for edge in _edgeList:
            edge.remove()
        self.mode = defaultMode
        self.cutEdge.remove()
        self.cutEdge = None
