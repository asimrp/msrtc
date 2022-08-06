import sys
import os.path

# from qgis.core import QgsApplication
# qgishome = 'C:\\Program Files\\QGIS 3.22.9\x07pps\\qgis-ltr'
# app = QgsApplication([], True)
# QgsApplication.setPrefixPath(qgishome, True) 

import pandas as pd

from PyQt5.QtCore import *
from qgis.gui import *
from qgis.utils import iface
from qgis import processing
from qgis.analysis import *
from qgis.core import *
from qgis.PyQt.QtCore  import QVariant

import qgis.utils


context = QgsProcessingContext() 
context.setProject(QgsProject.instance())

point_layer = QgsProcessingUtils.mapLayerFromString ("/D:/M.Tech/Fifth Sem/MTP/snr/projection.shp",context)

network_layer = QgsProcessingUtils.mapLayerFromString ("/D:/M.Tech/Fifth Sem/MTP/snr/Transport_Road.shp",context)

# [From this point I am not sure what actually hapening]
#creating an empty layer
cLayer = qgis.utils.iface.mapCanvas().currentLayer()
provider = cLayer.dataProvider()
#print (provider.encoding(),",", provider.fields(),",", provider.crs())

outputpath = "D:/M.Tech/Fifth Sem/MTP/snr/sinnar_dg.shp"

# SaveVectorOptions contains many settings for the writer process
# Write to an ESRI Shapefile format dataset using UTF-8 text encoding
save_options = QgsVectorFileWriter.SaveVectorOptions()
save_options.driverName = "ESRI Shapefile"
save_options.fileEncoding = "UTF-8"
transform_context = QgsProject.instance().transformContext()
writer = QgsVectorFileWriter.writeAsVectorFormatV3(cLayer,
                                                 outputpath,
                                                  transform_context,
                                                  save_options) #[Not sure if this one is right or wrong]

layer = QgsVectorLayer(outputpath,"rs02082022", "ogr")

if not layer.isValid():
    print ("Layer failed to load!")

#start editing
layer.startEditing()
provider = layer.dataProvider()

#add fields
provider.addAttributes( [ QgsField("AddressFrom",  QVariant.String)] )
provider.addAttributes( [ QgsField("AddressTo",  QVariant.String)] )
layer.commitChanges()

# prepare graph
vectorLayer  = QgsVectorLayer ("/D:/M.Tech/Fifth Sem/MTP/snr/Transport_Road.shp",'lines')
director = QgsVectorLayerDirector( vectorLayer, -1, '', '', '', 3 )
strategy = QgsNetworkDistanceStrategy()
director.addStrategy( strategy )

builder = QgsGraphBuilder(vectorLayer.crs()) #[ERROR]

# [From this point the code is not working properly.]
# prepare points
features = processing.features(point_layer) #[ERROR]
point_count = point_layer.featureCount() #It's showing 0 points means 
                                        #I did something wrong while debugging but what was that I am not sure.

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
        
        df = pd.read_csv('/D:/M.Tech/Fifth Sem/MTP/snr/Unique_Routes.csv')
        z= str(point_layer['address'][i]) +";;;;;" + str( point_layer['address'][j] ) #[Not sure which address I have to pass]
        #z=str((point_layer['address'][i]) + point_layer['address'][j]) ) 
        # point_layer['address'][i] represent from_address 
        # point_layer['address'][j] represent To_address
        fet.setAttributes([z] ) #instead of i we need to write "address" from shapefile 
        #after editing z values  just replace i with z
        provider.addFeatures([fet])
        layer.commitChanges()
        writer.addFeature(fet)
        
    
qgis.utils.iface.addVectorLayer(outputpath, "rs02082022", "ogr")

del writer