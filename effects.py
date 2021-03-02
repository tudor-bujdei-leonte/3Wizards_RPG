from constants import *


class Effect():
    """
    Defines the visual behaviour of one instance of buff/debuff
    """

    def __init__(self, entity, name, perm=False):
        """
        Creates the visuals of one effect right above the healthbar and after
        existing effects
        """
        self.name = name
        self.entity = entity

        # can be made impossible to remove, functionality not implemented
        self.permanent = perm

        x_a = 30 * len(entity.effects)

        self.image = PhotoImage(
            file=f"{objects_folder}/simple/effects/{name}.gif")
        self.tag = entity.canvas.create_image(
            (entity.healthbar_coords[0][0] + 15 + x_a,
             entity.healthbar_coords[0][1] - 20),
            image=self.image
        )
        entity.canvas.tag_raise(self.tag)

    def remove(self, idx):
        """
        Removes itself from the canvas and rearranges parent effects to fill
        its place
        """
        self.entity.canvas.delete(self.tag)

        x = self.entity.healthbar_coords[0][0] + 15
        y = self.entity.healthbar_coords[0][1] - 20
        for i in range(len(self.entity.effects)):
            if i != idx:
                self.entity.canvas.coords(
                    self.entity.effects[i].tag,
                    x, y
                )
                x += 30
