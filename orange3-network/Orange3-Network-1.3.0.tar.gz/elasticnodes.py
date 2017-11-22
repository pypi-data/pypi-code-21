
import numpy as np

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QLineF, QPointF, QRectF, Qt
from PyQt4.QtGui import qApp, QBrush, QPen, QPolygonF, QStyle, QColor

from orangecontrib.network._fr_layout import fruchterman_reingold_layout

import pyqtgraph as pg

# Expose OpenGL rendering for large graphs, if available
HAVE_OPENGL = True
try: from PyQt4 import QtOpenGL
except: HAVE_OPENGL = False


class QGraphicsEdge(QtGui.QGraphicsLineItem):
    def __init__(self, source, dest, view=None):
        super().__init__()
        self.setAcceptedMouseButtons(Qt.NoButton)
        self.setFlags(self.ItemIgnoresTransformations |
                      self.ItemIgnoresParentOpacity)
        self.setZValue(1)
        self.setPen(QPen(Qt.darkGray, .5))

        source.addEdge(self)
        dest.addEdge(self)
        self.source = source
        self.dest = dest
        self.__transform = view.transform
        # Add text labels
        label = self.label = QtGui.QGraphicsSimpleTextItem('test', self)
        label.setVisible(False)
        label.setBrush(Qt.gray)
        label.setZValue(2)
        label.setFlags(self.ItemIgnoresParentOpacity |
                       self.ItemIgnoresTransformations)
        view.scene().addItem(label)

        self.adjust()

    def adjust(self):
        line = QLineF(self.mapFromItem(self.source, 0, 0),
                      self.mapFromItem(self.dest, 0, 0))
        self.label.setPos(line.pointAt(.5))
        self.setLine(self.__transform().map(line))


class Edge(QGraphicsEdge):
    def __init__(self, source, dest, view=None):
        super().__init__(source, dest, view)
        self.setSize(.5)

    def setSize(self, size):
        self.setPen(QPen(self.pen().color(), size))

    def setText(self, text):
        if text: self.label.setText(text)
        self.label.setVisible(bool(text))

    def setColor(self, color):
        self.setPen(QPen(QColor(color), self.pen().width()))


class QGraphicsNode(QtGui.QGraphicsEllipseItem):
    """This class is the bare minimum to sustain a connected graph"""
    def __init__(self, rect=QRectF(-5, -5, 10, 10), view=None):
        super().__init__(rect)
        self.setCacheMode(self.DeviceCoordinateCache)
        self.setAcceptHoverEvents(True)
        self.setFlags(self.ItemIsMovable |
                      self.ItemIsSelectable |
                      self.ItemIgnoresTransformations |
                      self.ItemIgnoresParentOpacity |
                      self.ItemSendsGeometryChanges)
        self.setZValue(4)

        self.edges = []
        self._radius = rect.width() / 2
        self.__transform = view.transform
        # Add text labels
        label = self.label = QtGui.QGraphicsSimpleTextItem('test', self)
        #~ label.setVisible(False)
        label.setFlags(self.ItemIgnoresParentOpacity |
                       self.ItemIgnoresTransformations)
        label.setZValue(3)
        view.scene().addItem(label)

    def setPos(self, x, y):
        self.adjust()
        super().setPos(x, y)

    def adjust(self):
        # Adjust label position
        d = 1 / self.__transform().m11() * self._radius
        self.label.setPos(self.pos().x() + d, self.pos().y() + d)

    def addEdge(self, edge):
        self.edges.append(edge)

    def itemChange(self, change, value):
        if change == self.ItemPositionHasChanged:
            self.adjust()
            for edge in self.edges:
                edge.adjust()
        return super().itemChange(change, value)


class Node(QGraphicsNode):
    """
    This class provides an interface for all the bells & whistles of the
    Network Explorer.
    """

    BRUSH_DEFAULT = QBrush(QColor('#669'))

    class Pen:
        DEFAULT = QPen(Qt.black, 0)
        SELECTED = QPen(QColor('#ee0000'), 3)
        HIGHLIGHTED = QPen(QColor('#ff7700'), 3)

    _tooltip = lambda _: ''

    def __init__(self, id, view):
        super().__init__(view=view)
        self.id = id
        self.setBrush(Node.BRUSH_DEFAULT)
        self.setPen(Node.Pen.DEFAULT)

        self._is_highlighted = False

    def setSize(self, size):
        self._radius = radius = size/2
        self.setRect(-radius, -radius, size, size)

    def setText(self, text):
        if text: self.label.setText(text)
        self.label.setVisible(bool(text))

    def setColor(self, color=None):
        self.setBrush(QBrush(QColor(color)) if color else Node.BRUSH_DEFAULT)

    def isHighlighted(self):
        return self._is_highlighted
    def setHighlighted(self, highlight):
        self._is_highlighted = highlight
        if not self.isSelected():
            self.itemChange(self.ItemSelectedChange, False)

    def itemChange(self, change, value):
        if change == self.ItemSelectedChange:
            self.setPen(Node.Pen.SELECTED if value else
                        Node.Pen.HIGHLIGHTED if self._is_highlighted else
                        Node.Pen.DEFAULT)
        return super().itemChange(change, value)

    def paint(self, painter, option, widget):
        option.state &= ~QStyle.State_Selected  # We use a custom selection pen
        super().paint(painter, option, widget)

    def setTooltip(self, callback):
        self._tooltip = callback
    def hoverEnterEvent(self, event):
        self.setToolTip(self._tooltip())
    def hoverLeaveEvent(self, event):
        self.setToolTip('');


class TextWidget(QtGui.QGraphicsWidget):
    def __init__(self, view):
        super().__init__(view)
        #~ self.setCacheMode(self.DeviceCoordinateCache)
        #~ self.setFlags(self.ItemIgnoresTransformations |
                      #~ self.ItemIgnoresParentOpacity)
        #~ self.setZValue(5)
        #~ self.setAcceptHoverEvents(False)

        self.view = view
        self.text = QtGui.QGraphicsTextItem()

    def setText(self, html):
        self.text.setHtml(html)
        #~ super().setText(html)

    def adjust(self):
        #~ d = 1 / self.__transform().m11() * self._radius
        #~ self.label.setPos(self.pos().x() + d, self.pos().y() + d)
        self.setPos(self.view.mapToScene(10, 8))

class GraphView(QtGui.QGraphicsView):

    positionsChanged = QtCore.pyqtSignal(np.ndarray)
    # Emitted when nodes' selected or highlighted state changes
    selectionChanged = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.nodes = []
        self.edges = []
        self._selection = []
        self._clicked_node = None

        scene = QtGui.QGraphicsScene(self)
        scene.setItemIndexMethod(scene.NoIndex)
        #~ scene.setSceneRect(-400, -400, 800, 800)
        #~ scene.setSceneRect(-1, -1, 2, 2)
        self.setScene(scene)
        rect = QRectF(QtGui.QDesktopWidget().geometry())
        #~ self.scene().setSceneRect(rect.x(), rect.y(), 2*rect.width(), 2*rect.height())
        #~ self.setSceneRect(rect.x(), rect.y(), 2*rect.width(), 2*rect.height())

        #~ self.setSceneRect(-50, -50, 100, 100)
        #~ r = self.scene().sceneRect()
        #~ print(r.x())
        #~ print(r.y())
        #~ print(r.width())
        #~ print(r.height())
        self.setCacheMode(self.CacheBackground)
        self.setViewportUpdateMode(self.BoundingRectViewportUpdate)

        self.setTransformationAnchor(self.AnchorUnderMouse)
        self.setResizeAnchor(self.AnchorViewCenter)
        #~ self.setResizeAnchor(self.AnchorUnderMouse)

        #~ self.setDragMode(self.ScrollHandDrag)
        self.setDragMode(self.RubberBandDrag)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        #~ self.setMinimumSize(400, 400)
        #~ self.positionsChanged.connect(self._update_positions, type=Qt.BlockingQueuedConnection)
        self.positionsChanged.connect(self._update_positions)

        self.text = None

    def mousePressEvent(self, event):
        event.ignore()
        if event.button() == Qt.LeftButton:
            self.setDragMode(self.NoDrag)
            self.setDragMode(self.RubberBandDrag)
            if self._is_animating:
                self._is_animating = False
                self.setCursor(Qt.ArrowCursor)
            # Save the current selection and restore it on mouse{Move,Release}
            self._selection = []
            node = self._clicked_node = self.itemAt(event.pos())
            if event.modifiers() & (Qt.ControlModifier | Qt.ShiftModifier):
                self._selection = self.scene().selectedItems()
        # On right mouse button, switch to pan mode
        elif event.button() == Qt.RightButton:
            self.setDragMode(self.ScrollHandDrag)
            # Forge left mouse button event
            event = QtGui.QMouseEvent(event.type(),
                                      event.pos(),
                                      Qt.LeftButton,
                                      event.buttons() | Qt.LeftButton,
                                      event.modifiers())
        super().mousePressEvent(event)
        # Reselect the selection that had just been discarded
        for node in self._selection: node.setSelected(True)
    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if not self._clicked_node:
            for node in self._selection: node.setSelected(True)
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if self.dragMode() == self.RubberBandDrag:
            for node in self._selection: node.setSelected(True)
            self.selectionChanged.emit()
        self.setDragMode(self.NoDrag)
        self.setDragMode(self.RubberBandDrag)



    def getSelected(self):
        return self.scene().selectedItems()
    def getHighlighted(self):
        return [node for node in self.nodes
                if node.isHighlighted() and not node.isSelected()]
    def setHighlighted(self, nodes):
        for node in nodes:
            node.setHighlighted(True)
        self.selectionChanged.emit()

    def clear(self):
        self.scene().clear()
        self.scene().setSceneRect(QRectF())
        self.nodes.clear()
        self.edges.clear()

    def set_graph(self, graph):
        assert not graph or isinstance(graph, nx.Graph)  # TODO
        self.graph = graph
        if not graph:
            self.clear()
            return
        large_graph = graph.number_of_nodes() + graph.number_of_edges() > 4000
        self.setViewport(QtOpenGL.QGLWidget()
                         if large_graph and HAVE_OPENGL else
                         QtGui.QWidget())
        if not large_graph:
            self.setRenderHints(QtGui.QPainter.Antialiasing |
                                QtGui.QPainter.TextAntialiasing)
        self.clear()
        for v in sorted(graph.nodes()):
            self.addNode(Node(v, view=self))
        for u, v in graph.edges():
            self.addEdge(Edge(self.nodes[u], self.nodes[v], view=self))
        #~ self.ensureVisible(self.scene().sceneRect())
        #~ self.centerOn(self.scene().itemsBoundingRect().center())
        self.setText('<b>Yeah</b>, this works!')
        self.centerOn(self.scene().sceneRect().center())
        self.selectionChanged.emit()
        self.relayout()

    def addNode(self, node):
        assert isinstance(node, Node)
        self.nodes.append(node)
        self.scene().addItem(node)
    def addEdge(self, edge):
        assert isinstance(edge, Edge)
        self.edges.append(edge)
        self.scene().addItem(edge)

    def setText(self, text):
        self.text = QtGui.QStaticText(text)
    def drawForeground(self, painter, rect):
        if self.text:
            painter.resetTransform()
            painter.drawStaticText(10, 18, self.text)
        super().drawForeground(painter, rect)
    def scrollContentsBy(self, dx, dy):
        scene = self.scene()
        scene.invalidate(layers=scene.BackgroundLayer)
        super().scrollContentsBy(dx, dy)

    def wheelEvent(self, event):
        if event.orientation() != Qt.Vertical: return
        self.scaleView(2**(event.delta() / 240))
    def scaleView(self, factor):
        magnitude = self.matrix().scale(factor, factor).mapRect(QRectF(0, 0, 1, 1)).width()
        if 0.2 < magnitude < 30:
            self.scale(factor, factor)
        # Reposition nodes' labela and edges, both of which are node-dependend
        # (and nodes just "moved")
        for node in self.nodes: node.adjust()
        for edge in self.edges: edge.adjust()
        #~ self.text.adjust()

    def relayout(self, randomize=True):
        self._is_animating = True
        self.setCursor(Qt.ForbiddenCursor)
        pos = None
        if not randomize:
            pos = [[pos.x(), pos.y()]
                   for pos in (node.pos()
                               for node in self.nodes)]
        fruchterman_reingold_layout(self.graph,
                                    pos=pos,
                                    iterations=50,
                                    callback=self.update_positions)
        self._is_animating = False
        self.setCursor(Qt.ArrowCursor)

    def update_positions(self, positions):
        self.positionsChanged.emit(positions)
        return self._is_animating
    def _update_positions(self, positions):
        positions = positions*300
        MARGIN = 500
        (x, y), (w, h) = np.min(positions, 0) - MARGIN, np.ptp(positions, 0) + 2*MARGIN
        self.scene().setSceneRect(x, y, w, h)
        for node, pos in zip(self.nodes, positions):
            node.setPos(*pos)
        qApp.processEvents()

    def drawBackground(self, painter, rect):
        # TODO: delete
        painter.setPen(QPen(Qt.red, 2))
        painter.setBrush(QBrush('yellow'))
        #~ print(self.scene().sceneRect())
        painter.drawRect(self.scene().sceneRect())

class GVTest(QtGui.QGraphicsView):
    def __init__(self):
        super().__init__()
        scene = QtGui.QGraphicsScene(self)
        scene.setSceneRect(0, 0, 1000, 1000)
        self.setScene(scene)

    def mouseReleaseEvent(self, event):
        print(event)
        self.setDragMode(self.RubberBandDrag)
        super().mouseReleaseEvent(event)

    def test(self):
        QMouseEvent, QEvent = QtGui.QMouseEvent, QtCore.QEvent
        from PyQt4.QtCore import QPoint

        item = self.scene().addRect(200, 200, 100, 100)
        item.setFlag(item.ItemIsMovable)
        item.setFlag(item.ItemIsSelectable)
        item.setSelected(True)

        rect = item.boundingRect()
        print(rect.x(), rect.y())

        self.setDragMode(self.ScrollHandDrag)
        self.centerOn(item.boundingRect().center())
        click = QMouseEvent(QEvent.MouseButtonPress,
                            QPoint(250, 250),
                            Qt.LeftButton,
                            Qt.LeftButton,
                            Qt.NoModifier)
        drag = QMouseEvent(QEvent.MouseMove,
                            QPoint(50, 50),
                            Qt.LeftButton,
                            Qt.LeftButton,
                            Qt.NoModifier)
        release = QMouseEvent(QEvent.MouseButtonRelease,
                              QPoint(50, 50),
                            Qt.LeftButton,
                            Qt.LeftButton,
                            Qt.NoModifier)
        qApp.sendEvent(self.viewport(), click)
        qApp.sendEvent(self.viewport(), drag)
        qApp.sendEvent(self.viewport(), release)

        print(item.pos().x(), item.pos().y())

        #~ self.setDragMode(self.RubberBandDrag)


if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(sys.argv)

    view = GVTest()
    view.show()
    view.test()
    sys.exit(app.exec_())



    widget = GraphView()
    widget.show()
    import networkx as nx
    G = nx.scale_free_graph(int(sys.argv[1]) if len(sys.argv) > 1 else 100, seed=0)
    #~ G = nx.cycle_graph(int(sys.argv[1]) if len(sys.argv) > 1 else 100)

    #~ widget.relayout()
    widget.set_graph(G)
    print('nodes', len(widget.nodes), 'edges', len(widget.edges))
    #~ from threading import Thread
    #~ Thread(target=fruchterman_reingold_layout, args=(G,), kwargs=dict(iterations=50, callback=widget.update_positions)).start()

    for node in widget.nodes[:10]:
        node.setHighlighted(True)

    sys.exit(app.exec_())
