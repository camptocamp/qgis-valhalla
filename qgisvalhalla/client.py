# -*- coding: utf-8 -*-

## Code partially adapted from the QGIS - Valhalla plugin by Nils Nolde(nils@gis-ops.com)


from PyQt5.QtCore import QVariant

from qgis.core import (QgsPointXY,
                       QgsGeometry,
                       QgsFeature,
                       QgsVectorLayer,
                       QgsField)

from .utils import transformToWGS, decodePolyline6

class RoutingException(Exception):
    pass
    
class ValhallaClient():

    def __init__(connector = None):
        self.connector = connector or ConsoleConnector


    def route(points, crs, options, shortest=False):
        """
        Computes a route

        :param points: A list of QgsPointsXY with the points that define the route
        :type points: list

        :param crs: The crs in which the points coordinates are expressed
        :type crs: QgsCoordinateReferenceSystem

        :param options: The options for computing the route
        :type options: dict

        :param points: If True, computes shortest length route instead of shorter time
        :type points: bool

        :returns: Ouput layer with a single geometry containing the route.
        :rtype: QgsVectorLayer
        """


        points = pointsFromQgsPoints(qgspoints)
        try:
            response = self.connector.route(points, options)
        except Exception as e:
            raise RoutingException(str(e))
        route = createRouteFromResponse(response)
        return route

    def pointsFromQgsPoints(qgspoints, crs):
        points = []
        xform = transformToWGS(crs)
        for qgspoint in qgspoints:
            transformed = xform.transform(qgspoint)
            points.append({"lon": round(transformed.x(), 6), "lat": round(transformed.y(), 6)})
        return points


    def createRouteFromResponse(response):
        """
        Build output layer based on response attributes for directions endpoint.

        :param response: API response object
        :type response: dict


        :returns: Ouput layer with a single geometry containing the route.
        :rtype: QgsVectorLayer
        """
        response_mini = response['trip']
        feat = QgsFeature()
        coordinates, distance, duration = [], 0, 0
        for leg in response_mini['legs']:
                coordinates.extend([
                    list(reversed(coord))
                    for coord in decodePolyline6(leg['shape'])
                ])
                duration += round(leg['summary']['time'] / 3600, 3)
                distance += round(leg['summary']['length'], 3)

        qgis_coords = [QgsPointXY(x, y) for x, y in coordinates]
        feat.setGeometry(QgsGeometry.fromPolylineXY(qgis_coords))
        feat.setAttributes([distance,
                            duration
                            ])

        layer = QgsVectorLayer("LineString?crs=epsg:4326", "route", "memory")
        provider = layer.dataProvider()
        provider.addAttributes([QgsField("DIST_KM", QVariant.Double),
                             QgsField("DURATION_H", QVariant.Double)])
        layer.updateFields()
        provider.addFeature(feat)
        layer.updateExtents()
        return layer


