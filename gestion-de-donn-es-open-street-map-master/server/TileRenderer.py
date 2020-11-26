import database as db
from drawer import Image
from tempfile import gettempdir
from DataFetcherFactory import DataFetcherFactory


X = 0
Y = 1

WIDTH = 0
HEIGHT = 1

XMIN = 0
XMAX = 1
YMIN = 2
YMAX = 3

MAX_RGB = 255

class TileRenderer:

    def __init__(self, imageDimensions, datatype, boundingBox, srid):
        self.imageDimensions = imageDimensions
        self.searchEngine = DataFetcherFactory.create(datatype, boundingBox, srid)
        self.bbox = boundingBox
        self.srid = srid
        self.imageName = f"{datatype}_{imageDimensions[WIDTH]}x{imageDimensions[HEIGHT]}_{str(boundingBox)}"

    def linestringToTuple(self, linestring):
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
    

    def rescalePoints(self, all_coords, oldOrigins, scalingFactors, IMAGE_SIZE):
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
                            (coord[X] - oldOrigins[X]) * scalingFactors[X],
                            (coord[Y] - oldOrigins[Y]) * scalingFactors[Y]
                        ], all_coords))


    def getRealBoundingRect(self, lines, bbox):
        """
            Trouve une "vraie" boundary box en fonction des données les données.
            Note : Pas utilisé ici pour garder "la forme" du dessin
            :param lines: données
            :param bbox: ancienne bondary box, celle de la recherche
            :return: nouvelle bondary box
        """
        maxX = self.bbox[XMAX]
        minX = self.bbox[XMIN]
        minY = self.bbox[YMIN]
        maxY = self.bbox[YMAX]
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


    def render(self):
        bbox = self.bbox
        IMAGE_SIZE = self.imageDimensions
        COLORS_BINDING = self.searchEngine.getColorBindings()
        # À décommenter pour chercher dans la BDD. Mais c'est beaucoup trop long et chiant donc à vos risques et périls.
        #resBuffer = search(bbox)
        resBuffer = self.searchEngine.getData(bbox)
        bbox_unflat = self.linestringToTuple(self.searchEngine.convertBbox())
        bbox_flat = [item for sublist in bbox_unflat for item in sublist]
        bbox = [bbox_flat[0], bbox_flat[2], bbox_flat[1], bbox_flat[3]]
        linestrings = list(map(lambda res: res[1], resBuffer))
        types = list(map(lambda res: res[0], resBuffer))

        image = Image(*IMAGE_SIZE)
        # Conversion de toutes les représentation de string en tuples utilisables
        conv_linestrs = list(
            map(lambda linestr: self.linestringToTuple(linestr), linestrings))

        #linestrs_adapted = self.adaptToSrid(conv_linestrs)
        #print(conv_linestrs)

        # On ramène l'échelle à une origine de 0 et on scale à la taille de l'image
        scalingFactorX = IMAGE_SIZE[WIDTH] / (bbox[XMAX] - bbox[XMIN])
        scalingFactorY = IMAGE_SIZE[HEIGHT] / (bbox[YMAX] - bbox[YMIN])
        rescaled_pts = list(map(lambda line: self.rescalePoints(
            line, (bbox[XMIN], bbox[YMIN]), (scalingFactorX, scalingFactorY), IMAGE_SIZE), conv_linestrs))
        #print(rescaled_pts)
        # On dessine le tout
        for index, line in enumerate(rescaled_pts):
            # PyCairo, restant bien dans la veine des trucs pythons, ne respecte pas la convention de l'échelle
            # des 255 pour les couleurs. On corrige donc l'échelle pour lui.
            rgba_profile = list(
                map(lambda x: x / MAX_RGB if x > 1 else x,
                    COLORS_BINDING.get(types[index], (158, 244, 114, 0.8))
                )
            )
            image.draw_linestring(line, rgba_profile)
        # Et on sauvegarde
        image.save(f"{gettempdir()}/{self.imageName}.png")
