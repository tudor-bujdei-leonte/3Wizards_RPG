from constants import *
from effects import Effect
from enemy import Enemy


class Ally():
    """
    Defines one "ally" entity (wizard) and their actions.
    """
    animation_states = ["Attacking", "Dying",
                        "Hurt", "Walking", "Idle",
                        "Healing", "Healed", "Special"]

    def __init__(self, canvas, type="fire", x=500, y=500,
                 scale_factor=1, current_hp=100):
        """
        Loads all necessary animations and stats
        """
        self.canvas = canvas

        self.animation_sets = {}
        self.frames_count = {}

        self.current_frame = -1
        self.current_state = "Idle"
        self.current_image = 0

        self.name = type

        # for loaded game purposes, saves the current %hp of the entity
        self.current_health = current_hp
        self.load_stats(scale_factor)

        # can be loaded in one of two states. Second is only used for testing.
        self.start_walking(canvas, x, y)
        # self.start_idle(canvas, x, y)

        # measures the time that it takes to load the entity animations.
        # Not useful outside testing but helpful as a log since the player
        # doesn't normally check terminal while playing.
        time_s = perf_counter()
        pngs_folder = f"{current_path}/resources/entities/wizard/wizard_{type}"
        self.load_animations(pngs_folder)
        print(perf_counter() - time_s)

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
            self.attack_power = int(int(stats[1]) / scale_factor)
            self.defence = int(int(stats[2]) / scale_factor)
            self.max_health = int(int(stats[3]) / scale_factor)

        self.current_health = int(
            self.max_health*(self.current_health / 100))
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
        x -= self.distance_to_idle

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
            if self.current_state == "Hurt":
                self.current_state = "Idle"
            elif self.current_state == "Attacking":
                self.current_state = "Idle"
                # attacking is a 3-step process:
                # Attack animation, damage, damage animation
                self.finish_attack()
            elif self.current_state == "Dying":
                self.remove(canvas)
            elif self.current_state == "Healing":
                self.current_state = "Idle"
                # same as attacking
                self.target.get_heal(canvas, self.damage)
            elif self.current_state == "Healed":
                self.current_state = "Idle"
            elif self.current_state == "Special":
                self.current_state = "Idle"

            self.current_frame = 0
        elif self.current_frame > self.frames_count[self.current_state]:
            self.current_frame = 0

        self.current_image = self.animation_sets[self.current_state][self.current_frame]
        canvas.itemconfig(self.idd, image=self.current_image)

        if self.current_state == "Walking":
            self.move(canvas, 10)

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
        canvas.move(self.idd, distance, 0)
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
        self.healthbar_coords[0] = [self.coords[0] - 120,
                                    self.coords[1] - 180,
                                    self.coords[0] + 80,
                                    self.coords[1] - 150]

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
        # else, creates the tag
        self.hit_tag = canvas.create_text(
            (self.healthbar_coords[0][0] + self.healthbar_coords[0][2])/2 + 70,
            (self.healthbar_coords[0][1] + self.healthbar_coords[0][3])/2,
            text=f"- {damage}",
            font=("Arial", 20),
            fill="red"
        )
        self.hit_timer = 15  # will persist for 15 frames

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

    def remove(self, canvas):
        """
        After die() animation has finished, removes self from the canvas
        and sets is_dead for the gamecanvas to make relevant updates
        """
        self.hit_untag()
        self.heal_untag()
        canvas.delete(self.healthbar_idd[0])
        canvas.delete(self.healthbar_idd[1])
        canvas.delete(self.idd)
        self.is_dead = True

    def attack(self, canvas, allies, enemies):
        """
        Initiates an attack
        """
        # cheat-crash proofing
        if len(enemies) == 0:
            return

        # seletcs a target and sets the attack start animation
        self.target = enemies[0]
        self.current_frame = 0
        self.current_state = "Attacking"

        # chance-based effects depending on type
        # magic applies the effect at the end of animation, otherwise an
        # animation clash occurs and only the heal is applied
        if uniform(0, 1) > 0.2:
            if self.name == "fire":
                self.target.effects.append(
                    Effect(
                        self.target,
                        "heal break"
                    )
                )
            if self.name == "ice":
                self.target.effects.append(
                    Effect(
                        self.target,
                        "stun"
                    )
                )

        # canvas.move(self.idd, 137, 5)

    def special_attack(self, parent, allies, enemies):
        """
        Deals a special, unique attack
        """
        if self.name == "ice":
            # hits before applying the effect so that it can only apply one
            # defence break effect at a given time. Testing showed it to be OP
            # otherwise.
            for enemy in enemies:
                enemy.hit(self.canvas, 1)
                enemy.effects.append(Effect(enemy, "defence break"))
                enemy.effects.append(Effect(enemy, "attack break"))

            max_attack = self.attack_power
            max_ally = self
            for ally in allies:
                if max_attack < ally.attack_power:
                    max_attack = ally.attack_power
                    max_ally = ally
            max_ally.effects.append(Effect(max_ally, "attack buff"))
            max_ally.effects.append(Effect(max_ally, "attack buff"))
        elif self.name == "fire":
            # attacks all enemies once, then attacks a random enemy with an
            # attack-buffed hit
            for enemy in enemies:
                self.target = enemy
                self.finish_attack()

            self.effects.append(Effect(self, "attack buff"))
            self.target = choice(enemies)
            self.finish_attack()
        elif self.name == "magic":
            # slight heal and AoE defence buff
            for ally in allies:
                ally.effects.append(Effect(ally, "defence buff"))
                ally.get_heal(self.canvas, self.max_health * 0.1)
        self.current_state = "Special"
        self.current_frame = 0

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

        # magic normal attack special effect
        if self.name == "magic":
            self.get_heal(self.canvas, int(self.max_health / 4))

    def heal(self, canvas, allies, enemies):
        """
        Defence-based healing to the lowest hp ratio ally
        """
        # finds ally with lowest hp ratio
        min_hp = self.current_health / self.max_health
        min_ally = self
        for ally in allies:
            if ally.current_health / ally.max_health < min_hp:
                min_hp = ally.current_health / ally.max_health
                min_ally = ally

        # sets them as a target, sends the healing data at the end of animation
        self.target = min_ally
        self.damage = int(10 + self.defence)
        self.current_frame = 0
        self.current_state = "Healing"

    def get_heal(self, canvas, damage):
        """
        Receives a certain amount of healing
        """
        # health update, internal and visual
        self.current_health += damage
        if self.current_health > self.max_health:
            self.current_health = self.max_health
        self.health_update(canvas)
        self.current_frame = 0
        self.current_state = "Healed"

        # creates the heal tag
        self.heal_untag()
        self.heal_tag = canvas.create_text(
            (self.healthbar_coords[0][0] + self.healthbar_coords[0][2])/2 - 70,
            (self.healthbar_coords[0][1] + self.healthbar_coords[0][3])/2,
            text=f"+ {damage}",
            font=("Arial", 20),
            fill="lightgreen"
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
