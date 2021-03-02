#   ---  COURSEWORK 02  ---
# this game is played in 1920x1080 and
# scaling 100% (not 125%)

from constants import *
from startcanvas import StartCanvas

# TODO wizard png to gif
# TODO credit


def Main():
    root = Tk()
    startcanvas = StartCanvas(root, 1920, 1080)
    startcanvas.start()


if __name__ == "__main__":
    Main()
