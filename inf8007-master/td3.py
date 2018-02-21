#!/usr/bin/env python3.5
from os import listdir
from os.path import join, isfile

from td2 import SearchEngine
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from collections import defaultdict
import json


# this is used as json generator, see https://gist.github.com/hrldcpr/2012250
def _tree(): return defaultdict(_tree)

print('Mise en place du serveur...')

COURSE_PATH = '02/sample'
FILES = [join(COURSE_PATH, f) for f in listdir(COURSE_PATH) if isfile(join(COURSE_PATH, f))]


class AppHandler(BaseHTTPRequestHandler):
    search_engine = SearchEngine(FILES)

    def do_GET(self):
        """
        L’accession aux données se fait avec les paramètres suivant :
         - acronym (REQUIS) — le sigle du cours
         - sort — tri dans l’ordre décroissant des valeurs obtenues
         - length — nombre d’elements
        :return:
        """
        query = urlparse(self.path).query
        args = dict(i.split('=') for i in query.split('&'))
        args['sort'] = bool(args['sort']) if 'sort' in args else True
        args['length'] = int(args['length']) if 'length' in args else 10
        print(args)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        body = _tree()
        search_result = self.search_engine.search(args['acronym'], args['sort'])[:args['length']]
        body['data'] = [{'acr': acr, 'val': value, 'desc': self.search_engine.files[acr].original_content}
                        for acr, value in search_result]
        self.wfile.write(bytes(json.dumps(body), encoding="utf-8"))


def run():
    httpd = HTTPServer(('localhost', 8765), AppHandler)
    print('Serveur accessible à l’adresse http://localhost:8765. '
          'Appuyez sur ctrl-c pour interrompre.')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
