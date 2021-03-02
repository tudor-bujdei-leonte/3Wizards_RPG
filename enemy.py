from constants import *
from effects import Effect


class Enemy():
    """
    Defines one "enemy" entity and their actions.
    """
    animation_states = ["Idle", "Idle Blink",
                        "Attacking", "Hurt", "Dying",
                        "Walking", "Healed", "Healing"]

    def __init__(self, canvas, type="random", skin="random",
                 x=500, y=500,
                 scale_factor=1, current_hp=100):
        """
        Loads all necessary animations and stats.
        Type and skin are for testing and development.
        All possible enemies have 3 skins, except for the Golem,
        who has 6.
        """
        self.canvas = canvas

        self.animation_sets = {}
        self.frames_count = {}

        self.current_frame = -1
        self.current_state = "Idle"
        self.current_image = 0

        # gets/sets the type of enemy
        if type == "random":
            type = choice(enemy_types)
        elif type == "Golem":
            type += f"_{choice([1, 2])}"
        if type in ["Golem_1", "Golem_2"]:
            self.name = "Golem"
        else:
            self.name = type

        resources_folder = f"{current_path}/resources/entities/{type}"
        if skin == "random" or skin == "":
            skin = choice(listdir(resources_folder))
        elif skin in [1, 2, 3]:
            skin = f"{self.name}_0{skin}"

        # for loaded game purposes, saves the current %hp of the entity
        self.current_health = current_hp
        self.load_stats(scale_factor)

        # can start in one of two states, the second is only used for testing
        self.start_walking(canvas, x, y)
        # self.start_idle(canvas, x, y)

        # measures the time that it takes to load the entity animations.
        # Not useful outside testing but helpful as a log since the player
        # doesn't normally check terminal while playing.
        time_s = perf_counter()
        pngs_folder = f"{resources_folder}/{skin}/PNG Sequences"
        self.load_animations(pngs_folder)
        print(perf_counter() - time_s)
        self.effects = []

    def load_stats(self, scale_factor):
        """
        Loads the stats from the folder and adjusts them according to current
        scaling and starting hp (if on a loaded game). Also initialises
        healthbar variables, but this will be finished only when walking ends.
        """
        # stats
        with open("stats.txt", "r") as file:
            stats = [line for line in file.readlines() if self.name in line][0]
            stats = stats.split("|")
            self.attack_power = int(int(stats[1]) * scale_factor)
            self.defence = int(int(stats[2]) * scale_factor)
            self.max_health = int(int(stats[3]) * scale_factor)

        self.current_health = self.max_health * (self.current_health / 100)
        self.effects = []
        self.is_dead = False

        # canvas id
        self.idd = 0

        # healthbar
        self.coords = [0, 0]
        self.healthbar_idd = [0, 0]
        self.healthbar_coords = [0, 0]
        self.hit_timer = 0
        self.hit_tag = -1
        self.heal_timer = 0
        self.heal_tag = 0

    def load_animations(self, pngs_folder):
        """
        Loads all animations from resources. Loading times are quite long,
        but loading frames during frame_change is incomparably worse.
        """
        for animation_name in self.animation_states:
            animation_path = f"{pngs_folder}/{animation_name}"
            animation_set = []
            for frame_path in listdir(animation_path):
                new_frame = PhotoImage(file=f"{animation_path}/{frame_path}")
                animation_set.append(new_frame)
            self.animation_sets[animation_name] = animation_set
            self.frames_count[animation_name] = len(animation_set)

    def start_idle(self, canvas, x, y):
        """
        Starts at the appointed position (skips walking)
        """
        self.distance_to_idle = 0

        self.idd = canvas.create_image(x, y)
        canvas.tag_raise(self.idd)
        self.coords = [x, y]

        self.current_frame = -1  # it will be incremented before loading
        self.current_state = "Idle"

        self.create_healthbar(canvas)

    def start_walking(self, canvas, x, y):
        """
        Starts walking from 400 px away from the appointed position. When it
        stops walking, it will create the healthbar.
        """
        self.distance_to_idle = 400
        x += self.distance_to_idle

        self.idd = canvas.create_image(x, y)
        canvas.tag_raise(self.idd)
        self.coords = [x, y]

        self.current_frame = -1  # it will be incremented first
        self.current_state = "Walking"

    def change_frame(self, canvas):
        """
        Moves to the next frame for the entity
        """
        self.current_frame += 1
        if self.current_frame == self.frames_count[self.current_state]:
            # when it ends an animation set it will get the next one
            if self.current_state == "Idle":
                # has a chance to blink after idle
                x = randint(1, 3)
                if x == 1:
                    self.current_state = "Idle Blink"
            elif self.current_state == "Idle Blink":
                self.current_state = "Idle"
            elif self.current_state == "Hurt":
                self.current_state = "Idle"
            elif self.current_state == "Dying":
                self.remove(canvas)
            elif self.current_state == "Attacking":
                self.current_state = "Idle"
                self.finish_attack()
            elif self.current_state == "Jump Start":
                self.current_state = "Jump Loop"
            elif self.current_state == "Jump Loop":
                self.current_state = "Jump Start"
            elif self.current_state == "Throwing":
                self.current_state = "Throwing in The Air"
            elif self.current_state == "Throwing in The Air":
                self.current_state = "Idle"
            elif self.current_state == "Healing":
                self.current_state = "Idle"
                self.target.get_heal(canvas, self.damage)
            elif self.current_state == "Healed":
                self.current_state = "Idle"

            self.current_frame = 0
        elif self.current_frame > self.frames_count[self.current_state]:
            self.current_frame = 0

        self.current_image = self.animation_sets[self.current_state][self.current_frame]
        canvas.itemconfig(self.idd, image=self.current_image)

        if self.current_state == "Walking":
            self.move(canvas, 7)

        # also takes care of floating damage tag movements
        if self.hit_timer:
            self.hit_timer -= 1
            self.canvas.move(self.hit_tag, -1, 0)
            if self.hit_timer == 0:
                self.hit_untag()
        if self.heal_timer:
            self.heal_timer -= 1
            self.canvas.move(self.heal_tag, 1, 0)
            if self.heal_timer == 0:
                self.heal_untag()

    def move(self, canvas, distance):
        """
        Moves the entity through the canvas and becomes idle when it finishes.
        """
        canvas.move(self.idd, -distance, 0)
        self.distance_to_idle -= distance
        if self.distance_to_idle <= 0:
            self.current_frame = 0
            self.current_state = "Idle"
            self.coords = canvas.coords(self.idd)
            self.create_healthbar(canvas)

    def create_healthbar(self, canvas):
        """
        Creates the healthbar as 2 overlapping rectangles - one for the
        outline, one for the fill
        """
        self.healthbar_coords[0] = [self.coords[0] - 100,
                                    self.coords[1] - 180,
                                    self.coords[0] + 100,
                                    self.coords[1] - 150]
        if self.name == "Wraith":
            self.healthbar_coords[0][1] -= 50
            self.healthbar_coords[0][3] -= 50

        self.healthbar_idd[0] = canvas.create_rectangle(
            self.healthbar_coords[0],
            outline="green"
        )
        self.healthbar_idd[1] = canvas.create_rectangle(
            self.healthbar_coords[0],
            fill="green"
        )
        canvas.tag_raise(self.idd)

        self.healthbar_coords[1] = copy(self.healthbar_coords[0])
        self.health_update(canvas)

    def health_update(self, canvas):
        """
        Updates the visuals of the healthbar to match the current hp.
        """
        self.healthbar_coords[1][2] = self.healthbar_coords[1][0]
        self.healthbar_coords[1][2] += int(
            (self.current_health/self.max_health) * 200)

        canvas.coords(self.healthbar_idd[1], self.healthbar_coords[1])

    def hit(self, canvas, enemy_attack):
        """
        Receives a damage hit.
        """
        # changes the damage multiplier according to the current defence
        # effects
        mul = 1
        names = [self.effects[i].name for i in range(len(self.effects))]
        if "defence buff" in names:
            mul -= 0.5
            idx = names.index("defence buff")
            self.effects[idx].remove(idx)
            self.effects.pop(idx)
        if "defence break" in names:
            mul += 0.5
            idx = names.index("defence break")
            self.effects[idx].remove(idx)
            self.effects.pop(idx)
        # damage formula
        damage = int(mul * (enemy_attack + 10) / self.defence)

        # visual feedback of the hit
        self.current_frame = 0
        self.current_state = "Hurt"
        self.current_health -= damage
        if self.current_health <= 0:
            self.current_health = 0
            self.die(canvas)
        self.health_update(canvas)

        # adds to the current hit tag damage if hit in quick succession
        if self.hit_tag != -1:
            damage += int(self.canvas.itemcget(self.hit_tag, "text")[2:])
            self.hit_untag()
        # else creates the tag
        self.hit_tag = canvas.create_text(
            (self.healthbar_coords[0][0] + self.healthbar_coords[0][2])/2 + 70,
            (self.healthbar_coords[0][1] + self.healthbar_coords[0][3])/2,
            text=f"- {damage}",
            font=("Arial", 20),
            fill="red"
        )
        self.hit_timer = 15

        # this will stop the canvas for the duration
        # canvas.after(3000, self.hit_untag(canvas))

    def hit_untag(self):
        """
        Removes the hit tag when it finishes animating
        """
        if self.hit_tag == -1:
            return
        self.canvas.delete(self.hit_tag)
        self.hit_tag = -1

    def die(self, canvas):
        """
        Removes own tags and effects upon death
        """
        self.current_frame = 0
        self.current_state = "Dying"
        while len(self.effects):
            self.effects[0].remove(0)
            self.effects.pop(0)
        self.hit_untag()
        self.heal_untag()

    def remove(self, canvas):
        """
        After die() animation has finished, removes self from the canvas
        and sets is_dead for the gamecanvas to make relevant updates
        """
        canvas.delete(self.healthbar_idd[0])
        canvas.delete(self.healthbar_idd[1])
        canvas.delete(self.idd)
        self.is_dead = True

    def attack(self, canvas, allies, enemies):
        """
        Initiates an attack
        """
        # stun effect processing
        names = [effect.name for effect in self.effects]
        if "stun" in names:
            idx = names.index("stun")
            self.effects[idx].remove(idx)
            self.effects.pop(idx)
            return

        # cheat-crash proofing
        if len(allies) == 0:
            return

        # selects a target and sets the attack start animation
        self.target = allies[0]
        self.current_frame = 0
        self.current_state = "Attacking"

    def finish_attack(self):
        """
        Stops attacking and sends the damage information to the target
        """
        # effect-dependent multiplier
        mul = 1
        names = [self.effects[i].name for i in range(len(self.effects))]
        if "attack buff" in names:
            mul += 0.5
            idx = names.index("attack buff")
            self.effects[idx].remove(idx)
            self.effects.pop(idx)
        if "attack break" in names:
            mul -= 0.5
            idx = names.index("attack break")
            self.effects[idx].remove(idx)
            self.effects.pop(idx)
        # attack formula
        new_attack = int(mul * self.attack_power)

        # sends the damage to the enemy
        self.target.hit(self.canvas, new_attack)

    def heal(self, canvas, allies, enemies):
        """
        Defence-based healing to the lowest hp ratio ally
        """
        # stun effect processing
        names = [effect.name for effect in self.effects]
        if "stun" in names:
            idx = names.index("stun")
            self.effects[idx].remove(idx)
            self.effects.pop(idx)
            return

        # finds ally with lowest hp ratio
        min_hp = self.current_health / self.max_health
        min_enemy = self
        for enemy in enemies:
            if enemy.current_health / enemy.max_health < min_hp:
                min_hp = enemy.current_health / enemy.max_health
                min_enemy = enemy

        # sets them as a target, sends the healing data at the end of animation
        self.target = min_enemy
        self.damage = int(10 + self.defence)
        self.current_frame = 0
        self.current_state = "Healing"

    def get_heal(self, canvas, damage):
        """
        Receives a certain amount of healing
        """
        tag_colour = "lightgreen"
        tag_text = f"+ {damage}"

        self.current_frame = 0
        self.current_state = "Healed"

        # heal break effect processing
        names = [effect.name for effect in self.effects]
        if "heal break" in names:
            damage = 0
            tag_colour = "red"
            tag_text = "+ 0"
            self.current_state = "Idle"

            idx = names.index("heal break")
            self.effects[idx].remove(idx)
            self.effects.pop(idx)

        # health update, internal and visual
        self.current_health += damage
        if self.current_health > self.max_health:
            self.current_health = self.max_health
        self.health_update(canvas)

        # creates the heal tag
        self.heal_untag()
        self.heal_tag = canvas.create_text(
            (self.healthbar_coords[0][0] + self.healthbar_coords[0][2])/2 - 70,
            (self.healthbar_coords[0][1] + self.healthbar_coords[0][3])/2,
            text=tag_text,
            font=("Arial", 20),
            fill=tag_colour
        )
        self.heal_timer = 15

    def heal_untag(self):
        """
        Removes the heal tag when heal_timer ends
        """
        if self.heal_tag == -1:
            return
        self.canvas.delete(self.heal_tag)
        self.heal_tag = -1


class Enemy_old():
    """
    Deprecated class, different approach
    """
    # animation_sets = {}
    # frames_count = {}
    # animation_states = ["Idle", "Walking", "Hurt", "Dying"]

    idle_frameset = []
    idle_frame_count = 0

    walking_frameset = []
    walking_frame_count = 0

    hurt_frameset = []
    hurt_frame_count = 0

    dying_frameset = []
    dying_frame_count = 0

    current_frame = 0
    current_state = "Idle"
    current_image = 0

    health = 100
    effects = []

    def __init__(self, canvas, type="random", x=500, y=500):
        if type == "random":
            type = choice(enemy_types)
        # elif sel == "choice": type = type
        if type in ["Golem_1", "Golem_2"]:
            self.name = "Golem"
        else:
            self.name = type

        self.idd = canvas.create_image(x, y)

        resources_folder = f"{current_path}/resources/entities/{type}"
        skin = choice(listdir(resources_folder))
        pngs_folder = f"{resources_folder}/{skin}/PNG Sequences"

        time_s = perf_counter()

        self.load_animations(pngs_folder)
        # for animation_name in self.animation_states:
        #     # animation_name = "Idle"
        #     animation_folder = f"{pngs_folder}/{animation_name}"
        #     animation = [
        #         f"{animation_folder}/{d}"for d in listdir(animation_folder)]

        #     self.animation_sets[animation_name] = animation
        #     self.frames_count[animation_name] = len(animation)

        print(perf_counter() - time_s)

        self.current_frame = 0
        self.current_state = "Idle"
        # self.current_image = self.id[0]
        # canvas.itemconfig(self.idd, image=self.current_image)

        # self.aux = canvas.create_image(x + 100, y + 100)
        # self.aux_image = PhotoImage(file=self.animation_sets["Idle"][1])
        # canvas.itemconfig(self.aux, image=self.aux_image)
        # print(self.name)

        self.health = 100
        self.effects = []

    def change_frame(self, canvas):
        if self.current_state == "Idle":
            self.current_frame += 1
            if self.current_frame >= self.idle_frame_count:
                self.current_frame = 0
            self.current_image = self.idle_frameset[self.current_frame]
        elif self.current_state == "Walking":
            self.current_frame += 1
            if self.current_frame >= self.walking_frame_count:
                self.current_frame = 0
            self.current_image = self.walking_frameset[self.current_frame]
        elif self.current_state == "Hurt":
            self.current_frame += 1
            if self.current_frame >= self.hurt_frame_count:
                self.current_frame = 0
            self.current_image = self.hurt_frameset[self.current_frame]
        elif self.current_state == "Dying":
            self.current_frame += 1
            if self.current_frame >= self.dying_frame_count:
                self.current_frame = 0
            self.current_image = self.dying_frameset[self.current_frame]
            # print(0)
        canvas.itemconfig(self.idd, image=self.current_image)

    def load_animations(self, pngs_folder):
        animation_states = ["Idle", "Walking", "Hurt", "Dying"]
        # animation_sets = [self.idle_frameset, self.walking_frameset,
        #                   self.hurt_frameset, self.dying_frameset]
        # frame_counts = [self.idle_frame_count, self.walking_frame_count,
        #                 self.hurt_frame_count, self.walking_frame_count]
        animation_sets = []
        frame_counts = []

        for i in range(len(animation_states)):
            animation_name = animation_states[i]
            animation_folder = f"{pngs_folder}/{animation_name}"
            # print(animation_folder)
            # animation = []
            # for d in listdir(animation_folder):
            #     new_image = PhotoImage(file=f"{animation_folder}/{d}")
            #     standard_width = int(520 / new_image.width())
            #     standard_height = int(420 / new_image.height())
            #     print(standard_width, standard_height)
            #     animation.append(new_image.zoom(
            #         standard_width, standard_height))
            animation = [PhotoImage(file=f"{animation_folder}/{d}")
                         for d in listdir(animation_folder) if d[-3:] == "gif"]
            animation_sets.append(animation)
            frame_counts.append(len(animation))

        self.idle_frameset = animation_sets[0]
        self.idle_frame_count = frame_counts[0]
        print(frame_counts)
        self.walking_frameset = animation_sets[1]
        self.walking_frame_count = frame_counts[1]
        self.hurt_frameset = animation_sets[2]
        self.hurt_frame_count = frame_counts[2]
        self.dying_frameset = animation_sets[3]
        self.dying_frame_count = frame_counts[3]

        return [animation_sets, frame_counts]

        # animation_name = "Idle"
        # animation_folder = f"{pngs_folder}/{animation_name}"
        # animation = [PhotoImage(file=f"{animation_folder}/{d}")
        #              for d in listdir(animation_folder)]
        # self.idle_frameset = animation
        # self.idle_frame_count = len(animation)

        # animation_name = "Walking"
        # animation_folder = f"{pngs_folder}/{animation_name}"
        # animation = [
        #     f"{animation_folder}/{d}"for d in listdir(animation_folder)]
        # self.walking_frameset = animation
        # self.walking_frame_count = len(animation)

        # animation_name = "Hurt"
        # animation_folder = f"{pngs_folder}/{animation_name}"
        # animation = [
        #     f"{animation_folder}/{d}"for d in listdir(animation_folder)]
        # self.hurt_frameset = animation
        # self.hurt_frame_count = len(animation)

        # animation_name = "Dying"
        # animation_folder = f"{pngs_folder}/{animation_name}"
        # animation = [
        #     f"{animation_folder}/{d}"for d in listdir(animation_folder)]
        # self.dying_frameset = animation
        # self.dying_frame_count = len(animation)
