from PyQt4.QtCore import *
from qgis.networkanalysis import *
from qgis.core import *
import processing
from processing.tools.vector import VectorWriter
import psycopg2


point_layer = processing.getObject("/home/anshulgoel031gmailcom/Downloads/sudanshu/projections.shp")
network_layer = processing.getObject("/home/anshulgoel031gmailcom/Downloads/bangaloreStreets.shp")

#creating an empty layer

cLayer = qgis.utils.iface.mapCanvas().currentLayer()
provider = cLayer.dataProvider()
print provider.encoding(),",", provider.fields(),",", provider.crs()
writer = QgsVectorFileWriter( "/home/anshulgoel031gmailcom/Downloads/MTP1v2/sudanshu.shp", provider.encoding(), provider.fields(),QGis.WKBLineString, provider.crs() )
#writer = VectorWriter("/home/anshulgoel031gmailcom/Downloads/MTP1v2/rs_generic_10062019_3.shp", None, [QgsField("order", QVariant.Int)], network_layer.dataProvider().geometryType(), network_layer.crs() )

layer = QgsVectorLayer("/home/anshulgoel031gmailcom/Downloads/MTP1v2/sudanshu.shp","rs10062019", "ogr")

if not layer.isValid():
    print "Layer failed to load!"
#start editing
layer.startEditing()
provider = layer.dataProvider()
#add fields
provider.addAttributes( [ QgsField("AddressFrom",  QVariant.String)] )
provider.addAttributes( [ QgsField("AddressTo",  QVariant.String)] )
layer.commitChanges()

# prepare graph
vl = network_layer
director = QgsLineVectorLayerDirector( vl, -1, '', '', '', 3 )
properter = QgsDistanceArcProperter()
director.addProperter( properter )
crs = vl.crs()
builder = QgsGraphBuilder( crs )

#

#builder = QgsGraphBuilder(layer.crs()) #sudhanshu one
#
#changes may have to be done in builder currently taken of sudhanshu

# prepare points
features = processing.features(point_layer)
point_count = point_layer.featureCount() #total no. of records in my case

points = []

for f in features:
  points.append(f.geometry().asPoint())

tiedPoints = director.makeGraph( builder, points )
graph = builder.graph()

for i in range(0,point_count-1):
    for j in range (i+1,point_count ):
            
    #for i in range(0,5):    
    #    progress.setPercentage(int(100 * i/ point_count))
        
        from_point = points[i]
        to_point = points[j]
    
        from_id = graph.findVertex(from_point)
        to_id = graph.findVertex(to_point)
    
        (tree,cost) = QgsGraphAnalyzer.dijkstra(graph,from_id,0)
    
        if tree[to_id] == -1:
            continue # ignore this point pair
        else:
            # collect all the vertices between the points
            route_points = []
            curPos = to_id 
            while (curPos != from_id):
                route_points.append( graph.vertex( graph.arc( tree[ curPos ] ).inVertex() ).point() )
                curPos = graph.arc( tree[ curPos ] ).outVertex()
     
            route_points.append(from_point)
        
        layer.startEditing()
        provider = layer.dataProvider()
        # add a feature
        fet = QgsFeature()
        fet.setGeometry(QgsGeometry.fromPolyline(route_points))
        import pandas as pd
        df = pd.read_csv('/home/anshulgoel031gmailcom/Downloads/MTP1v2/Sinnar_Bus_routes.csv')
        z= str(point_layer[address][i]) +";;;;;" + str( point_layer[address][j] )
        #z=str((point_layer['address'][i]) + point_layer['address'][j]) ) 
        # point_layer['address'][i] represent from_address 
        # point_layer['address'][j] represent To_address
        fet.setAttributes([z])#instead of i we need to write "address" from shapefile 
        #after editing z values  just replace i with z
        provider.addFeatures([fet])
        layer.commitChanges()
        writer.addFeature(fet)
        
    
iface.addVectorLayer("/home/anshulgoel031gmailcom/Downloads/MTP1v2/sudanshu.shp",  "rs10062019", "ogr")




del writer
