#! /usr/bin/python3
"""
Gestión de números aleatorios y manejo de archivos WAVE mono y estéreo.

Uso:
    estereo.py [opciones] <ficL> [ficR] <ficEste> 
    estereo.py mono [options] <ficEste> <ficMono> 

Opciones:
  -l, --left                     La señal mono es el canal izquierdo de la señal estéreo.
  -r, --right                    La señal mono es el canal derecho de la señal estéreo.
  -s, --suma                     La señal mono es la semisuma de los dos canales.
  -d, --diferencia               La señal mono es la semidiferencia de los dos canales.
  -h, --help                     Mostrar esta ayuda.
  --version                      Mostrar la versión del programa.
"""

from docopt import docopt
from estereo import *

if __name__ == '__main__':
    args = docopt(__doc__, version="Gestor de archivos WAVE v1.0")

    if args['mono']:
        ficEste = args["<ficEste>"]
        ficMono = args["<ficMono>"]
        canal = 2  # por defecto: semisuma

        if args['--left']:
            canal = 0
        elif args['--right']:
            canal = 1
        elif args['--diferencia']:
            canal = 3

        estereo2mono(ficEste, ficMono, canal=canal)
        print("Conversión a mono completada correctamente.")

    else:
        ficL = args["<ficL>"]
        ficR = args["<ficR>"]
        ficEste = args["<ficEste>"]

        if ficR is None:
            raise ValueError("Error: Falta el fichero del canal derecho (ficR).")

        mono2estereo(ficL, ficR, ficEste)
        print("Archivo estéreo creado correctamente.")
