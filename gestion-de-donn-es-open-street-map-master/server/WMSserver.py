#!/usr/bin/python3

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import urllib.parse as urlparse
from TileRenderer import TileRenderer
from DataFetcherFactory import DataFetcherFactory
from tempfile import gettempdir
import database as db
import os
from threading import Semaphore
import config


sema = Semaphore(config.MAX_THREADS / 2)
PORT_NUMBER = 4242


class WMSHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        global sema
        if self.path.startswith("/wms"):
            # Ici on récupère les valeurs de paramètres GET
            params = urlparse.parse_qs(urlparse.urlparse(self.path).query)
            
            mandatoryParameters = ["request", "layers", "width", "height", "srs", "bbox"]
            if(not all(elem in params.keys() for elem in mandatoryParameters)):
                mising_params = list(set(mandatoryParameters) - set(params.keys()))
                self.send_error(
                    400, f"Requête mal formée : les elements suivants sont manquants : {' '.join(mising_params)}")

            print(params)
            requestType = params["request"][0]
            if(requestType != "GetMap"):
                self.send_error(400, f"Le type de requête \"{params['request']}\" n'est pas supporté !")
                return
            
            layer = params["layers"][0]
            if(layer not in DataFetcherFactory.getAllowedLayers()):
                self.send_error(400, f"La couche demandée ({layer}) ne fait pas partie des couches proposées par l'application !\
                    Les couches disponibles sont {' '.join(DataFetcherFactory.getAllowedLayers())}")
                return
            
            bbox_origin = eval(params["bbox"][0])
            bbox = (bbox_origin[0], bbox_origin[2], bbox_origin[1], bbox_origin[3])
            width = int(params["width"][0])
            height=int(params["height"][0])

            srs = params["srs"][0]
            if(srs != "EPSG:3857"):
                self.send_error(
                    400, f"Le format {srs} n'est pas supporté ! Seul EPSG:3857 est accepté !")
                return

            imageName = f"{layer}_{width}x{height}_{str(bbox)}"
            imagePath = f"{gettempdir()}/{imageName}.png"
            if not os.path.isfile(imagePath):
                sema.acquire()
                tr = TileRenderer( (width, height),layer, bbox, 3857)
                tr.render()
                sema.release()
            self.send_png_image(imagePath)
            return

        self.send_error(404, 'Fichier non trouvé : %s' % self.path)

    def send_plain_text(self, content):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=UTF-8')
        self.end_headers()
        self.wfile.write(bytes(content, "utf-8"))

    def send_png_image(self, filename):
        self.send_response(200)
        self.send_header('Content-type', 'image/png')
        self.end_headers()
        with open(filename, 'rb') as file:
            self.wfile.write(file.read())

    def send_html_file(self, filename):
        self.send_response(200)
        self.end_headers()
        self.serveFile(filename)


if __name__ == "__main__":
    try:
        # Ici on crée un serveur web HTTP, et on affecte le traitement
        # des requêtes à notre releaseHandler ci-dessus.
        server = ThreadingHTTPServer(('', PORT_NUMBER), WMSHandler)
        print('Serveur démarré sur le port ', PORT_NUMBER)
        print('Ouvrez un navigateur et tapez dans la barre d\'url :'
              + ' http://localhost:%d/' % PORT_NUMBER)

        # Ici, on demande au serveur d'attendre jusqu'à la fin des temps...
        server.serve_forever()

    # ...sauf si l'utilisateur l'interrompt avec ^C par exemple
    except KeyboardInterrupt:
        print('^C reçu, je ferme le serveur. Merci.')
        server.socket.close()
        db.close_connections()
