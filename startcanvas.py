from constants import *
from canvasbutton import CanvasButton
from gamecanvas import GameCanvas
from leaderboard_canvas import LeaderboardCanvas
from canvasmenu import CanvasMenu


class StartCanvas():
    """
    The main page canvas object
    """
    button_text = ["Play", "Load game", "Leaderboard", "User"]

    def __init__(self, root, width, height):
        self.root = root
        self.configure_root()

        self.canvas = Canvas(
            root,
            width=width,
            height=height,
            bg="black",
            bd=0,
            highlightthickness=0
        )
        self.canvas.pack()
        self.canvas.focus_set()

        self.background_image = PhotoImage(
            file=f"{objects_folder}/start canvas/start board.gif"
        )
        self.canvas.create_image(
            0, 0,
            image=self.background_image,
            anchor="nw"
        )

        self.create_boss_canvas(width, height)
        self.active_canvas = self.canvas

        self.create_buttons()
        self.areyousure = -1

        self.user = self.get_username()

    def get_username(self):
        """
        Gets the saved username
        """
        with open("username.txt") as file:
            return file.read().strip()

    def create_boss_canvas(self, width, height):
        """
        Creates the boss key functionality
        """
        # it will be a canvas pasted on the screen
        self.boss_canvas = Canvas(
            self.root,
            width=width,
            height=height,
            bg="black",
            bd=0,
            highlightthickness=0
        )
        # it only contains the boss image
        self.boss_image = PhotoImage(
            file=f"{objects_folder}/start canvas/boss.gif"
        )
        self.boss_canvas.create_image(
            int(width / 2), int(height / 2),
            image=self.boss_image
        )
        self.boss = False

    def configure_root(self):
        """
        Configures the root
        """
        # makes it fullscreen, works on any os
        self.root.attributes("-fullscreen", True)

        # I do not have access to a mac so I decided against this
        # root.state("withdrawn")
        # if "Win" in platform():
        #     root.state("zoomed")
        # elif "Linux" in platform():
        #     root.state("normal")

        self.root.config(bg="black")

        self.root.bind(
            "<b>",
            self.toggle_boss
        )

    def toggle_boss(self, event):
        """
        Switches the active canvas to the boss canvas and vice versa
        """
        if not self.boss:
            self.active_canvas.pack_forget()
            self.boss_canvas.pack()
        else:
            self.boss_canvas.pack_forget()
            self.active_canvas.pack()
        self.boss = not self.boss

    def start(self):
        """
        Refreshes the page.
        Would be needed if I decide to implement any animations.
        """
        while True:
            self.root.update()

    def create_buttons(self):
        """
        Creates the menu.
        """
        self.menubuttons = {}

        self.menubuttons["Play"] = CanvasButton(
            self.canvas,
            event=lambda self=self: self.play_new(),
            text="Play",
            font=("Arial Bold", 70),
            x=300, y=150,
            scale_factor=3
        )

        self.menubuttons["Load Game"] = CanvasButton(
            self.canvas,
            event=lambda self=self: self.areyousure_menu(event=self.load_game),
            text="Load Game",
            font=("Arial Bold", 50),
            x=300, y=350,
            scale_factor=3
        )

        self.menubuttons["Leaderboard"] = CanvasButton(
            self.canvas,
            event=lambda self=self: self.load_leaderboard(),
            text="Leaderboard",
            font=("Arial Bold", 50),
            x=300, y=550,
            scale_factor=3
        )

        self.menubuttons["User"] = CanvasButton(
            self.canvas,
            event=lambda self=self: self.login(),
            text="User",
            font=("Arial Bold", 70),
            x=300, y=750,
            scale_factor=3
        )

        self.menubuttons["Exit"] = CanvasButton(
            self.canvas,
            event=lambda self=self: self.areyousure_menu(
                event=self.root.destroy),
            text="Exit",
            font=("Arial Bold", 70),
            x=300, y=950,
            scale_factor=3
        )

    def areyousure_menu(self, message="", event=lambda x: print(0)):
        """
        Makes a yes/no popup for confirmation
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
        Cancels the action
        """
        self.areyousure.destroy()
        self.areyousure = -1

    def load_leaderboard(self):
        """
        Switches to the leaderboard canvas
        """
        if self.areyousure != -1:
            return

        self.canvas.pack_forget()

        leaderboard_canvas = LeaderboardCanvas(self, 1920, 1080)
        self.active_canvas = leaderboard_canvas.canvas
        leaderboard_canvas.start()

        leaderboard_canvas.canvas.pack_forget()
        del leaderboard_canvas
        self.active_canvas = self.canvas

        self.canvas.pack()
        self.root.lift(self.canvas)
        self.canvas.focus_set()

    def play_new(self):
        """
        Starts a new game
        """
        if self.areyousure != -1:
            return

        self.canvas.pack_forget()

        gamecanvas = GameCanvas(self, 1920, 1080, user=self.user)
        self.active_canvas = gamecanvas.canvas
        gamecanvas.start_game()

        gamecanvas.canvas.pack_forget()
        del gamecanvas
        self.active_canvas = self.canvas

        self.canvas.pack()
        self.root.lift(self.canvas)
        self.canvas.focus_set()

    def load_game(self):
        """
        Loads the saved file
        """
        self.areyousure.destroy()
        self.areyousure = -1
        self.canvas.pack_forget()

        gamecanvas = GameCanvas(self, 1920, 1080, user=self.user)
        self.active_canvas = gamecanvas.canvas
        gamecanvas.load_game()
        gamecanvas.start_game(loaded=True)

        gamecanvas.canvas.pack_forget()
        del gamecanvas
        self.active_canvas = self.canvas

        self.canvas.pack()
        self.root.lift(self.canvas)
        self.canvas.focus_set()

    def login(self):
        """
        Changes the username
        """
        if self.areyousure != -1:
            return

        self.login_menu = CanvasMenu(self.canvas, x=1920 / 2, y=1080 / 2)
        self.areyousure = 0
        self.login_text = self.canvas.create_text(
            1920 / 2, 1080 / 2 - 130,
            text=" Enter the\nusername:",
            font=("Arial Bold", 70),
            fill="#633506"
        )
        self.username_box = [Entry(
            self.canvas,
            font=("Arial Bold", 70),
            width=10,
            fg="white",
            background="#633506"
        )]
        self.username_box[0].insert(0, self.user)
        self.username_box.append(self.canvas.create_window(
            1920 / 2, 1080 / 2 + 70, window=self.username_box[0]
        ))
        self.save_button = CanvasButton(
            self.canvas,
            event=lambda self=self: self.areyousure_login(),
            text="Ok", font=("Arial Bold", 50),
            x=1920 / 2, y=1080 / 2 + 230,
            scale_factor=2
        )

    def areyousure_login(self):
        """
        Confirmation prompt for name change
        """
        temp_name = self.username_box[0].get()

        self.login_menu.destroy()
        self.canvas.delete(self.login_text)
        self.canvas.delete(self.username_box[1])
        self.save_button.destroy(self.canvas)
        self.areyousure = -1

        self.areyousure_menu(
            event=lambda self=self: self.save_login(temp_name))

    def save_login(self, new_name="Guest"):
        """
        Name change method
        """
        self.areyousure.destroy()
        self.areyousure = -1

        self.user = new_name

        with open("username.txt", "w") as file:
            file.write(new_name)
