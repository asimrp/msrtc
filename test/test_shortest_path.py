import os

from qgis.core import (
    QgsApplication,
    QgsPointXY,
    QgsVectorLayer
)
from qgis.analysis import (
    QgsGraphAnalyzer,
    QgsGraphBuilder,
    QgsNetworkDistanceStrategy,
    QgsVectorLayerDirector
)

def CreateApp():
    """Boilerplate to create a QGIS standalone application

    """
    if "QGIS_PREFIX_PATH" not in os.environ:
        raise Exception(
            "QGIS_PREFIX_PATH environment variable not set")
    if os.uname().sysname == "Darwin":
        if ("DYLD_INSERT_LIBRARIES" not in os.environ or
            len(os.environ["DYLD_INSERT_LIBRARIES"]) == 0):
            raise Exception("DYLD_INSERT_LIBRARIES not set")
    prefix = os.environ["QGIS_PREFIX_PATH"]
    QgsApplication.setPrefixPath(prefix, True)
    qgsApp = QgsApplication([], True)
    qgsApp.initQgis()
    # Boiler plate to initialize processing algorithms.  Needed
    # only in stand-alone apps, not needed in plugin code.
    from processing.core.Processing import Processing
    Processing.initialize()
    return qgsApp

def ShortestPathExample(linelayer, startPoint, endPoint):
    """Use network analysis API to run dijkstra's algorithm to compute
    shortest path between two points from a line vector layer.

    """
    director = QgsVectorLayerDirector(linelayer,
                                      -1,
                                      '', '', '',
                                      QgsVectorLayerDirector.DirectionBoth)
    strategy = QgsNetworkDistanceStrategy()
    director.addStrategy(strategy)
    builder = QgsGraphBuilder(linelayer.sourceCrs())
    tiedPoints = director.makeGraph(builder, [startPoint, endPoint])
    tStart, tStop = tiedPoints

    graph = builder.graph()
    idxStart = graph.findVertex(tStart)
    idxEnd = graph.findVertex(tStop)

    (tree, costs) = QgsGraphAnalyzer.dijkstra(graph, idxStart, 0)

    if tree[idxEnd] == -1:
        raise Exception('No route!')

    # Total cost
    cost = costs[idxEnd]
    # Add last point
    shortestRoute = [graph.vertex(idxEnd).point()]
    # Iterate the graph
    while idxEnd != idxStart:
        idxEnd = graph.edge(tree[idxEnd]).fromVertex()
        shortestRoute.insert(0, graph.vertex(idxEnd).point())
    return shortestRoute

if __name__ == "__main__":
    app = CreateApp()
    shapefile = os.path.join(os.path.dirname(__file__), "sample_routes.shp")
    routes = QgsVectorLayer(shapefile, "routes", "ogr")
    if not routes.isValid():
        raise Exception("cannot load routes from %s" % shapefile)
    startPoint = QgsPointXY(562436, 2396173)
    endPoint = QgsPointXY(557714, 2360914)
    shortestRoute = ShortestPathExample(routes, startPoint, endPoint)
    print("start:")
    import pdb
    pdb.set_trace()
    for point in shortestRoute:
        print(" --> POINT(%d, %d)" % (point.x(), point.y()))
    print("end.")
