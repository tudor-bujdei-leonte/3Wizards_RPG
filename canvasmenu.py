from constants import *
from canvasbutton import CanvasButton


class CanvasMenu():
    """
    A canvas menu item with several possible configurations. Used for
    confirmation screens, notices, empty menus and the leaderboard.
    """

    def __init__(self, canvas,
                 text="", text_style="normal", font=("Arial Bold", 50),
                 x=0, y=0, event=lambda x: print(0)):
        """
        Initialises the menu with different attributes depending on
        text_style
        """
        self.canvas = canvas
        self.text_style = text_style

        if text_style == "leftright":
            # used for leaderboard logs
            self.text = canvas.create_text(
                x - int(len(text) / 2), y - 10,
                text=text,
                font=font,
                fill="#633506"
            )
            self.background_image = PhotoImage(
                file=f"{objects_folder}/simple/buttons/tile_beige.gif"
            )
            self.background = canvas.create_image(
                x - int(len(text)/2), y - 10,
                image=self.background_image
            )
        elif text_style == "yesno":
            # used for yes/no confirmation messages
            x = 1920 / 2
            y = 1080 / 2
            self.text = canvas.create_text(
                x - int(len(text) / 2), y - 80,
                text=text,
                font=font,
                fill="#633506"
            )
            self.buttons = []
            self.buttons.append(CanvasButton(
                canvas,
                event=event[0],
                text="Yes", font=("Arial Bold", 50),
                x=x - 175, y=y + 50,
                scale_factor=2
            ))
            self.buttons.append(CanvasButton(
                canvas,
                event=event[1],
                text="No", font=("Arial Bold", 50),
                x=x + 175, y=y + 50,
                scale_factor=2
            ))
            self.background_image = PhotoImage(
                file=f"{objects_folder}/simple/buttons/panel_beige.gif"
            ).subsample(1, 2)
            self.background = canvas.create_image(
                x - int(len(text) / 2), y - 10,
                image=self.background_image
            )
            CanvasButton.tag_raise(self.buttons[0], self.background)
            CanvasButton.tag_raise(self.buttons[1], self.background)
        elif text_style == "ok":
            # used for notice popups
            x = 1920 / 2
            y = 1080 / 2
            self.text = canvas.create_text(
                x - int(len(text) / 2), y - 80,
                text=text,
                font=font,
                fill="#633506"
            )
            self.background_image = PhotoImage(
                file=f"{objects_folder}/simple/buttons/panel_beige.gif"
            ).subsample(1, 2)
            self.background = canvas.create_image(
                x - int(len(text) / 2), y - 10,
                image=self.background_image
            )
            self.button = CanvasButton(
                canvas,
                event=event,
                text="Ok", font=("Arial Bold", 50),
                x=x, y=y + 50,
                scale_factor=2
            )
        else:
            # empty menu
            self.text = -1
            self.background_image = PhotoImage(
                file=f"{objects_folder}/simple/buttons/panel_beige.gif"
            )
            self.background = canvas.create_image(
                x, y,
                image=self.background_image
            )
        self.canvas.tag_raise(self.text, self.background)

        # center coordinates for easy access
        self.x = x
        self.y = y

    def move(self, x=0, y=0):
        # moves "leftright" type menus
        self.canvas.move(self.text, x, y)
        self.canvas.move(self.background, x, y)
        self.x += x
        self.y += y

    def destroy(self):
        # removes itself from the canvas
        if self.text_style == "yesno":
            self.buttons[0].destroy(self.canvas)
            self.buttons[1].destroy(self.canvas)
        elif self.text_style == "ok":
            self.button.destroy(self.canvas)
        self.canvas.delete(self.background)
        if self.text != -1:
            self.canvas.delete(self.text)
