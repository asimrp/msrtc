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
writer = QgsVectorFileWriter( "E:\\CTARA\\MTP\\shapefiles\\testFolder20022019\\rs_generic_10062019_3.shp", provider.encoding(), provider.fields(),QGis.WKBLineString, provider.crs() )

layer = QgsVectorLayer("E:\\CTARA\\MTP\\shapefiles\\testFolder20022019\\rs_generic_10062019_3.shp", "rs10062019", "ogr")
if not layer.isValid():
    print "Layer failed to load!"
#start editing
layer.startEditing()
provider = layer.dataProvider()
#add fields
provider.addAttributes( [ QgsField("rs_id",  QVariant.String)] )
layer.commitChanges()
road_network = processing.getObject("E:\\CTARA\\MTP\\shapefiles\\communityGIS\\roads_merged_07042019.shp")
 
def create_rs(fp_long, fp_lat, tp_long, tp_lat, rs_id):
    from_point = QgsPoint(fp_long, fp_lat)
    to_point = QgsPoint(tp_long, tp_lat)
   
    director = QgsLineVectorLayerDirector (road_network, -1 , '','','', 3)
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
    route_points = []
    curPos = to_id
    while(curPos != from_id):
        in_vertex= graph.arc(tree[curPos]).inVertex()
        route_points.append(graph.vertex(in_vertex).point())
        curPos = graph.arc(tree[curPos]).outVertex()
    route_points.append(from_point)
    #print route_points
    #start editing
    layer.startEditing()
    provider = layer.dataProvider()
    # add a feature
    fet = QgsFeature()
    fet.setGeometry(QgsGeometry.fromPolyline(route_points))
    fet.setAttributes([rs_id])
    provider.addFeatures([fet])
    layer.commitChanges()

try:
    def create_rs_via(fp_long, fp_lat,vp_long, vp_lat, tp_long, tp_lat, rs_id):
        from_point = QgsPoint(fp_long, fp_lat)
        via_point = QgsPoint(vp_long, vp_lat)
        to_point = QgsPoint(tp_long, tp_lat)
   
        director = QgsLineVectorLayerDirector (road_network, -1 , '','','', 3)
        director.addProperter(QgsDistanceArcProperter())
        builder = QgsGraphBuilder(layer.crs())
        tied_points = director.makeGraph(builder, [from_point, via_point, to_point])
    #understand what this does
        graph = builder.graph()

    #compute the route from from_id to to_id
        from_id = graph.findVertex(tied_points[0])
        via_id = graph.findVertex(tied_points[1])
        (tree,cost)= QgsGraphAnalyzer.dijkstra(graph, via_id, 0)

    #assemble the route
        route_points = []
        curPos = from_id
        while(curPos != via_id):
            in_vertex= graph.arc(tree[curPos]).inVertex()        
            route_points.append(graph.vertex(in_vertex).point())
            curPos = graph.arc(tree[curPos]).outVertex()
        route_points.append(via_point)
       # print route_points

    #compute the route from from_id to to_id
        via_id = graph.findVertex(tied_points[1])
        to_id = graph.findVertex(tied_points[2])
        (tree,cost)= QgsGraphAnalyzer.dijkstra(graph, to_id, 0)
        
    #assemble the route
        curPos = via_id
        while(curPos != to_id):
            in_vertex= graph.arc(tree[curPos]).inVertex()
            route_points.append(graph.vertex(in_vertex).point())
            curPos = graph.arc(tree[curPos]).outVertex()
        route_points.append(to_point)
    
    
    
    #start editing
        layer.startEditing()
        provider = layer.dataProvider()
    # add a feature
        fet = QgsFeature()
        fet.setGeometry(QgsGeometry.fromPolyline(route_points))
        fet.setAttributes([rs_id])
        provider.addFeatures([fet])
        layer.commitChanges()
except Exception as e:
    print (e)

#####################################################################################################################################################
layer1 = QgsVectorLayer("E:\\CTARA\\MTP\\shapefiles\\ShahapurFinal31052019\\t_31052019.shp", "termini_list", "ogr")
termini_list = []

for a in layer1.getFeatures():
    termini_list.append(a.attribute("name"))
T= [[0 for i in range(len(termini_list))] for j in range(len(termini_list))]
#for i in range(len(termini_list)):
#    print termini_list[i]

try:
    conn = psycopg2.connect("dbname='shahapurBusDepot' user='postgres' host='localhost' password='postgres'")
except:
    print "I am unable to connect to the database"
try:
    cur = conn.cursor()

# the following query prints in the format terminal 1 , via , terminal 2 along with their lat longs   
    sql =  """select rs.termini1 as term1, ST_X(t1.geom) as geom1_X, ST_Y(t1.geom) as geom1_Y, 
rs.termini2 as term2, ST_X(t3.geom) as geom3_X,ST_Y(t3.geom)  as geom3_Y,
rs.rs_id as rsId from t1_t2_rs_final_31052019 as rs inner join t_31052019 AS t1 on t1.name = rs.termini1 
inner join t_31052019 AS t3 on t3.name = rs.termini2 
where rs.via1 = ''
ORDER BY 1, 3"""
    cur.execute(sql)
    result_set= cur.fetchall()
   
    
    for row in result_set  :
        i = termini_list.index(row[0])
        j = termini_list.index(row[3])
        if i < j:
            #print k  
            print row[0], " " , row[3]
            
#        print 'RS'+str(i)+'_'+ str(j)
            if T[i][j]==0:
                T[i][j] = 'RS_'+str(i)+'_'+ str(j)
                print T[i][j]
                create_rs(row[1], row[2], row[4], row[5], T[i][j] )
            
                #cur.execute("UPDATE t1_t2_jeep_rs SET rs_id=(%s) WHERE termini1 = (%s) and termini2 = (%s)", (T[i][j],row[0],row[3]));
            
        else:
            print row[0], " " , row[3]
            
#        print 'RS'+str(j)+'_'+ str(i)
            if T[j][i]==0:
                #print k                 
                T[j][i] = 'RS_'+str(j)+'_'+ str(i)
                print T[j][i]
                create_rs(row[4], row[5], row[1], row[2],T[j][i] )
            
                #cur.execute("UPDATE t1_t2_jeep_rs SET rs_id=(%s) WHERE termini1 = (%s) and termini2 = (%s)", (T[j][i],row[0],row[3])); 
    sql = """select rs.termini1 as term1, ST_X(t1.geom) as geom1_X, ST_Y(t1.geom) as geom1_Y, 
rs.via1 as rsvia, ST_X(t2.geom) as geom2_X, ST_Y(t2.geom) as geom2_Y,
rs.termini2 as term2, ST_X(t3.geom) as geom3_X,ST_Y(t3.geom)  as geom3_Y,
rs.rs_id as rsId from t1_t2_rs_final_31052019 as rs inner join t_31052019 AS t1 on t1.name = rs.termini1 
inner join t_31052019 as t2 on t2.name = rs.via1
inner join t_31052019 AS t3 on t3.name = rs.termini2 
ORDER BY 1, 3;"""    
    cur.execute(sql)
    result_set=[]
    result_set= cur.fetchall()
    
    for row in result_set:
        i = termini_list.index(row[0])
        j = termini_list.index(row[6])
        k = termini_list.index(row[3])
                     
        if i < j:
            #print k  
            print row[0], " via ", row[3]," " , row[6]
                
#        print 'RS'+str(i)+'_'+ str(j)
                
            rs_via_id = 'RS_'+str(i)+'_'+ str(j)+'_v_'+str(k)
            create_rs_via(row[1], row[2], row[4], row[5], row[7], row[8], rs_via_id )
               # cur.execute("UPDATE t1_t2_jeep_rs SET rs_id=(%s) WHERE termini1 = (%s) and termini2 = (%s)", (T[i][j],row[0],row[3]));
            
        else:
            print row[0], " via " , row[3],  " ", row[6],
            
#        print 'RS'+str(j)+'_'+ str(i)
       
                
            rs_via_id = 'RS_'+str(j)+'_'+ str(i)+'_v_'+str(k)
                #cur.execute("UPDATE t1_t2_jeep_rs SET rs_id=(%s) WHERE termini1 = (%s) and termini2 = (%s)", (T[j][i],row[0],row[3])); 
    
    

    
#            
#i, j = 0, 0 ; 
    conn.commit()
    cur.close()
except Exception as e:
    print (e)
#
## Commit changes
layer.commitChanges()
iface.addVectorLayer("E:\\CTARA\\MTP\\shapefiles\\testFolder20022019\\rs_generic_10062019_3.shp",  "rs10062019", "ogr")
