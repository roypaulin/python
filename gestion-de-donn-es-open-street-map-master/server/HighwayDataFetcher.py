from DataFetcher import DataFetcher
import database as db
import os

class HighwayDataFetcher(DataFetcher):
    colorBindings = {
        'motorway_link': (44, 61, 38, 0.6),
        'path': (57, 76, 158, 0.3),
        'pedestrian': (104, 149, 97, 0.4),
        'escape': (14, 89, 197, 0.4),
        'no': (103, 133, 44, 0.5),
        'primary': (227, 200, 132, 1),
        'bus_stop': (183, 91, 153, 0.3),
        'bus_guideway': (183, 120, 173, 0.3),
        'primary_link': (154, 105, 205, 0.9),
        'tertiary_link': (58, 93, 44, 0.6),
        'trunk': (134, 218, 90, 0.8),
        'tertiary': (158, 244, 114, 0.5),
        'secondary_link': (165, 79, 91, 0.7),
        'track': (131, 69, 208, 0.5),
        'footway': (245, 64, 136, 0.3),
        'living_street': (32, 114, 178, 0.8),
        'motorway': (200, 121, 127, 0.9),
        'construction': (68, 209, 86, 1),
        'platform': (150, 91, 170, 0.5),
        'rest_area': (174, 171, 194, 0.6),
        'services': (150, 91, 170, 0.5),
        'proposed': (174, 171, 194, 0.6),
        'residential': (138, 155, 137, 0.6),
        'road': (145, 65, 153, 0.7),
        'bridleway': (80, 134, 200, 0.7),
        'cycleway': (115, 76, 214, 0.6),
        'raceway': (0, 220, 15, 0.2),
        'via_ferrata': (35, 177, 233, 0.7),
        'unclassified': (159, 21, 153, 0.5),
        'steps': (180, 205, 40, 0.9),
        'corridor': (37, 220, 97, 0.5),
        'trunk_link': (212, 102, 168, 0.5),
        'service': (246, 143, 37, 0.8),
        'secondary': (194, 107, 118, 1)
    }
    def __init__(self, bbox, srid):
        super().__init__(bbox, srid)

    def search(self, bbox):
        """
            Requêtage de la bdd
            :param bbox: Boundary Box pour la recherche
        """
            #"SELECT tags->'highway', ST_AsText(ST_Transform(linestring, %s)) " +\
        raw_query =\
            "SELECT tags->'highway', ST_AsText(linestring) " +\
            "FROM ways " +\
            "WHERE  tags ? 'highway' " +\
            "AND ST_Contains(ST_MakeEnvelope(%s, %s, %s, %s, %s), ST_Transform(linestring, %s) ) "

        # Exec
        (cursor, connection) = db.execute_query(
            raw_query,
            *bbox,
            self.srid,
            self.srid
        )

        res = list(cursor)

        cursor.close()
        db.close_connection(connection)

        return res
    
    def getData(self, bbox):
        filepath = f'{type(self).__name__}_highway_{str(bbox)}.txt'
        if os.path.isfile(filepath):
            return self._readResultBuffer(filepath)
        
        return self.search(bbox)
