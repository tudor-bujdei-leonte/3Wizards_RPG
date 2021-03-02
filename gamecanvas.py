from constants import *
from ally import Ally
from enemy import Enemy
from canvasbutton import CanvasButton
from canvasmenu import CanvasMenu


class GameCanvas():
    """
    Defines the canvas for actual gameplay
    """

    def __init__(self, parent, cwidth, cheight, scale_factor=1, money=0, spd=1, user="Guest"):
        """
        Prepares the canvas. Fight must be started separately.
        """
        print("Booting game...")
        self.parent = parent
        self.root = parent.root
        self.user = user

        # yes/no messages
        self.areyousure = -1

        # visual implementation
        self.canvas_width = cwidth
        self.canvas_height = cheight
        self.canvas = Canvas(
            self.root,
            width=self.canvas_width,
            height=self.canvas_height,
            bg="black",
            bd=0,
            highlightthickness=0
        )
        self.background_image = PhotoImage(
            file=f"{objects_folder}/paper background.gif")
        self.background = self.canvas.create_image(
            0, 0,
            image=self.background_image,
            anchor="nw"
        )
        self.canvas.tag_lower(self.background)
        self.canvas.pack()

        # a crude FPS counter
        self.fps_counter = self.canvas.create_text(
            0, self.canvas_height,
            fill="black",
            anchor="sw"
        )

        # game works on a delta time basis
        self.last_tick = perf_counter()
        self.second_tick = 0
        self.paused = False
        self.speed_multiplier = spd  # can be increased up to x4
        self.keep_running = True  # becomes false to stop the fight

        self.enemies = []
        self.allies = []
        self.scale_factor = scale_factor  # scales 1.2^x
        self.turn = 1

        # self.canvas.bind("<Escape>", lambda x: self.root.destroy())
        self.canvas.focus_set()

        self.buttons = {}
        self.start_queue()

        # this will block all visual updates. Could wait for everyone_idle()
        # but doesn't need to and in fact becomes annoying if you can't
        # increase the speed multiplier while waiting.
        # self.canvas.after(5000, self.create_menu)

        self.create_menu()

        # creates the score tag and values
        self.create_money(money)

    def start_game(self, loaded=False):
        """
        Creates an instance of fight and loops it until win or loss.
        """
        self.root.lift(self.canvas)

        # skips fight initialisation if it has already been done (i.e. load
        # game)
        if not loaded:
            self.init_fight()

        # only creates cheat buttons after walking ends
        self.did_cheats = False

        # this way of counting frames is unrealistic but it's fun to see it
        # anyway
        frame_count = 0
        current_frame = perf_counter()
        while self.keep_running:  # stops at win/loss
            frame_count += 1
            if perf_counter() - current_frame > 1:
                self.update_frame(frame_count)  # updates once per second
                frame_count = 0
                current_frame = perf_counter()

            # refreshes the screen
            # must be done outside the gameloop if statement, otherwise the
            # pause menu wouldn't update
            self.root.update()

            if not self.paused:
                self.gameloop()

    def load_game(self):
        """
        Loads an instance of fight from the savefile.
        """
        self.create_progressbar()
        i = 0.1

        with open("savefile.txt") as file:
            lines = file.readlines()  # reads all lines
            for line in lines:
                line = line.strip()
                attributes = line.split("|")  # splits them into words

                # score stat
                if attributes[0] == "money":
                    self.money = int(attributes[1])
                # current wave progress is log1.2(x)
                elif attributes[0] == "scale_factor":
                    self.scale_factor = float(attributes[1])
                # creates an ally with the specified hp and type
                elif attributes[0] == "ally":
                    self.create_ally(
                        type=attributes[1],
                        current_hp=float(attributes[2])
                    )
                    self.fill_progressbar(i)
                    i += 0.1
                # creates an enemy with the specified hp and type
                elif attributes[0] == "enemy":
                    self.create_enemy(
                        type=attributes[1],
                        current_hp=float(attributes[2])
                    )
                    self.fill_progressbar(i)
                    i += 0.1

        # due to how the game is saved, i will end up at most 0.9 and at least
        # 0.4
        self.fill_progressbar(1)
        sleep(0.05)  # feels more natural a transition
        self.remove_progressbar()

        self.q.append(choice(self.allies))  # random ally turn in queue
        self.q.append(choice(self.enemies))  # random enemy turn 2

        self.update_money()  # visual start of the score at the loaded value

    def gameloop(self):
        """
        Processes the current frame.
        """

        # if it is the user's turn, waits for input
        if self.turn == 1:
            pass
        # else the enemy attacks
        elif self.turn == -1:
            self.enemy_attack()

        # if someone won the game, end it
        if self.check_win_conditions():
            self.reset_game()
        # otherwise check if the queue needs filling
        else:
            if len(self.q) < 3:
                self.q.append(self.choose_q())
                # and update its images()
                self.update_next()

        self.check_dead()
        self.flip_turn()

        # delta time implementation
        # wizards update every 0.1s and enemies 0.07
        # I did not find better free animations for the wizards
        # uses two counters: one for the framerate, one for frame updates
        current_tick = perf_counter()
        tick_difference = current_tick - self.last_tick
        if tick_difference > 0.01 / self.speed_multiplier:
            self.second_tick += 1
            self.last_tick = current_tick
            if self.second_tick % 7 == 0:
                for enemy in self.enemies:
                    enemy.change_frame(self.canvas)
            if self.second_tick % 10 == 0:
                for ally in self.allies:
                    ally.change_frame(self.canvas)
            # also updates the score floating tag
            if self.second_tick % 7 == 0:
                if self.money_counter != 0:
                    self.canvas.move(self.money_tag_new, 1, 0)
                    self.money_counter -= 1
                    if self.money_counter == 0:
                        self.canvas.delete(self.money_tag_new)
                        self.money_tag_new = -1

            if self.second_tick > 70:
                self.second_tick = 0

        # creates cheat buttons when the entities have stopped walking
        if not self.did_cheats:
            if self.everyone_idle():
                self.create_cheat_buttons()
                self.hide_cheats()
                self.did_cheats = True

                # binds the cheat button
                self.canvas.bind(
                    "<c>",
                    self.toggle_cheats
                )

    def toggle_cheats(self, event):
        """
        Shows or hides cheats
        """
        if self.cheats_hidden:
            self.show_cheats()
        else:
            self.hide_cheats()

    def show_cheats(self):
        """
        Makes all cheat buttons visible
        """
        for ally in self.allies:
            for button in self.buttons[ally]:
                button.show()
        for enemy in self.enemies:
            for button in self.buttons[enemy]:
                button.show()
        self.cheats_hidden = False

    def init_fight(self):
        """
        Starts an instance of fight if the game is not loaded from the
        external file
        """
        self.progressbars = []
        self.create_progressbar()

        i = 0.1
        # creates the three wizards
        for t in ["magic", "ice", "fire"]:
            print(f"Creating {t} wizard...")
            self.create_ally(type=t)
            self.fill_progressbar(i)
            i += 0.1
        self.q.append(choice(self.allies))

        # creates 3 random enemies
        print("Creating random enemies...")
        self.fill_progressbar(i)
        i += 0.1
        for t in range(3):
            self.create_enemy()
            self.fill_progressbar(i)
            i += 0.1
        self.q.append(choice(self.enemies))

        self.remove_progressbar()

    def start_queue(self):
        """
        Initialises the turn queue
        """
        self.q = list()
        self.q_images = [[0, PhotoImage(), PhotoImage()],
                         [0, PhotoImage(), PhotoImage()]]
        self.q_images[0][0] = (self.canvas.create_image(
            1750, 1000,
            image=self.q_images[0][1]
        ))
        self.q_images[1][0] = (self.canvas.create_image(
            1870, 1000,
            image=self.q_images[1][1]
        ))

    def create_menu(self):
        """
        Creates the battle menu
        """
        self.menubuttons = {}

        self.money_background = [PhotoImage(
            file=f"{objects_folder}/simple/buttons/button_default.gif"
        )]
        self.money_background.append(self.canvas.create_image(
            80, 30,
            image=self.money_background[0]
        ))

        self.menubuttons["Pause"] = CanvasButton(
            self.canvas,
            event=lambda self=self: self.pause_canvas(),
            text="Pause",
            font=("Arial Bold", 50),
            x=180, y=1020,
            scale_factor=2
        )
        # escape shortcut for pausing
        self.canvas.bind("<Escape>", lambda x, self=self: self.pause_canvas())

        self.menubuttons["Attack"] = CanvasButton(
            self.canvas,
            event=lambda self=self: self.ally_attack(),
            text="Attack",
            font=("Arial Bold", 50),
            x=500, y=1020,
            scale_factor=2
        )

        self.menubuttons["Heal"] = CanvasButton(
            self.canvas,
            event=lambda self=self: self.ally_heal(),
            text="Heal",
            font=("Arial Bold", 50),
            x=820, y=1020,
            scale_factor=2
        )

        self.menubuttons["Special"] = CanvasButton(
            self.canvas,
            event=lambda self=self: self.ally_special(),
            text="Special",
            font=("Arial Bold", 50),
            x=1140, y=1020,
            scale_factor=2
        )

        self.menubuttons["Speed"] = CanvasButton(
            self.canvas,
            event=lambda self=self: self.toggle_speed(),
            text=f"Spd x{self.speed_multiplier}",
            font=("Arial Bold", 50),
            x=1460, y=1020,
            scale_factor=2
        )

    def toggle_speed(self):
        """
        Toggles the animation speed multiplier between x1, x2 and x4
        """
        self.speed_multiplier *= 2
        if self.speed_multiplier > 4:
            self.speed_multiplier = 1

        # visual update
        self.menubuttons["Speed"].change_text(
            self.canvas,
            f"Spd x{self.speed_multiplier}"
        )

    def ally_special(self):
        """
        User special attack. Internally presses the special cheat button for
        the entity.
        """
        if self.turn != 1 or not self.everyone_idle():
            return
        self.press_cheat_button(self.q[0], "Special")
        self.q.pop(0)

    def ally_heal(self):
        """
        User heal. Internally presses the heal cheat button for the
        entity.
        """
        if self.turn != 1 or not self.everyone_idle():
            return
        self.press_cheat_button(self.q[0], "Healing")
        self.q.pop(0)

    def ally_attack(self):
        """
        User attack. Internally presses the attack cheat button for the
        entity.
        """
        if self.turn != 1 or not self.everyone_idle():
            return
        self.press_cheat_button(self.q[0], "Attacking")
        self.q.pop(0)

    def pause_canvas(self):
        """
        Pauses the canvas
        """
        if self.paused:
            return
        self.paused = True
        self.create_paused_menu()

    def create_paused_menu(self):
        """
        Creates the special on-pause menu
        """
        self.paused_menu = CanvasMenu(
            self.canvas,
            x=int(self.canvas_width / 2),
            y=int(self.canvas_height / 2) - 50
        )

        self.menubuttons["Resume"] = CanvasButton(
            self.canvas,
            event=lambda self=self: self.resume_canvas(),
            text="Resume",
            font=("Arial Bold", 65),
            x=int(self.canvas_width / 2),
            y=int(self.canvas_height / 2) - 225,
            scale_factor=3
        )

        self.menubuttons["Save"] = CanvasButton(
            self.canvas,
            event=lambda self=self: self.areyousure_menu(event=self.save_game),
            text="Save",
            font=("Arial Bold", 65),
            x=int(self.canvas_width / 2),
            y=int(self.canvas_height / 2) - 25,
            scale_factor=3
        )

        self.menubuttons["Quit"] = CanvasButton(
            self.canvas,
            event=lambda self=self: self.areyousure_menu(event=self.quit_game),
            text="Quit",
            font=("Arial Bold", 65),
            x=int(self.canvas_width / 2),
            y=int(self.canvas_height / 2) + 175,
            scale_factor=3
        )

    def areyousure_menu(self, message="", event=lambda x: print(0)):
        """
        The confirmation popup for save and quit
        """
        if self.areyousure != -1:
            return

        self.areyousure = CanvasMenu(
            self.canvas,
            text="Are you sure " + message + "?",
            text_style="yesno",
            event=[event, lambda self=self:self.areyousure_no()]
        )

    def areyousure_no(self):
        """
        If the confirmation is rejected, cancels the action
        """
        self.areyousure.destroy()
        self.areyousure = -1

    def save_game(self):
        """
        Updates the savefile with the current data
        """
        if not self.finished_walking():
            return
        savefile = ""
        for item in ["money", "scale_factor", "queue", "ally", "enemy"]:
            s = f"{item}|"
            if item == "money":
                s += str(self.money)
            elif item == "scale_factor":
                s += str(self.scale_factor)
            elif item == "queue":
                for entity in self.q:
                    if isinstance(entity, Ally):
                        s += f"ally_{self.allies.index(entity)}"
                    elif isinstance(entity, Enemy):
                        s += f"enemy_{self.enemies.index(entity)}"
                    s += "|"
                s = s[:-1]
            elif item == "ally":
                for ally in self.allies:
                    s += f"{ally.name}|{100 * ally.current_health/ally.max_health}"
                    s += "\nally|"
                s = s[:-6]
            elif item == "enemy":
                for enemy in self.enemies:
                    s += f"{enemy.name}|{100 * enemy.current_health/enemy.max_health}"
                    s += "\nenemy|"
                s = s[:-7]
            s += "\n"
            savefile += s
        with open("savefile.txt", "w") as file:
            file.write(savefile)

        # removes the confirmation popup
        self.areyousure.destroy()
        # creates a confirmation message
        self.message = CanvasMenu(
            self.canvas,
            text="Saved the game!",
            text_style="ok",
            event=lambda self=self: self.delete_message()
        )

    def delete_message(self, stop_game=False):
        """
        Removes the confirmation message
        """
        self.message.destroy()
        self.areyousure = -1
        if stop_game:
            self.add_leaderboard()
            self.keep_running = False

    def quit_game(self):
        """
        Quits the game
        """
        if not self.finished_walking():
            return
        self.keep_running = False

    def resume_canvas(self):
        """
        Unpauses the canvas and removes the pause menu
        """
        self.paused = False

        self.paused_menu.destroy()

        self.menubuttons["Resume"].destroy(self.canvas)
        self.menubuttons.pop("Resume")

        self.menubuttons["Quit"].destroy(self.canvas)
        self.menubuttons.pop("Quit")

        self.menubuttons["Save"].destroy(self.canvas)
        self.menubuttons.pop("Save")

    def update_next(self):
        """
        Updates the queue images to match the upcoming two entities
        """
        if self.q_images[0][1] != self.q[0].animation_sets["Idle"][0]:
            self.q_images[0][1] = self.q[0].animation_sets["Idle"][0]
            self.q_images[0][2] = self.q_images[0][1].subsample(3)
            self.canvas.itemconfig(
                self.q_images[0][0],
                image=self.q_images[0][2]
            )
        if self.q_images[1][1] != self.q[1].animation_sets["Idle"][0]:
            self.q_images[1][1] = self.q[1].animation_sets["Idle"][0]
            self.q_images[1][2] = self.q_images[1][1].subsample(3)
            self.canvas.itemconfig(
                self.q_images[1][0],
                image=self.q_images[1][2]
            )

    def create_progressbar(self):
        """
        A simple progressbar for then the fight is loading
        """
        self.progressbar = self.canvas.create_rectangle(
            0, 0, self.canvas_width, 100,
            outline="red"
        )
        self.progress = self.canvas.create_rectangle(
            0, 0, 0, 100,
            fill="red"
        )
        self.progress_label = self.canvas.create_text(
            1000, 50,
            text="Loading...",
            font=("Arial", 65),
            fill="#633506"
        )
        self.root.update()

    def fill_progressbar(self, p):
        """
        Fills the progressbar to p
        """
        self.canvas.coords(
            self.progress,
            0, 0, int(p * self.canvas_width), 100
        )
        self.root.update()

    def remove_progressbar(self):
        """
        Removes the progressbar
        """
        self.canvas.delete(self.progressbar)
        self.canvas.delete(self.progress)
        self.canvas.delete(self.progress_label)

    def reset_game(self):
        """
        Resets the game by reinitialising the canvas.
        Can be improved to just reset enemies, allies and queue.
        """
        if self.enemies:
            # creates a confirmation message
            self.message = CanvasMenu(
                self.canvas,
                text="You lost!",
                text_style="ok",
                event=lambda self=self: self.delete_message(stop_game=True)
            )
            return
        self.canvas.destroy()
        self.__init__(self.parent, self.canvas_width,
                      self.canvas_height, self.scale_factor * 1.2,
                      money=self.money, spd=self.speed_multiplier,
                      user=self.user)
        self.init_fight()

        # self.start_game()
        # self.create_cheat_buttons()
        self.did_cheats = False

    def add_leaderboard(self):
        """
        Adds the current user/score to the leaderboard
        """
        with open("leaderboard.txt", "a") as file:
            file.write(f"\n{self.user}|{self.money}")

    def create_entity_buttons(self):
        """
        Creates the cheat buttons for all entities
        """
        i = 1
        for ally in self.allies:
            new_buttons = self.entity_button(ally, 250, i)
            self.buttons[ally] = new_buttons
            i = (i + 1) % 2
        for enemy in self.enemies:
            new_buttons = self.entity_button(enemy, 220, i)
            self.buttons[enemy] = new_buttons
            i = (i + 1) % 2

    def entity_button(self, entity, d, i):
        """
        Creates the cheat buttons for one entity
        """
        new_buttons = []
        [x, y] = self.canvas.coords(entity.idd)
        no_states = len(entity.animation_states)
        phi = (-6) * (pi / 24) + i * (pi)  # - pi / 12)
        for i in range(no_states):
            state = entity.animation_states[i]
            if state in ["Attacking", "Dying", "Hurt", "Healing", "Special"]:
                phi += pi/12
                # if i > 2:
                #     phi += (3*pi / 2)
                [x_n, y_n] = [x + int(d * cos(phi)), y + int(d * sin(phi))]
                new_button = CanvasButton(
                    self.canvas,
                    event=lambda entity=entity, state=state:
                        self.press_cheat_button(
                            entity, state
                        ),
                    text=state,
                    font=("Arial Bold", 20),
                    x=x_n, y=y_n
                )
                new_buttons.append(new_button)
        return new_buttons

    def hide_cheats(self):
        """
        Hides the cheat buttons
        """
        for ally in self.allies:
            for button in self.buttons[ally]:
                button.hide()
        for enemy in self.enemies:
            for button in self.buttons[enemy]:
                button.hide()
        self.cheats_hidden = True

    def press_cheat_button(self, entity, state):
        """
        The activation function for all cheat buttons
        """
        if state == "Attacking":
            entity.attack(self.canvas, self.allies, self.enemies)
        elif state == "Healing":
            entity.heal(self.canvas, self.allies, self.enemies)
        elif state == "Special":
            entity.special_attack(self, self.allies, self.enemies)
        elif state == "Hurt":
            entity.hit(self.canvas, 1000)
        elif state == "Dying":
            entity.die(self.canvas)

    def create_ally(self, type, current_hp=100):
        """
        Creates a new ally entity
        """
        # current_hp is a percentage
        # they have fixed positions
        if len(self.allies) == 0:
            x = 670
            y = 500
        elif len(self.allies) == 1:
            x = 370
            y = 250
        elif len(self.allies) == 2:
            x = 370
            y = 750

        new_ally = Ally(self.canvas, type=type, x=x, y=y,
                        scale_factor=self.scale_factor,
                        current_hp=current_hp)
        self.allies.append(new_ally)

    def create_enemy(self, type="random", skin="random", current_hp=100):
        """
        Creates a new enemy entity
        """
        # current_hp is a percentage
        # they have fixed positions
        if len(self.enemies) == 0:
            x = 1350
            y = 525
        elif len(self.enemies) == 1:
            x = 1550
            y = 275
        elif len(self.enemies) == 2:
            x = 1550
            y = 775

        new_enemy = Enemy(self.canvas, type=type, skin=skin,
                          x=x, y=y, scale_factor=self.scale_factor,
                          current_hp=current_hp)
        self.enemies.append(new_enemy)

    def update_frame(self, frame_count):
        """
        Updates the frame counter
        """
        self.canvas.itemconfig(
            self.fps_counter,
            text=f"FPS: {frame_count}"
        )

    def choose_q(self, exceptions=[]):
        """
        Chooses a random ally or enemy with a 50/50 chance
        """
        return choice([choice(self.enemies), choice(self.allies)])

    def enemy_attack(self):
        """
        Makes the current entity attack if it is an enemy. They will choose to
        either attack the frontmost ally, or to defence-based heal the lowest
        hp enemy. The chance to heal scales with both lowest hp in team and
        with entity defence.
        """
        if self.turn != -1 or not self.everyone_idle() or len(self.q) == 0:
            return

        entity = self.q[0]
        action = "Attacking"

        min_hp = entity.current_health / entity.max_health
        min_enemy = entity
        for enemy in self.enemies:
            if enemy.current_health / entity.max_health < min_hp:
                min_hp = enemy.current_health / entity.max_health
                min_enemy = enemy

        if min_hp < 0.6:
            heal_chance = 1 - min_hp + entity.defence / 10
            if heal_chance > uniform(0, 1):
                action = "Healing"

        self.press_cheat_button(self.q[0], action)
        self.q.pop(0)

    def everyone_idle(self):
        """
        Checks if all enemies and allies are Idle.
        """
        for ally in self.allies:
            if ally.current_state != "Idle":
                return False
        for enemy in self.enemies:
            if "Idle" not in enemy.current_state:
                return False
        return True

    def flip_turn(self):
        """
        Decides which side is currently taking a turn. Deprecated since the
        implementation of self.q.
        """
        if len(self.q) == 0:
            return
        current_entity = self.q[0]
        if isinstance(current_entity, Ally):
            self.turn = 1
        elif isinstance(current_entity, Enemy):
            self.turn = -1

    def check_win_conditions(self):
        """
        Checks if the fight should end. This happens when one side is dead.
        """
        if not self.enemies or not self.allies:
            return True
        return False

    def create_cheat_buttons(self):
        """
        Waits for allies and enemies to finish walking before creating buttons
        """
        if self.everyone_idle():
            self.create_entity_buttons()

    def change_enemy_state(self, enemy_id, state):
        """
        Sets the state of an enemy. Test purposes only.
        """
        self.enemies[enemy_id].current_state = state

    def finished_walking(self):
        """
        A more general instance of everyone_idle(), checks if anybody
        is walking.
        """
        return len(self.buttons)

    def check_dead(self):
        """
        Cleans up memory after kills and adds to score if enemies die.
        """
        for i in range(len(self.allies)):
            if self.allies[i].is_dead:
                for j in range(len(self.q)):
                    while self.allies[i] == self.q[j]:
                        self.q[j] = self.choose_q([self.allies[i]])
                for button in self.buttons[self.allies[i]]:
                    button.destroy(self.canvas)
                self.buttons.pop(self.allies[i])
                self.allies.pop(i)
                return
        for i in range(len(self.enemies)):
            if self.enemies[i].is_dead:
                self.add_money()
                for j in range(len(self.q)):
                    while self.enemies[i] == self.q[j]:
                        self.q[j] = self.choose_q([self.enemies[i]])
                for button in self.buttons[self.enemies[i]]:
                    button.destroy(self.canvas)
                self.buttons.pop(self.enemies[i])
                self.enemies.pop(i)
                return

    def create_money(self, money):
        """
        Creates the score image and value.
        """
        self.money = money
        self.money_tag = self.canvas.create_text(
            70, 30,
            text=f"Score: {money}",
            font=("Arial", 20),
            fill="yellow"
        )
        self.money_counter = 0
        self.money_tag_new = -1

    def add_money(self):
        """
        Adds to the score value and creates its tag.
        """
        if self.money_tag_new != -1:
            self.canvas.delete(self.money_tag_new)

        new_money = int(20 * self.scale_factor)
        self.money += new_money
        self.update_money()
        self.money_counter = 15
        self.money_tag_new = self.canvas.create_text(
            250, 30,
            text=f"+ {new_money}",
            font=("Arial", 20),
            fill="yellow"
        )

    def update_money(self):
        """
        Visually updates the money value
        """
        self.canvas.itemconfig(
            self.money_tag,
            text=f"Score: {self.money}"
        )


# Test purposes only
if __name__ == "__main__":
    from startcanvas import StartCanvas
    root = Tk()
    startcanvas = StartCanvas(root, 1920, 1080)
    startcanvas.load_game()
    # startcanvas.play_new()
