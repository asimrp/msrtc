from PyQt4.QtCore import *
import processing 
from processing.tools.vector import VectorWriter
from qgis.core import *
from qgis.networkanalysis import *
import psycopg2


#creating an empty layer

cLayer = qgis.utils.iface.mapCanvas().currentLayer()
provider = cLayer.dataProvider()
print provider.encoding(),",", provider.fields(),",", provider.crs()
writer = QgsVectorFileWriter( "E:\\CTARA\\MTP\\shapefiles\\ShahapurFinal31052019\\edge.shp", provider.encoding(), provider.fields(),QGis.WKBLineString, provider.crs() )

layer = QgsVectorLayer("E:\\CTARA\\MTP\\shapefiles\\ShahapurFinal31052019\\edge.shp", "edges", "ogr")
if not layer.isValid():
    print "Layer failed to load!"
#start editing
layer.startEditing()
provider = layer.dataProvider()
#add fields
provider.addAttributes( [ QgsField("edgeid",  QVariant.String)] )
layer.commitChanges()
rs_network = processing.getObject("E:\\CTARA\\MTP\\shapefiles\\ShahapurFinal31052019\\rs_generic_31052019_1.shp")
 
def createGraph(from_point, to_point, e_id):
#    from_point = QgsPoint(fp_long, fp_lat)
#    to_point = QgsPoint(tp_long, tp_lat)
   
    director = QgsLineVectorLayerDirector (rs_network, -1 , '','','', 3)
    director.addProperter(QgsDistanceArcProperter())
    builder = QgsGraphBuilder(layer.crs())
    tied_points = director.makeGraph(builder, [from_point, to_point])
    #understand what this does
    graph = builder.graph()

    #compute the route from from_id to to_id
    from_id = graph.findVertex(tied_points[0])
    to_id = graph.findVertex(tied_points[1])
    (tree,cost)= QgsGraphAnalyzer.dijkstra(graph, from_id, 0)

    #assemble the route
    route_point = []
    curPos = to_id
    while(curPos != from_id):
        in_vertex= graph.arc(tree[curPos]).inVertex()
        route_point.append(graph.vertex(in_vertex).point())
        curPos = graph.arc(tree[curPos]).outVertex()
    route_point.append(from_point)
    #start editing
    layer.startEditing()
    provider = layer.dataProvider()
    # add a feature
    fet = QgsFeature()
    fet.setGeometry(QgsGeometry.fromPolyline(route_point))
    fet.setAttributes([e_id])
    provider.addFeatures([fet])
    layer.commitChanges()


route_points = []
inter_points =[]
final_points = []

# input: vertice shapefile (V set)
# appending vert_id to a list vert_list
vert_layer = QgsVectorLayer("E:\\CTARA\\MTP\\shapefiles\\ShahapurFinal31052019\\v.shp", "v", "ogr")
layer1 = iface.addVectorLayer("E:\\CTARA\\MTP\\shapefiles\\ShahapurFinal31052019\\rs_generic_31052019_1.shp", "rs_via", "ogr")
layer2 = iface.addVectorLayer("E:\\CTARA\\MTP\\shapefiles\\ShahapurFinal31052019\\v_inter_rs.shp", "v_intersect_rs", "ogr")

vert_list = []
for a in vert_layer.getFeatures():
    vert_list.append(a.attribute("vert_id"))
V= [[0 for o in range(len(vert_list))] for p in range(len(vert_list))]

#the following code appends the v_intersect_rs tuple into the list inter_points
for b in layer2.getFeatures():
#    inter_points.append(b.geometry().asPoint())
    inter_points.append(b)

#following connects to the database
try:
    conn = psycopg2.connect("dbname='shahapurBusDepot' user='postgres' host='localhost' password='postgres'")
except:
    print "I am unable to connect to the database"


try:
    #opening a connection 
    cur = conn.cursor()
#the following code populates final_points list by ordered set of points 
    for a in layer1.getFeatures():
        route_points = a.geometry().asPolyline()
        for i in range(len(route_points)):
            for j in range(len(inter_points)):
                if route_points[i] == inter_points[j].geometry().asPoint() and a.attribute("rs_id") == inter_points[j].attribute("rs_id"):
#                print route_points[i] , " ", a.attribute("road_segme")
                    final_points.append(inter_points[j])
        print a.attribute("rs_id")
        for k in range(len(final_points) - 1):
#        print final_points[k].attribute("pointId"), "", final_points[k].attribute("segId")
            if final_points[k].geometry().asPoint() != final_points[k+1].geometry().asPoint():
                print final_points[k].attribute("vert_id"), " ", final_points[k+1].attribute("vert_id"), " " ,final_points[k].attribute("rs_id")
                l = vert_list.index(final_points[k].attribute("vert_id"))
                m=vert_list.index(final_points[k+1].attribute("vert_id"))
                
                if l<m:
                    #populating the rs_e table
                    cur.execute("insert into rs_e (rs_id, edge_id) values (%s, %s)", (final_points[k].attribute("rs_id"),'E'+str(l+1)+'_'+str(m+1)))
                    
                    if V[l][m]==0:
                        V[l][m]= 'E'+str(l+1)+'_'+str(m+1)
                        cur.execute("insert into v1_v2_e(vert1, vert2, edgeId) values (%s, %s, %s)", (final_points[k].attribute("vert_id"), final_points[k+1].attribute("vert_id"),'E'+str(l+1)+'_'+str(m+1) ))
                        print final_points[k].attribute("vert_id"), " ", final_points[k+1].attribute("vert_id"),  " " ,V[l][m]
                        createGraph(final_points[k].geometry().asPoint(), final_points[k+1].geometry().asPoint(), V[l][m] )
                else:
                    #populating the rs_e table
                    cur.execute("insert into rs_e (rs_id, edge_id) values (%s, %s)", (final_points[k].attribute("rs_id"),'E'+str(m+1)+'_'+str(l+1)))
                    
                    if V[m][l] ==0:
                        V[m][l]= 'E'+str(m+1)+'_'+str(l+1)
                        cur.execute("insert into v1_v2_e(vert1, vert2, edgeid) values (%s, %s, %s)", (final_points[k+1].attribute("vert_id"), final_points[k].attribute("vert_id"),'E'+str(m+1)+'_'+str(l+1) ))
                        print final_points[k+1].attribute("vert_id"), " ", final_points[k].attribute("vert_id"),  " " ,V[m][l]
                        createGraph(final_points[k+1].geometry().asPoint(), final_points[k].geometry().asPoint(), V[m][l] )
                        
                
            
        final_points = []
        route_points= []
    
    conn.commit()
    cur.close()
except Exception as e:
    print (e)
#
## Commit changes
layer.commitChanges()
iface.addVectorLayer("E:\\CTARA\\MTP\\shapefiles\\ShahapurFinal31052019\\edge.shp", "edges", "ogr")















   
