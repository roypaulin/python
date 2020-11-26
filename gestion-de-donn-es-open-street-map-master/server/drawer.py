import cairo


class Image:
    """
    Cette classe représente une image dotée d'un
    contexte graphique sur lequel on peut dessiner
    des formes élémentaires.
    """
    def __init__(self, width, height):
        """
        Initialise une image en spécifiant ses dimensions.

        :param width: la largeur de l'image
        :param height: la hauteur de l'image
        """
        self.width = width
        self.height = height
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        self.ctx = cairo.Context(self.surface)

    def draw_line(self, x0, y0, x1, y1, stroke_color):
        """
        Dessine une ligne sur l'image.

        :param x0: abscisse du premier point
        :param y0: ordonnée du premier point
        :param x1: abscisse du second point
        :param y1: ordonnée du second point
        :param stroke_color: quadruplet représentant la couleur RGBA
        """
        self.ctx.set_source_rgba(*stroke_color)
        self.ctx.set_line_width(1)
        self.ctx.move_to(x0, y0)
        self.ctx.line_to(x1, y1)
        self.ctx.stroke()

    def draw_linestring(self, points, stroke_color):
        """
        Dessine une ligne brisée sur l'image.

        :param points: la liste des sommets
        :param stroke_color: quadruplet représentant la couleur RGBA
        """
        self.ctx.set_source_rgba(*stroke_color)
        self.ctx.set_line_width(1)
        iter_points = iter(points)
        x, y = next(iter_points)
        self.ctx.move_to(x, y)
        for x, y in iter_points:
            self.ctx.line_to(x, y)
        self.ctx.stroke()

    def draw_polygon(self, points, stroke, fill):
        """
        Dessine un polygone sur l'image.

        :param points: la liste des sommets
        :param stroke: quadruplet représentant la couleur de ligne RGBA
        :param fill: quadruplet représentant la couleur de remplissage RGBA
        """
        self.ctx.set_source_rgba(*fill)
        iter_points = iter(points)
        x, y = next(iter_points)
        self.ctx.move_to(x, y)
        for x, y in iter_points:
            self.ctx.line_to(x, y)
        self.ctx.close_path()
        self.ctx.fill()
        self.ctx.set_source_rgba(*stroke)
        self.ctx.set_line_width(1)
        iter_points = iter(points)
        x, y = next(iter_points)
        self.ctx.move_to(x, y)
        for x, y in iter_points:
            self.ctx.line_to(x, y)
        self.ctx.close_path()
        self.ctx.stroke()

    def draw_rectangle(self, x0, y0, x1, y1, stroke, fill):
        """
        Dessine un rectangle parallèle aux axes principaux.

        :param x0: abscisse du premier sommet
        :param y0: ordonnée du premier sommet
        :param x1: abscisse du second sommet
        :param y1: ordonnée du second sommet
        :param stroke: quadruplet représentant la couleur de ligne RGBA
        :param fill: quadruplet représentant la couleur de remplissage RGBA
        """
        self.ctx.set_source_rgba(*fill)
        self.ctx.rectangle(x0, y0, x1, y1)
        self.ctx.fill()
        self.ctx.set_source_rgba(*stroke)
        self.ctx.rectangle(x0, y0, x1, y1)
        self.ctx.stroke()

    def save(self, filename):
        """
        Sauvegarde l'image au format PNG.

        :param filename: le nom du fichier
        """
        self.surface.write_to_png(filename)
