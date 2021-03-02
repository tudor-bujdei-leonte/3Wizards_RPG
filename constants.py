from tkinter import *
from time import perf_counter, sleep
from pathlib import Path
from os import listdir
from random import choice, randint, uniform
from platform import platform
from math import pi, sin, cos
from queue import Queue
from copy import deepcopy as copy

"""
Contains all standard lib imports and a few important constants such as the
resources folder path.
"""

current_path: Path = Path(__file__).parent.resolve()
resources_path = str(current_path) + "/resources/entities"
enemy_folders = [(resources_path + "/" + p)
                 for p in listdir("resources/entities")
                 if p != "wizard" and p != "objects"]
ally_folders = ["/resources/entities/wizard"]
enemy_types = [p for p in listdir(
    "resources/entities") if p != "wizard" and p != "objects"]
enemy_size = [420, 420]  # differs
objects_folder = str(current_path) + "/resources/objects"
