import database as db
from drawer import Image
from tempfile import gettempdir


X = 0
Y = 1

WIDTH = 0
HEIGHT = 1

XMIN = 0
XMAX = 1
YMIN = 2
YMAX = 3

MAX_RGB = 255

HIGHWAY_COLORS_BINDING = {
    'motorway_link': (44, 61, 38, 0.6),
    'path': (57, 76, 158, 0.3),
    'pedestrian': (104, 149, 97, 0.4),
    'no': (103, 133, 44, 0.5),
    'primary': (227, 200, 132, 0.1),
    'bus_stop': (183, 91, 153, 0.3),
    'primary_link': (154, 105, 205, 0.9),
    'tertiary_link': (58, 93, 44, 0.6),
    'trunk': (134, 218, 90, 0.3),
    'tertiary': (158, 244, 114, 0.5),
    'secondary_link': (165, 79, 91, 0.2),
    'track': (131, 69, 208, 0.5),
    'footway': (245, 64, 136, 0.3),
    'living_street': (32, 114, 178, 0.8),
    'motorway': (200, 121, 127, 0.1),
    'construction': (68, 209, 86, 1),
    'platform': (150, 91, 170, 0.5),
    'rest_area': (174, 171, 194, 0.6),
    'services': (150, 91, 170, 0.5),
    'proposed': (174, 171, 194, 0.6),
    'residential': (138, 155, 137, 0.6),
    'road': (145, 65, 153, 0.7),
    'bridleway': (80, 134, 200, 0.2),
    'cycleway': (115, 76, 214, 0.4),
    'raceway': (0, 220, 15, 0.2),
    'via_ferrata': (35, 177, 233, 0.7),
    'unclassified': (159, 21, 153, 0.5),
    'steps': (180, 205, 40, 0.9),
    'corridor': (37, 220, 97, 0.5),
    'trunk_link': (212, 102, 168, 0.5),
    'service': (246, 143, 37, 0.8),
    'secondary': (194, 107, 118, 1)
}


def linestringToTuple(linestring):
    """
        Parse une représentation textuelle d'un linestring en tuple de point
        Ex : "LINESTRING( 1 2, 3 4)" devient ( (1,2), (3,4) )
        :param: le string à parser
        :return: le tuple de points
    """
    points = linestring[len("LINESTRING("):-1].split(",")
    all_coords = list(map(lambda point: point.strip().split(" "), points))
    return list(map(lambda coord:
                    [
                        float(coord[X]),
                        float(coord[Y])
                    ], all_coords))


def rescalePoints(all_coords, oldOrigins, scalingFactors, IMAGE_SIZE):
    """
        Change l'échelle des points pour permettre d'utiliserla résolution d'image IMAGE_SIZE
        :param all_coords: les données
        :param origin: les coordonées de l'origine de l'échelle actuelle (X,Y)
        :param origin: les facteurs d'aggrandissement pour étirer l'image (X,Y)
        :param origin: la taille de l'image (HEIGHT,WIDTH)
        :return: Une nouvelles liste contenant les données mise à l'échelle 

    """
    return list(map(lambda coord:
                    [
                        min((coord[X] - oldOrigins[X]) *
                            scalingFactors[X], IMAGE_SIZE[WIDTH]),
                        min((coord[Y] - oldOrigins[Y]) *
                            scalingFactors[Y], IMAGE_SIZE[HEIGHT])
                    ], all_coords))


def getRealBoundingRect(lines, bbox):
    """
        Trouve une "vraie" boundary box en fonction des données les données.
        Note : Pas utilisé ici pour garder "la forme" du dessin
        :param lines: données
        :param bbox: ancienne bondary box, celle de la recherche
        :return: nouvelle bondary box
    """
    minX = bbox[XMIN]
    maxX = bbox[XMAX]
    minY = bbox[YMIN]
    maxY = bbox[YMAX]
    for line in lines:
        for point in line:
            if point[X] < minX:
                minX = point[X]
            if point[Y] < minY:
                minY = point[Y]
            if point[X] > maxX:
                maxX = point[X]
            if point[Y] > maxY:
                maxY = point[Y]
    return (minX, maxX, minY, maxY)


def search(bbox):
    """
        Requêtage de la bdd
        :param bbox: Boundary Box pour la recherche
    """
    raw_query =\
        "SELECT tags->'highway', ST_AsText(linestring) " +\
        "FROM ways " +\
        "WHERE  tags ? 'highway' " +\
        "AND ST_Contains(ST_MakeEnvelope(%s, %s, %s, %s, 4326), linestring ) "

    # Exec
    cursor = db.execute_query(
        raw_query,
        *bbox
    )

    res = list(cursor)

    cursor.close()
    db.close_connection()

    return res


def readResultBuffer(path):
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


def main():
    bbox = (5.7, 5.8, 45.1, 45.2)
    IMAGE_SIZE = (1920, 1080)
    # À décommenter pour chercher dans la BDD. Mais c'est beaucoup trop long et chiant donc à vos risques et périls.
    #resBuffer = search(bbox)
    resBuffer = readResultBuffer("resultBuffer.txt")
    linestrings = list(map(lambda res: res[1], resBuffer))
    types = list(map(lambda res: res[0], resBuffer))

    image = Image(*IMAGE_SIZE)
    # Conversion de toutes les représentation de string en tuples utilisables
    conv_linestrs = list(
        map(lambda linestr: linestringToTuple(linestr), linestrings))

    # On ramène l'échelle à une origine de 0 et on scale à la taille de l'image
    scalingFactorX = IMAGE_SIZE[WIDTH] / (bbox[XMAX] - bbox[XMIN])
    scalingFactorY = IMAGE_SIZE[HEIGHT] / (bbox[YMAX] - bbox[YMIN])
    rescaled_pts = list(map(lambda line: rescalePoints(
        line, (bbox[XMIN], bbox[YMIN]), (scalingFactorX, scalingFactorY), IMAGE_SIZE), conv_linestrs))

    # On dessine le tout
    for index, line in enumerate(rescaled_pts):
        # PyCairo, restant bien dans la veine des trucs pythons, ne respecte pas la convention de l'échelle
        # des 255 pour les couleurs. On corrige donc l'échelle pour lui.
        rgba_profile = list(
            map(lambda x: x / MAX_RGB if x > 1 else x,
                HIGHWAY_COLORS_BINDING[types[index]])
        )
        image.draw_linestring(line, rgba_profile)
    # Et on sauvegarde
    image.save(f"{gettempdir()}/meh.png")


main()
