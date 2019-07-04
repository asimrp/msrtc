from PyQt4.QtCore import *
#creating an empty layer

cLayer = qgis.utils.iface.mapCanvas().currentLayer()
provider = cLayer.dataProvider()
print provider.encoding(),",", provider.fields(),",", provider.crs()
writer = QgsVectorFileWriter( "E:\\CTARA\\MTP\\shapefiles\\ShahpurFinal31052019\\v_intersect_rs_02062019_5.shp", provider.encoding(), provider.fields(),QGis.WKBPoint, provider.crs() )
#cLayer =iface.addVectorLayer("E:\Blah3.shp", "Blah3", "ogr")
#provider = cLayer.dataProvider()
layer = QgsVectorLayer("E:\\CTARA\\MTP\\shapefiles\\ShahpurFinal31052019\\v_intersect_rs_02062019_5.shp", "v_intersect_rs_02062019", "ogr")
if not layer.isValid():
    print "Layer failed to load!"
#

layer1 = iface.addVectorLayer("E:\\CTARA\\MTP\\shapefiles\\ShahpurFinal31052019\\v_final_02062019.shp", "vert_28042019", "ogr")
layer2 = iface.addVectorLayer("E:\\CTARA\\MTP\\shapefiles\\ShahapurFinal31052019\\rs_generic_31052019_1.shp", "roadNetwork_28042019", "ogr")
#mapcanvas = iface.mapCanvas()
#layers = mapcanvas.layers()
#
#if not cLayer:
#    print "layer cannot be loaded"
#start editing
layer.startEditing()
provider = layer.dataProvider()
#add fields
provider.addAttributes( [ QgsField("vert_id", QVariant.String),QgsField("rs_id",  QVariant.String)] )

# add a feature
fet = QgsFeature()

for a in layer2.getFeatures():
    print  a.attribute("rs_id")
    for b in layer1.getFeatures():
        #if geometries of point and line set intersect generates the points of intersection in sequence
        if b.geometry().intersects(a.geometry()):
            print b.attribute("vert_id") ,'','', a.attribute("rs_id")
            print b.geometry().asPoint().x() , b.geometry().asPoint().y()
#            print  a.attribute("feat_name"),a.geometry().asPolyline()
            fet.setGeometry(QgsGeometry.fromPoint(QgsPoint(b.geometry().asPoint().x(),b.geometry().asPoint().y())))
            fet.setAttributes([b.attribute("vert_id"), a.attribute("rs_id")])
            provider.addFeatures([fet])


#segLayer = iface.addVectorLayer("E:\CTARA\MTP\shapefiles\testFolder20022019\test27022019.shp", "testSegments0303", "ogr")

# Commit changes
layer.commitChanges()
iface.addVectorLayer("E:\\CTARA\\MTP\\shapefiles\\ShahpurFinal31052019\\v_intersect_rs_02062019_5.shp", "v_intersect_rs_02062019", "ogr")
