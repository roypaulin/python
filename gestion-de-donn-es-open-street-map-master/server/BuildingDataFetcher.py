from DataFetcher import DataFetcher
import database as db
import os

class BuildingDataFetcher(DataFetcher):
    colorBindings = {}

    def __init__(self, bbox, srid):
        super().__init__(bbox, srid)

    def search(self, bbox):
        """
            Requêtage de la bdd
            :param bbox: Boundary Box pour la recherche
        """
        #"SELECT tags->'highway', ST_AsText(ST_Transform(linestring, %s)) " +\
        raw_query =\
            "SELECT tags->'building', ST_AsText(linestring) " +\
            "FROM ways " +\
            "WHERE  tags ? 'building' " +\
            "AND ST_Contains(ST_MakeEnvelope(%s, %s, %s, %s, %s), ST_Transform(linestring, %s) ) "

        # Exec
        (cursor, connection) = db.execute_query(
            raw_query,
            *bbox,
            self.srid,
            self.srid
        )

        res = list(cursor)
        self._randomizeColorBindings(res)

        cursor.close()
        db.close_connection(connection)

        return res

    def getData(self, bbox):
        filepath = f'{type(self).__name__}_building_{str(bbox)}.txt'
        if os.path.isfile(filepath):
            return self._readResultBuffer(filepath)

        return self.search(bbox)
