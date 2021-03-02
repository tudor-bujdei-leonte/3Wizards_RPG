from constants import *
from canvasbutton import CanvasButton
from canvasmenu import CanvasMenu


class LeaderboardCanvas():
    """
    The canvas that displays the leaderboard
    """

    def __init__(self, parent, width, height):
        self.parent = parent
        self.root = parent.root

        self.canvas = Canvas(
            self.root,
            width=width,
            height=height,
            bg="black",
            bd=0,
            highlightthickness=0
        )
        self.canvas.pack()
        self.canvas.focus_set()

        self.background_image = PhotoImage(
            file=f"{objects_folder}/start canvas/wood board background.gif"
        )
        self.canvas.create_image(
            0, 0,
            image=self.background_image,
            anchor="nw"
        )

        self.keep_looping = True

        self.create_buttons()
        self.display_leaderboard()

    def loop(self):
        """
        Continuously updates the screen. This is only needed for the intro
        animation.
        """
        if perf_counter() - self.tick > 0.005:
            for i in range(5):
                if self.board[i].x > 960:
                    self.board[i].move(x=-25)
            self.tick = perf_counter()

        self.root.update()

    def display_leaderboard(self):
        """
        Creates the leaderboard images
        """
        self.load_scores()
        self.board = []
        for i in range(5):
            self.board.append(CanvasMenu(
                self.canvas,
                text=self.scores[i], text_style="leftright",
                font=("Arial Bold", 70),
                x=2000 + 200 * i, y=150 + i * 170
            ))

    def load_scores(self):
        """
        Loads and sorts scores from the file and appends N/A if there are not
        enough to display
        """
        with open("leaderboard.txt") as file:
            lines = file.readlines()
            self.scores = [line.split("|") for line in lines]
        for i in range(len(self.scores)):
            self.scores[i][1] = int(self.scores[i][1].strip())
        for i in range(len(self.scores)):
            for j in range(i + 1, len(self.scores)):
                if self.scores[i][1] < self.scores[j][1]:
                    aux = self.scores[i]
                    self.scores[i] = self.scores[j]
                    self.scores[j] = aux
        for i in range(10):
            self.scores.append(["N/A", 0])

    def create_buttons(self):
        """
        Creates the return button
        """
        self.return_button = CanvasButton(
            self.canvas,
            event=lambda self=self: self.destroy(),
            text="Return",
            font=("Arial Bold", 50),
            x=225, y=1000,
            scale_factor=2
        )

    def destroy(self):
        """
        Stops running itself
        """
        self.keep_looping = False

    def start(self):
        """
        Starts running itself
        """
        self.tick = perf_counter()
        while self.keep_looping:
            self.loop()
