from constants import *
from ally import Ally
from enemy import Enemy


class CanvasButton():
    """
    Creates a button-like object inside the canvas
    """

    def __init__(
            self, canvas,
            event=lambda x: print(0),
            text="", font=("Arial Bold", 20),
            x=0, y=0,
            scale_factor=1):
        """
        Initialises the button as an image-text overlapping pair with
        associated bindings. The image will change to appear 'pressed'
        on click, along with the passed event.
        """
        self.canvas = canvas
        self.event = event

        # loads the background images on click and idle
        self.load_images(scale_factor)

        # places the items on canvas
        self.text = canvas.create_text(
            x - int(len(text) / 2), y - 10,
            text=text,
            font=font,
            fill="#633506"
        )
        self.background = canvas.create_image(
            x - int(len(text)/2), y - 10,
            image=self.background_image
        )

        # sets the bindings to the event to both text and background so it
        # feels like a button
        self.canvas.tag_bind(
            self.background,
            "<Button-1>",
            event
        )
        self.canvas.tag_bind(
            self.text,
            "<Button-1>",
            event
        )
        # raises the text above the button image
        self.canvas.tag_raise(self.text, self.background)

        # secondary bind so it changes image on click
        self.canvas.tag_bind(
            self.background,
            "<Button-1>",
            lambda x, self=self: self.clicked()
        )
        self.canvas.tag_bind(
            self.text,
            "<Button-1>",
            lambda x, self=self: self.clicked()
        )

        # coordinates of the center (for accessibility)
        self.x = x
        self.y = y

    def load_images(self, scale_factor):
        """
        Loads the images for normal state and clicked state.
        """
        self.background_image = PhotoImage(
            file=f"{objects_folder}/simple/buttons/button_default.gif"
        ).zoom(scale_factor, scale_factor)
        self.background_image_onclick = PhotoImage(
            file=f"{objects_folder}/simple/buttons/button_clicked.gif"
        ).zoom(scale_factor, scale_factor)

    def clicked(self):
        """
        Changes the image when clicked
        """
        self.event()
        self.canvas.itemconfig(
            self.background,
            image=self.background_image_onclick
        )

        # reverts after 0.1s
        self.canvas.after(100, lambda self=self: self.unclicked())

    def unclicked(self):
        """
        Reverts clicked image to normal image
        """
        self.canvas.itemconfig(
            self.background,
            image=self.background_image
        )

    def hide(self):
        """
        Hides the button
        """
        self.canvas.itemconfig(
            self.text,
            state="hidden"
        )
        self.canvas.itemconfig(
            self.background,
            state="hidden"
        )

    def show(self):
        """
        Unhides the button
        """
        self.canvas.itemconfig(
            self.text,
            state="normal"
        )
        self.canvas.itemconfig(
            self.background,
            state="normal"
        )

    def destroy(self, canvas):
        """
        Deletes the button from canvas
        """
        canvas.delete(self.text)
        canvas.delete(self.background)

    def change_text(self, canvas, new_text):
        """
        Updates the button text
        """
        canvas.itemconfig(
            self.text,
            text=new_text
        )

    def tag_raise(self, background):
        """
        Raises the button over certain menu backgrounds
        """
        self.canvas.tag_raise(
            self.background, background
        )
        self.canvas.tag_raise(
            self.text, self.background
        )
