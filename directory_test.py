from pathlib import Path
from os import listdir
from random import choice
from tkinter import *

"""
TEST FILE. NOT FOR USERS.
"""

current_path: Path = Path(__file__).parent.resolve()
resources_path = str(current_path) + "/resources"
enemy_folders = [(resources_path + "/" + p)
                 for p in listdir("resources") if p != "wizard"]


def get_animations():
    with open("Animations.txt", "w") as file:
        animations = []
        for folder in enemy_folders:
            seq_path = f"{folder}/{listdir(folder)[0]}/PNG Sequences"
            file.write(f"{folder[95:]}\n")
            for subfolder in listdir(seq_path):
                file.write(f"    {subfolder}\n")
                if subfolder not in animations:
                    animations.append(subfolder)

        for folder in enemy_folders:
            seq_path = f"{folder}/{listdir(folder)[0]}/PNG Sequences"
            for animation in animations:
                if animation not in listdir(seq_path):
                    animations.remove(animation)

        file.write("\n\n\nCOMMON ANIMATIONS:\n")
        for animation in animations:
            file.write(f"{animation}\n")


class Enemy():
    animation_sets = [0]

    def __init__(self, canvas, ttype="", sel="random", x=500, y=500):
        idle_path = f"D:/Desktop/Uni/computer science/GitLab/programming-practicals_n98211tb/coursework_02/resources/{ttype}/{ttype}_01/PNG Sequences/Idle/"
        self.animation_sets[0] = list([
            idle_path + d for d in listdir(idle_path)])
        self.current_frame = 0
        self.current_image = PhotoImage(
            file=self.animation_sets[0][self.current_frame])
        self.idd = canvas.create_image(x, y)
        canvas.itemconfig(self.idd, image=self.current_image)

    def update_frame(self):
        self.current_frame += 1
        if self.current_frame >= len(self.animation_sets[0]):
            self.current_frame = 0
        self.current_image = PhotoImage(
            file=self.animation_sets[0][self.current_frame])
        canvas.itemconfig(self.idd, image=self.current_image)


root = Tk()
canvas = Canvas(root, width=800, height=800, bg="white")
canvas.pack()

enemy1 = Enemy(canvas, "Wraith", "choice", 200, 200)
enemy2 = Enemy(canvas, "Satyr", "choice", 600, 600)

while (True):
    enemy1.update_frame()
    enemy2.update_frame()
    root.update()
root.mainloop()
