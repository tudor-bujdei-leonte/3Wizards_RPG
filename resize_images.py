from PIL import Image, ImageOps
import constants
from os import listdir, rename, remove, removedirs
from shutil import rmtree, copyfile

"""
TEST FILE. NOT FOR USERS.
"""


path = "D:/Desktop/Uni/computer science/GitLab/programming-practicals_n98211tb/coursework_02/resources/entities"


def gifize_frames():
    for folder in constants.enemy_folders:
        if "" in folder:
            for subfolder in listdir(folder):
                if "" in subfolder:
                    # remove_useless_folders(f"{folder}/{subfolder}")
                    path = f"{folder}/{subfolder}/PNG Sequences"
                    # rename(path, path[:-12] + "GIF Sequences")
                    for animation_folder in listdir(path):
                        animations_path = f"{path}/{animation_folder}"
                        for name in listdir(animations_path):
                            # resize_frame(f"{animations_path}/{name}")
                            gifize_frame(f"{animations_path}/{name}")

                        print(f"Done: {animations_path}")


def resize_frames():
    for folder in constants.enemy_folders:
        if "" in folder:
            for subfolder in listdir(folder):
                if "" in subfolder:
                    # remove_useless_folders(f"{folder}/{subfolder}")
                    path = f"{folder}/{subfolder}/PNG Sequences"
                    # rename(path, path[:-12] + "GIF Sequences")
                    for animation_folder in listdir(path):
                        animations_path = f"{path}/{animation_folder}"
                        for name in listdir(animations_path):
                            resize_frame(f"{animations_path}/{name}")
                            # gifize_frame(f"{animations_path}/{name}")

                        print(f"Done: {animations_path}")


def gifize_frame(frame_path):
    rename(frame_path, frame_path[:-3] + "gif")


def resize_frame(frame_path):
    frame = Image.open(frame_path)
    width, height = frame.size
    ratio = width / height
    height = 420
    width = int(420 * ratio)
    frame = frame.resize((width, height))
    frame.save(frame_path)


def remove_useless_folders():
    for folder in constants.enemy_folders:
        if "" in folder:
            for subfolder in listdir(folder):
                if "" in subfolder:
                    remove_useless_folder(f"{folder}/{subfolder}")
                    print("Done with: " + subfolder)


def remove_useless_folder(path):
    for subsubfolder in listdir(path):
        if subsubfolder != "PNG Sequences":
            rmtree(f"{path}/{subsubfolder}")


# heal = jump start + throwing in the air
# heal = taunt

# healed = jump start + jump loop
# healed = casting spells

def rename_healing():
    for folder in constants.enemy_folders:
        if "" in folder:
            for subfolder in listdir(folder):
                if "" in subfolder:
                    path = f"{folder}/{subfolder}/PNG Sequences"
                    healing(path, subfolder)


def healing(path, subfolder):
    if "Taunt" not in listdir(path):
        # move all from "jump start" and "throwing in the air" together
        for frame_path in listdir(f"{path}/Jump Start"):
            # print(f"{path}/Jump Start/{frame_path}")
            copyfile(
                f"{path}/Jump Start/{frame_path}",
                f"{path}/Throwing in The Air/{frame_path}"
            )

        # rename the resulting folder to "Healing"
        rename(
            f"{path}/Throwing in The Air",
            f"{path}/Healing"
        )
    else:
        rename(
            f"{path}/Taunt",
            f"{path}/Healing"
        )

    # completion to Healing: append jump_start in reverse order
    if "Slashing in The Air" in listdir(path):
        path_healing = f"{path}/Healing"
        path_jumpstart = f"{path}/Jump Start"
        i = 9
        for fp in listdir(path_jumpstart):
            fpp = f"{path_jumpstart}/{fp}"
            fpd = f"{path_healing}/{i}{fp}"
            copyfile(fpp, fpd)
            i -= 1

    print("Done: " + subfolder)


def rename_healed():
    for folder in constants.enemy_folders:
        if "" in folder:
            for subfolder in listdir(folder):
                if "" in subfolder:
                    path = f"{folder}/{subfolder}/PNG Sequences"

                    healed(path)


def healed(path):
    if "Wraith" not in path:
        # add jump start to itself in reverse order
        path_jumpstart = f"{path}/Jump Start"
        i = 9
        for fp in listdir(path_jumpstart):
            fpp = f"{path_jumpstart}/{fp}"
            fpd = f"{path_jumpstart}/{i}{fp}"
            copyfile(fpp, fpd)
            i -= 1

        # rename "jump loop" to be alphabetically last
        path_jumploop = f"{path}/Jump Loop"
        path_jumpstart = f"{path}/Jump Start"
        i = 1
        for fp in listdir(path_jumploop):
            fpp = f"{path_jumploop}/{fp}"
            fpd = f"{path_jumpstart}/{i}{fp}"
            rename(fpp, fpd)
            # i -= 1

        path_healed = f"{path}/Healed"
        rename(path_jumpstart, path_healed)
    else:
        path_jumploop = f"{path}/Casting Spells"
        path_jumpstart = f"{path}/Healed"
        rename(path_jumploop, path_jumpstart)

    print("Done: " + path)


def rename_folders():
    for folder in constants.enemy_folders:
        if "Fallen_Angels" in folder:
            for subfolder in listdir(folder):
                if "01" in subfolder:
                    path = f"{folder}/{subfolder}/PNG Sequences"
                    if "Idle Blink" not in listdir(path):
                        # print(path)
                        rename(path + "/Idle Blinking", path + "/Idle Blink")
                    if "Attacking" not in listdir(path):
                        rename(path + "/Slashing", path + "/Attacking")
                    print("Done with: " + path)


def mirror_images():
    for folder in constants.enemy_folders:
        if "" in folder:
            for subfolder in listdir(folder):
                if "" in subfolder:
                    path = f"{folder}/{subfolder}/PNG Sequences"
                    for frameset in listdir(path):
                        frame_paths = f"{path}/{frameset}"
                        for frame_path in listdir(frame_paths):
                            mirror_image(f"{frame_paths}/{frame_path}")
                        print("Done with: " + frame_paths)


def mirror_image(path):
    # print(path)
    frame = Image.open(path)
    frame = ImageOps.mirror(frame)
    frame.save(path)


def from_initial_to_usable():
    remove_useless_folders()
    rename_folders()
    resize_frames()
    mirror_images()
    gifize_frames()
    rename_healing()
    rename_healed()
