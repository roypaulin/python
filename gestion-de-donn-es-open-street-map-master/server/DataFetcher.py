import database as db
from random import randint, uniform

class DataFetcher:

    def __init__(self, bbox, srid):
        self.bbox = bbox
        self.srid = srid

    def search(self, bbox):
        """
            Requêtage de la bdd
            :param bbox: Boundary Box pour la recherche
        """
        pass

    def getColorBindings(self):
        return self.colorBindings

    def _readResultBuffer(self, path):
        """
            Lit le fichier dans lequel sont stockés les résultats de la requête
            :param path: chemin du fichier
        """
        res = list()
        with open(path, 'r') as fp:
            line = fp.readline()
            while line:
                res.append(eval(line))
                line = fp.readline()
        return res
    
    def _randomizeColorBindings(self, res):
        """
            Affecte une couleur aléatoire à chaque type différent dans la liste de résultat passé en paramètre
            :param res: le resultat à analyser
        """
        for result in res:
            if result[0] not in self.colorBindings:
                self.colorBindings[result[0]] = (randint(10, 255), randint(10, 255), randint(10, 255), uniform(0.4,1))

    def convertBbox(self):
        """
            Requêtage de la bdd
            :param bbox: Boundary Box pour la recherche
        """
        raw_query =\
            "select ST_AsText(ST_TRANSFORM(ST_GeomFromText('LINESTRING(%s %s, %s %s)', %s), 4326))"

        # Exec
        (cursor, connection) = db.execute_query(
            raw_query,
            self.bbox[0],
            self.bbox[2],
            self.bbox[1],
            self.bbox[3],
            self.srid
        )

        res = list(cursor)

        cursor.close()
        db.close_connection(connection)
        return res[0][0]
