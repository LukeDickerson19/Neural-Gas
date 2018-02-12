''' NOTES:


    TODO:

        copy this code
        strip it down to the bare essential components I need
            GUI display of network that:
                starts with 


    SOURCES:

        pyqtgraph:
        https://github.com/pyqtgraph/pyqtgraph

        Base code aquired from: https://stackoverflow.com/questions/46868432/pyqtgraph-change-color-of-node-and-its-edges-on-click?rq=1
        provides PyQt graph code to display the network
    
            https://stackoverflow.com/questions/46791395/pyqtgraph-get-text-of-node-and-change-color-on-mouseclick
                this link was accessed from the base code
                it might be easier to strip this down

        A Growing Neural Gas Learns Topologies - Original Research Paper
        https://papers.nips.cc/paper/893-a-growing-neural-gas-network-learns-topologies.pdf

    '''


    # -*- coding: utf-8 -*-
"""
Simple example of subclassing GraphItem.
"""

# https://groups.google.com/forum/#!topic/pyqtgraph/pTrem1RCKSw
# https://stackoverflow.com/questions/18867980/pyqtgraph-select-2d-region-of-graph-as-threshold-to-redraw-the-graph
# https://groups.google.com/forum/#!topic/pyqtgraph/pTrem1RCKSw
# https://groups.google.com/forum/#!topic/pyqtgraph/dqw_Lip8rNk

import initExample ## Add path to library (just for examples; you do not need this)

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.Point import Point
import numpy as np


def MultiSelect(newLines, mypoint_index_all, mypoint_edges, mypoints_all_edges, allpoints_neighbornodes, symbolBrushs):
    mypoint_neighbornodes = list(set([e for tup in mypoint_edges for e in tup]))
    allpoints_neighbornodes.append(mypoint_neighbornodes)

    for myp_index in mypoint_index_all:
        symbolBrushs[myp_index] = pg.mkBrush(color=(255, 0, 0))
        for allmy_neighbornodes in allpoints_neighbornodes:
            for all_node in allmy_neighbornodes:
                symbolBrushs[all_node] = pg.mkBrush(color=(255, 0, 0))
            for myp_eges in mypoints_all_edges:
                for i in range(len(myp_eges)):
                    for j in range(len(adj)):
                        if np.array_equal(adj[j], myp_eges[i]):
                            break
                    index = j
                    newLines.itemset(index, (255, 0, 0, 255, 1))

    return newLines, symbolBrushs


class MyViewBox(pg.ViewBox):
    def mouseDragEvent(self, ev):
        if ev.button() == QtCore.Qt.RightButton:
            ev.ignore()
        else:
            pg.ViewBox.mouseDragEvent(self, ev)

        ev.accept()
        pos = ev.pos()
        self.dragPoint = None
        if ev.button() == QtCore.Qt.RightButton:
            if ev.isFinish():
                self.rbScaleBox.hide()
                self.ax = QtCore.QRectF(Point(ev.buttonDownPos(ev.button())), Point(pos))
                self.ax = self.childGroup.mapRectFromParent(self.ax)
                self.Coords =  self.ax.getCoords()
                self.getPointsInRect()
            else:
                self.updateScaleBox(ev.buttonDownPos(), ev.pos())

    def getPointsInRect(self):
        # Get the data from the Graphicsitem that are within scaleBox rectangle
        data = viewbx.allChildren()[2].data.tolist()
        rectangle_coordinates = self.Coords
        graph_nodes_x_coords = viewbx.allChildren()[2].getData()[0]
        graph_nodes_y_coords = viewbx.allChildren()[2].getData()[1]
        graph_nodes = zip(graph_nodes_x_coords, graph_nodes_y_coords)

        rect_x1 = rectangle_coordinates[0]
        rect_y1 = rectangle_coordinates[1]
        rect_x2 = rectangle_coordinates[2]
        rect_y2 = rectangle_coordinates[3]

        points_in_rect_list = []
        for tup in graph_nodes:
            point_x = tup[0]
            point_y = tup[1]
            if rect_x1 <= point_x <= rect_x2 and rect_y1 <= point_y <= rect_y2:
                points_in_rect_list.append(tup)

        self.changePointsColors(points_in_rect_list, data, graph_nodes_x_coords, graph_nodes_y_coords)

    def changePointsColors(self, pointslist, data, graph_nodes_x_coords, graph_nodes_y_coords):
        data_x = [tup[0] for tup in pointslist]
        data_y = [tup[1] for tup in pointslist]
        newPos = np.vstack([graph_nodes_x_coords, graph_nodes_y_coords]).transpose()
        newLines = lines.copy()
        symbolBrushs = [None] * len(data)

        if QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier:  # check if ctrl key is pressed
            self.symbolBrushs_allpoints_indx = g.symbolBrushs_allpoints_indx
            self.symbolBrushs_allpoints_neighbornodes = g.symbolBrushs_allpoints_neighbornodes
            self.mypoint_edges_allpoints = g.mypoint_edges_allpoints

        else:
            self.symbolBrushs_allpoints_indx = []
            self.symbolBrushs_allpoints_neighbornodes = []
            self.mypoint_edges_allpoints = []

        for x, y in zip(data_x, data_y):
            for tup in data:
                if x == tup[0] and y == tup[1]:
                    mypoint_indx = data.index(tup)
                    mypoint_edges = [tup for tup in g.data['adj'] if mypoint_indx in tup]

                    self.symbolBrushs_allpoints_indx.append(mypoint_indx)
                    self.mypoint_edges_allpoints.append(mypoint_edges)

                    mypoint_neighbornodes = list(set([e for tup in mypoint_edges for e in tup]))
                    self.symbolBrushs_allpoints_neighbornodes.append(mypoint_neighbornodes)

        newLines, symbolBrushs = MultiSelect(newLines=newLines, mypoint_index_all=self.symbolBrushs_allpoints_indx,
                               mypoint_edges=mypoint_edges, mypoints_all_edges=self.mypoint_edges_allpoints,
                               allpoints_neighbornodes=self.symbolBrushs_allpoints_neighbornodes, symbolBrushs=symbolBrushs)

        g.setData(pos=newPos, adj=adj, pen=newLines, size=1, symbol=symbols, pxMode=False, text=texts,
              symbolBrush=symbolBrushs)

        g.updateGraph()


class Graph(pg.GraphItem):
    def __init__(self):
        self.textItems = []
        pg.GraphItem.__init__(self)
        self.scatter.sigClicked.connect(self.clicked)
        self.symbolBrushs_allpoints_indx = []
        self.symbolBrushs_allpoints_neighbornodes = []
        self.mypoint_edges_allpoints = []

    def setData(self, **kwds):
        self.text = kwds.pop('text', [])
        self.data = kwds
        if 'pos' in self.data:
            npts = self.data['pos'].shape[0]
            self.data['data'] = np.empty(npts, dtype=[('index', int)])
            self.data['data']['index'] = np.arange(npts)
        self.setTexts(self.text)
        self.updateGraph()

    def setTexts(self, text):
        for i in self.textItems:
            i.scene().removeItem(i)
        self.textItems = []
        for t in text:
            item = pg.TextItem(t)
            self.textItems.append(item)
            item.setParentItem(self)

    def updateGraph(self):
        pg.GraphItem.setData(self, **self.data)
        for i,item in enumerate(self.textItems):
            item.setPos(*self.data['pos'][i])

    def mouseDragEvent(self, ev):
        ev.accept()
        pos = ev.pos()

        if ev.isStart():
            # We are already one step into the drag.
            # Find the point(s) at the mouse cursor when the button was first
            # pressed:
            pos = ev.buttonDownPos()
            pts = self.scatter.pointsAt(pos)
            if len(pts) == 0:
                ev.ignore()
                return
            self.dragPoint = pts[0]
            ind = pts[0].data()[0]
            self.dragOffset = self.data['pos'][ind] - pos
        if ev.isFinish():
            self.dragPoint = None
            return
        else:
            if self.dragPoint is None:
                ev.ignore()
                return

        ind = self.dragPoint.data()[0]
        self.data['pos'][ind] = ev.pos() + self.dragOffset
        self.updateGraph()
        ev.accept()

    def clicked(self, scatter, pts):
        # print(self)
        data_list = scatter.data.tolist()
        mypoint = [tup for tup in data_list if pts[0] in tup][0]
        mypoint_index = data_list.index(mypoint)
        mypoint_edges = [tup for tup in self.data['adj'] if mypoint_index in tup]
        mypoint_neighbornodes = list(set([e for tup in mypoint_edges for e in tup]))

        data = scatter.getData()
        newPos = np.vstack([data[0], data[1]]).transpose()
        newLines = lines.copy()
        symbolBrushs = [None] * len(data[0])

        if QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier:  # check if ctrl key is pressed
            self.symbolBrushs_allpoints_indx.append(mypoint_index)
            self.mypoint_edges_allpoints.append(mypoint_edges)
            self.mypoint_neighbornodes = list(set([e for tup in mypoint_edges for e in tup]))
            self.symbolBrushs_allpoints_neighbornodes.append(mypoint_neighbornodes)

            newLines, symbolBrushs = MultiSelect(newLines=newLines, mypoint_index_all=self.symbolBrushs_allpoints_indx,
                                     mypoint_edges=mypoint_edges, mypoints_all_edges=self.mypoint_edges_allpoints,
                                     allpoints_neighbornodes=self.symbolBrushs_allpoints_neighbornodes,
                                     symbolBrushs=symbolBrushs)

        else:
            self.symbolBrushs_allpoints_indx = []
            self.symbolBrushs_allpoints_neighbornodes = []
            self.mypoint_edges_allpoints = []

            self.symbolBrushs_allpoints_indx.append(mypoint_index)
            self.mypoint_edges_allpoints.append(mypoint_edges)
            self.mypoint_neighbornodes = list(set([e for tup in mypoint_edges for e in tup]))
            self.symbolBrushs_allpoints_neighbornodes.append(mypoint_neighbornodes)
            print(self.symbolBrushs_allpoints_indx)

            symbolBrushs[mypoint_index] = pg.mkBrush(color=(255, 0, 0))
            for neighbornode in mypoint_neighbornodes:
                symbolBrushs[neighbornode] = pg.mkBrush(color=(255, 0, 0))
            for i in range(len(mypoint_edges)):
                for j in range(len(adj)):
                    if np.array_equal(adj[j], mypoint_edges[i]):
                        break
                index = j
                newLines.itemset(index, (255, 0, 0, 255, 1))

        g.setData(pos=newPos, adj=adj, pen=newLines, size=1, symbol=symbols, pxMode=False, text=texts,
                  symbolBrush=symbolBrushs)

        self.updateGraph()
    def clicked2(self, scatter, pts):
        data_list = scatter.data.tolist()
        mypoint = [tup for tup in data_list if pts[0] in tup][0]
        mypoint_index = data_list.index(mypoint)
        mypoint_edges = [tup for tup in self.data['adj'] if mypoint_index in tup]

        data = scatter.getData()
        newPos = np.vstack([data[0],data[1]]).transpose()
        newLines = lines.copy()
        symbolBrushs = [None] * len(data[0])
        symbolBrushs[mypoint_index] = pg.mkBrush(color=(255, 0, 0))
        for i in range(len(mypoint_edges)):
            for j in range(len(adj)):
                if np.array_equal(adj[j], mypoint_edges[i]):
                    break
            index = j
            newLines.itemset(index, (255,0,0,255,1))
        g.setData(pos=newPos, adj=adj, pen=newLines, size=1, symbol=symbols, pxMode=False, text=texts, symbolBrush=symbolBrushs)

        self.updateGraph()

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)
w = pg.GraphicsWindow()
w.setWindowTitle('pyqtgraph example: CustomGraphItem')
viewbx = MyViewBox()
w.addItem(viewbx)
viewbx.setAspectLocked()

g = Graph()
viewbx.addItem(g)

# Define positions of nodes
pos = np.array([
    [0,0],
    [10,0],
    [0,10],
    [10,10],
    [5,5],
    [15,5]
    ], dtype=float)

# Define the set of connections in the graph
adj = np.array([
    [0,1],
    [1,3],
    [3,2],
    [2,0],
    [1,5],
    [3,5],
    ])

# Define the symbol to use for each node (this is optional)
symbols = ['o','o','o','o','o','o']

# Define the line style for each connection (this is optional)
lines = np.array([
    (255,255,255,255,1),
    (255,255,255,255,2),
    (255,255,255,255,3),
    (255,255,255,255,2),
    (255,255,255,255,1),
    (255,255,255,255,4),
    ], dtype=[('red',np.ubyte),('green',np.ubyte),('blue',np.ubyte),('alpha',np.ubyte),('width',float)])

# Define text to show next to each symbol
texts = ["Point %d" % i for i in range(6)]

# Update the graph
g.setData(pos=pos, adj=adj, pen=lines, size=1, symbol=symbols, pxMode=False, text=texts)


# Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()